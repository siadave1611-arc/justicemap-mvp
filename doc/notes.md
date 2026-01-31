# LA Eviction Rights Map - Development Log

## Day 1 Complete (Feb 1, 2026)

### Decisions Made
- Address > ZIP for jurisdiction precision (zips cross city boundaries)
- Jurisdiction-centric data model (la_city, unincorporated_la, long_beach)
- Point-in-polygon geocoding vs LA County GeoJSON boundaries

### Data Architecture
Coverage: 82% LA County population (top 5 jurisdictions)

### Data Sources
- LAHD: Eviction notices (14,585 in 90028 alone, 2023-25)
- StayHousedLA: Priority ZIPs (90011, 90037, 90044)
- DCBA: RSTPO unincorporated protections
- LA County GIS: 88 cities + unincorporated boundaries

### Day 2 Plan
Backend: `src/backend/geocode_rules.py`

### Issues/Blockers
- None
