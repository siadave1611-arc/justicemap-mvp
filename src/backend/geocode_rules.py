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
RIGHTS_FILE = DATA_DIR / "address_data.json"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "JusticeMapMVP/1.0 (LA-tenant-rights-project)"
REQUEST_DELAY = 1.0  # Nominatim requires 1 req/sec max

_last_req = 0

# === JURISDICTION MAPPING ===
# Maps GeoJSON CITY_COMM_NAME -> address_data.json keys
JURISDICTION_MAP = {
    "LOS ANGELES": "los_angeles_city",
    "LONG BEACH": "long_beach",
    "GLENDALE": "glendale",
    "PASADENA": "pasadena",
    "SANTA MONICA": "santa_monica",
    "WEST HOLLYWOOD": "west_hollywood",
    "BEVERLY HILLS": "beverly_hills",
    "CULVER CITY": "culver_city",
    "INGLEWOOD": "inglewood",
}

def map_jurisdiction(city_comm_name: str, jurisdiction_type: str) -> str:
    """Map GeoJSON names to address_data.json keys."""
    name_upper = city_comm_name.upper().strip()
    
    # Check explicit mapping first
    if name_upper in JURISDICTION_MAP:
        return JURISDICTION_MAP[name_upper]
    
    # Unincorporated areas -> LA County rules
    if jurisdiction_type == "UNINCORPORATED AREA":
        return "la_county"
    
    # Other incorporated cities -> CA statewide rules
    return "california_statewide"


# === DATA LOADERS (cached) ===
@lru_cache(maxsize=1)
def load_boundaries():
    """Load GeoJSON jurisdiction boundaries."""
    if not BOUNDARIES_FILE.exists():
        print(f"[Warning] Boundaries file not found: {BOUNDARIES_FILE}")
        return []
    
    with open(BOUNDARIES_FILE) as f:
        data = json.load(f)
    
    jurisdictions = []
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        
        # Use actual field names from LA County GeoJSON
        city_comm_name = props.get("CITY_COMM_NAME", "Unknown")
        jurisdiction_type = props.get("JURISDICTION", "")
        
        # Map to our jurisdiction keys
        jid = map_jurisdiction(city_comm_name, jurisdiction_type)
        
        try:
            geom = shape(feat["geometry"])
            jurisdictions.append({
                "id": jid,
                "name": city_comm_name.title(),  # "LOS ANGELES" -> "Los Angeles"
                "type": jurisdiction_type,
                "geometry": geom
            })
        except Exception as e:
            print(f"[Warning] Could not parse geometry for {city_comm_name}: {e}")
            continue
    
    print(f"[Info] Loaded {len(jurisdictions)} jurisdiction boundaries")
    return jurisdictions


@lru_cache(maxsize=1)
def load_rights():
    """Load jurisdiction rights data from address_data.json."""
    if RIGHTS_FILE.exists():
        with open(RIGHTS_FILE) as f:
            return json.load(f)
    print(f"[Warning] Rights file not found: {RIGHTS_FILE}")
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
            return {
                "id": j["id"],
                "name": j["name"],
                "type": j["type"]
            }
    return None


def get_jurisdiction_rights(jid: str) -> dict:
    """Get rights info for a jurisdiction ID."""
    rights = load_rights()
    
    # Direct match
    if jid in rights:
        return rights[jid]
    
    # Fallback to statewide
    if "california_statewide" in rights:
        result = rights["california_statewide"].copy()
        result["note"] = f"Specific rules for this jurisdiction not yet verified. Showing California statewide protections."
        return result
    
    # Ultimate fallback
    return {
        "name": "California (Statewide)",
        "rent_control": False,
        "just_cause": True,
        "protections": [
            "California Tenant Protection Act (AB 1482) applies",
            "Just-cause eviction for tenancies >12 months",
            "Rent cap: 5% + local CPI (max 10%) annually"
        ],
        "notice_requirements": "60-day notice for tenancies >1 year, 30-day for <1 year",
        "resources": [
            {"name": "CA Courts Self-Help", "url": "https://www.courts.ca.gov/selfhelp-housing.htm"}
        ],
        "note": "Could not determine specific local rules. Showing CA state minimums."
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
        # Outside LA County or boundary gap
        result["jurisdiction"] = {
            "id": "california_statewide",
            "name": "Outside LA County boundaries",
            "type": "STATEWIDE"
        }
        jid = "california_statewide"
    
    # Step 3: Get rights
    result["rights"] = get_jurisdiction_rights(jid)
    result["success"] = True
    
    return result


# === CLI USAGE ===
if __name__ == "__main__":
    import sys
    
    test_addresses = [
        "1200 W 7th St, Los Angeles, CA 90017",      # LA City (Downtown)
        "411 W Ocean Blvd, Long Beach, CA 90802",    # Long Beach
        "613 E Broadway, Glendale, CA 91206",        # Glendale
        "100 N Garfield Ave, Pasadena, CA 91101",    # Pasadena
        "3250 Wilshire Blvd, Los Angeles, CA 90010", # LA City (Koreatown)
        "1000 Vin Scully Ave, Los Angeles, CA 90012",# LA City (Dodger Stadium)
        "4801 Whittier Blvd, East Los Angeles, CA",  # Unincorporated (East LA)
    ]
    
    if len(sys.argv) > 1:
        # Custom address from command line
        addr = " ".join(sys.argv[1:])
        print(f"\n🔍 Looking up: {addr}\n")
        res = lookup_address(addr)
        print(json.dumps(res, indent=2))
    else:
        # Run test suite
        print("=" * 60)
        print("JusticeMap MVP - Jurisdiction Lookup Test")
        print("=" * 60)
        
        for addr in test_addresses:
            print(f"\n📍 {addr}")
            res = lookup_address(addr)
            if res["success"]:
                j = res["jurisdiction"]
                print(f"   ✅ {j['name']} ({j['id']})")
                print(f"   📜 {res['rights'].get('name', 'Unknown')}")
            else:
                print(f"   ❌ {res['error']}")
            print("-" * 40)
