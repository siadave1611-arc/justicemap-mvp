"""
LA County Eviction Rights - Geocoding & Jurisdiction Lookup
Nominatim (free) + point-in-polygon matching
"""
import json
import requests
import time
from pathlib import Path
from shapely.geometry import Point, shape
from functools import lru_cache

# === CONFIG ===
DATA_DIR = Path(__file__).parent.parent.parent / "data"
BOUNDARIES_FILE = DATA_DIR / "la_boundaries.geojson"
RIGHTS_FILE = DATA_DIR / "jurisdiction_rights.json"  # You'll create this
ZIP_DATA_FILE = DATA_DIR / "zip_data.json"  # Your existing file

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "JusticeMapMVP/1.0 (LA-tenant-rights-project)"
REQUEST_DELAY = 1.0  # Nominatim requires 1 req/sec max

_last_req = 0


# === DATA LOADERS (cached) ===
@lru_cache(maxsize=1)
def load_boundaries():
    """Load GeoJSON jurisdiction boundaries."""
    if not BOUNDARIES_FILE.exists():
        return []
    with open(BOUNDARIES_FILE) as f:
        data = json.load(f)
    
    jurisdictions = []
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        # Handle common GeoJSON property names
        jid = (props.get("jurisdiction_id") or 
               props.get("CITY", "").lower().replace(" ", "_") or
               props.get("NAME", "").lower().replace(" ", "_"))
        name = props.get("name") or props.get("CITY") or props.get("NAME") or "Unknown"
        
        try:
            geom = shape(feat["geometry"])
            jurisdictions.append({"id": jid, "name": name, "geometry": geom})
        except Exception:
            continue
    return jurisdictions


@lru_cache(maxsize=1)
def load_rights():
    """Load jurisdiction rights data."""
    if RIGHTS_FILE.exists():
        with open(RIGHTS_FILE) as f:
            return json.load(f)
    return {}


@lru_cache(maxsize=1)
def load_zip_data():
    """Load existing zip_data.json for fallback."""
    if ZIP_DATA_FILE.exists():
        with open(ZIP_DATA_FILE) as f:
            return json.load(f)
    return {}


# === GEOCODING ===
def geocode(address: str) -> dict | None:
    """Convert address to lat/lon via Nominatim."""
    global _last_req
    
    # Rate limit
    wait = REQUEST_DELAY - (time.time() - _last_req)
    if wait > 0:
        time.sleep(wait)
    
    params = {
        "q": f"{address}, Los Angeles County, California, USA",
        "format": "json",
        "limit": 1,
        "countrycodes": "us"
    }
    
    try:
        r = requests.get(NOMINATIM_URL, params=params, 
                        headers={"User-Agent": USER_AGENT}, timeout=10)
        _last_req = time.time()
        r.raise_for_status()
        results = r.json()
        
        if results:
            return {
                "lat": float(results[0]["lat"]),
                "lon": float(results[0]["lon"]),
                "display": results[0].get("display_name", "")
            }
    except Exception as e:
        print(f"[Geocode Error] {e}")
    return None


# === JURISDICTION LOOKUP ===
def find_jurisdiction(lat: float, lon: float) -> dict | None:
    """Point-in-polygon check against boundaries."""
    pt = Point(lon, lat)  # shapely uses (x=lon, y=lat)
    
    for j in load_boundaries():
        if j["geometry"].contains(pt):
            return {"id": j["id"], "name": j["name"]}
    return None


def get_jurisdiction_rights(jid: str) -> dict:
    """Get rights info for a jurisdiction ID."""
    rights = load_rights()
    
    # Default rights data structure
    defaults = {
        "la_city": {
            "name": "City of Los Angeles",
            "rent_control": True,
            "just_cause": True,
            "key_rights": [
                "Rent Stabilization Ordinance (RSO) covers buildings built before 10/1/1978",
                "Just-cause eviction required for RSO units",
                "Annual rent increases capped (typically 3-8%)",
                "Relocation assistance required for no-fault evictions"
            ],
            "notice_requirements": "60-day notice for tenancies >1 year, 30-day for <1 year",
            "resources": [
                {"name": "LA Housing Department", "url": "https://housing.lacity.org", "phone": "866-557-7368"},
                {"name": "Stay Housed LA", "url": "https://stayhousedla.org"}
            ]
        },
        "santa_monica": {
            "name": "City of Santa Monica",
            "rent_control": True,
            "just_cause": True,
            "key_rights": [
                "Strong rent control - covers most rentals",
                "Just-cause eviction required",
                "Strict limits on rent increases"
            ],
            "notice_requirements": "60-day notice required",
            "resources": [
                {"name": "Santa Monica Rent Control", "url": "https://www.smgov.net/rentcontrol", "phone": "310-458-8751"}
            ]
        },
        "unincorporated": {
            "name": "Unincorporated LA County",
            "rent_control": True,
            "just_cause": True,
            "key_rights": [
                "LA County Rent Stabilization Ordinance (2020)",
                "Covers unincorporated areas",
                "Just-cause eviction protections",
                "3% annual rent cap + CPI"
            ],
            "notice_requirements": "60-day notice for tenancies >1 year",
            "resources": [
                {"name": "LA County DCBA", "url": "https://dcba.lacounty.gov/rentstabilization", "phone": "833-223-7368"}
            ]
        }
    }
    
    # Merge loaded rights with defaults
    if jid in rights:
        return rights[jid]
    if jid in defaults:
        return defaults[jid]
    
    # Unknown jurisdiction - return CA state minimums
    return {
        "name": "Unknown Jurisdiction",
        "rent_control": False,
        "just_cause": True,
        "key_rights": [
            "California Tenant Protection Act (AB 1482) may apply",
            "Just-cause eviction for tenancies >12 months",
            "Rent cap: 5% + local CPI (max 10%) annually"
        ],
        "notice_requirements": "60-day notice for tenancies >1 year, 30-day for <1 year",
        "resources": [
            {"name": "CA Dept of Consumer Affairs", "url": "https://www.courts.ca.gov/selfhelp-housing.htm"}
        ],
        "warning": "Could not determine exact jurisdiction - showing CA state minimums"
    }


# === MAIN LOOKUP FUNCTION ===
def lookup_address(address: str) -> dict:
    """
    Main entry: address -> coordinates -> jurisdiction -> rights
    Returns complete JSON response for frontend.
    """
    result = {
        "success": False,
        "input": address,
        "coordinates": None,
        "jurisdiction": None,
        "rights": None,
        "error": None
    }
    
    # Step 1: Geocode
    coords = geocode(address)
    if not coords:
        result["error"] = "Could not geocode address. Please check spelling and try again."
        return result
    
    result["coordinates"] = {"lat": coords["lat"], "lon": coords["lon"]}
    result["resolved_address"] = coords["display"]
    
    # Step 2: Find jurisdiction
    jurisdiction = find_jurisdiction(coords["lat"], coords["lon"])
    
    if jurisdiction:
        result["jurisdiction"] = jurisdiction
        jid = jurisdiction["id"]
    else:
        # Fallback: try to infer from address
        result["jurisdiction"] = {"id": "unknown", "name": "Unknown (CA state rules apply)"}
        jid = "unknown"
    
    # Step 3: Get rights
    result["rights"] = get_jurisdiction_rights(jid)
    result["success"] = True
    
    return result


# === CLI USAGE ===
if __name__ == "__main__":
    import sys
    addr = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "123 Main St, Los Angeles, CA 90012"
    
    print(f"\n🔍 Looking up: {addr}\n")
    res = lookup_address(addr)
    print(json.dumps(res, indent=2))
