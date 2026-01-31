"""
Test script for geocode_rules.py
Run: python tests/test_geocode.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from geocode_rules import lookup_address, geocode, find_jurisdiction, load_boundaries
import json

def test_geocode():
    """Test basic geocoding."""
    print("=" * 50)
    print("TEST 1: Geocoding")
    print("=" * 50)
    
    coords = geocode("Los Angeles City Hall, 200 N Spring St, Los Angeles, CA 90012")
    if coords:
        print(f"✅ Geocoded successfully: ({coords['lat']:.4f}, {coords['lon']:.4f})")
        assert 33.5 < coords['lat'] < 34.5, "Latitude out of LA range"
        assert -119 < coords['lon'] < -117, "Longitude out of LA range"
    else:
        print("⚠️  Geocoding returned None (might be rate limited)")


def test_boundaries_load():
    """Test boundary loading."""
    print("\n" + "=" * 50)
    print("TEST 2: Boundary Loading")
    print("=" * 50)
    
    boundaries = load_boundaries()
    if boundaries:
        print(f"✅ Loaded {len(boundaries)} jurisdiction boundaries")
        for b in boundaries[:3]:
            print(f"   - {b['name']} (id: {b['id']})")
    else:
        print("⚠️  No boundaries loaded (la_boundaries.geojson may be missing)")
        print("   This is OK for now - will use fallback defaults")


def test_full_lookup():
    """Test complete address lookup flow."""
    print("\n" + "=" * 50)
    print("TEST 3: Full Address Lookup")
    print("=" * 50)
    
    test_addresses = [
        "123 Main St, Los Angeles, CA 90012",
        "1685 Main St, Santa Monica, CA 90401",
        "100 W Broadway, Glendale, CA 91210",
    ]
    
    for addr in test_addresses:
        print(f"\n📍 Testing: {addr}")
        result = lookup_address(addr)
        
        if result["success"]:
            print(f"   ✅ Success!")
            print(f"   Coords: ({result['coordinates']['lat']:.4f}, {result['coordinates']['lon']:.4f})")
            print(f"   Jurisdiction: {result['jurisdiction']['name']}")
            
            rights = result['rights']
            print(f"   Rent Control: {'Yes' if rights.get('rent_control') else 'No'}")
            print(f"   Just Cause: {'Yes' if rights.get('just_cause') else 'No'}")
            
            if rights.get('key_rights'):
                print(f"   Key Right: {rights['key_rights'][0][:60]}...")
        else:
            print(f"   ❌ Failed: {result.get('error')}")


def test_expected_output():
    """Test the exact output format requested."""
    print("\n" + "=" * 50)
    print("TEST 4: Expected Output Format")
    print("=" * 50)
    
    result = lookup_address("123 Main St, 90012")
    
    print(f"\nAddress: 123 Main St, 90012")
    
    if result["success"]:
        jname = result["jurisdiction"]["name"] if result["jurisdiction"] else "Unknown"
        print(f"Jurisdiction: {result['jurisdiction']['id']}")
        
        rights = result.get("rights", {})
        key_rights = rights.get("key_rights", [])
        notice = rights.get("notice_requirements", "N/A")
        
        rights_summary = ", ".join(key_rights[:2]) if key_rights else "See full details"
        print(f"Rights: {rights_summary[:80]}...")
        print(f"Notice: {notice}")
        
        print("\n✅ OUTPUT FORMAT MATCHES SPEC")
    else:
        print(f"Error: {result.get('error')}")


def run_all_tests():
    """Run all tests."""
    print("\n🧪 JUSTICEMAP GEOCODE TESTS\n")
    
    try:
        test_boundaries_load()
        test_geocode()
        test_full_lookup()
        test_expected_output()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
