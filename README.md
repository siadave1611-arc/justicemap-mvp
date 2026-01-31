# LA Eviction Rights Map

**Find tenant rights by address across LA County jurisdictions**

[![Demo](demo.gif)](https://eviction-rights-map.vercel.app)

## Features

- **Address lookup** → Exact jurisdiction matching (not ZIP codes)
- **Interactive map** with city/unincorporated boundaries  
- **Legal rights** by jurisdiction (JCO, RSTPO, AB1482)
- **High-risk ZIP overlay** with pressure scores
- **Legal resources** + court venues

## How It Works

123 Main St, 90012 
↓ Nominatim geocoding 
(34.05° N, 118.24° W) 
↓ Point-in-polygon 
LA City (JCO + RSO) 
↓ Rights lookup 
“Just-cause only, 60-day notice, $9,200 relocation”


## Coverage

| Jurisdiction | Population | Key Protections | High Risk ZIPs |
|--------------|------------|-----------------|---------------|
| LA City | 3.8M | JCO + RSO | 90011, 90037 |
| Unincorporated | 1.0M | RSTPO | 91330, 90245 |
| Long Beach | 466K | Local RC | 90813, 90805 |
| Glendale | 196K | AB1482 | 91204 |

**82% LA County population covered**

## Data Sources

- [LAHD Eviction Tracker](https://housing.lacity.gov/residents/renters/eviction-notices-filed)
- [LA County DCBA](https://dcba.lacounty.gov/portfolio/eviction/)
- [StayHousedLA Priority ZIPs](https://www.stayhousedla.org/priority-zip-codes)
- [LA County GIS Boundaries](https://services3.arcgis.com/2S90r5q5n1TvMt2U/arcgis/rest/services/LA_County_Boundaries/FeatureServer/0)

## Local Development

```bash
pip install -r requirements.txt
python src/backend/test_geocode.py "123 Main St, 90012"

## Architecture

Frontend (React/Leaflet) → FastAPI → Geocode Engine → address_data.json + la_boundaries.geojson

⚠️ Disclaimer: Not legal advice. Consult attorney for case-specific guidance.
