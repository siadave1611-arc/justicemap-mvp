# JusticeMap MVP — System Architecture

> **Version:** 1.0 (MVP)  
> **Last Updated:** February 2026

---

## Overview

JusticeMap is a tenant rights lookup tool for LA County. Users enter an address → system returns applicable eviction protections and resources for their jurisdiction.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   USER      │────▶│  GEOCODER   │────▶│ JURISDICTION│────▶│   RIGHTS    │
│   ADDRESS   │     │  (Nominatim)│     │   MATCHER   │     │   LOOKUP    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                          │                    │                    │
                          ▼                    ▼                    ▼
                    lat/lon coords      point-in-polygon      jurisdictions.json
```

---

## Components

### 1. Data Layer (`/data`)

| File | Purpose |
|------|---------|
| `address_data.json` | Verified tenant rights by jurisdiction (LA City, County, Pasadena, etc.) |
| `eviction_stats.csv` | Historical eviction data for pressure score calculation |
| `la_boundaries.geojson` | LA County city boundary polygons for point-in-polygon matching |
| `zip_data_20.json` | ZIP-level risk signals, resources, and pressure scores |

**Data integrity:** See [`data_sources.md`](./data_sources.md) for verification status of each claim.

### 2. Backend (`/src/backend`)

| Module | Responsibility |
|--------|----------------|
| `api.py` | REST API endpoints for frontend consumption |
| `geocode_rules.py` | Main orchestrator: address → coords → jurisdiction → rights |
| `pressure_score.py` | Calculates normalized risk score (0–100) from rent burden, poverty, unemployment |

**Core functions in `geocode_rules.py`:**
| Function | Purpose |
|----------|---------|
| `geocode()` | Nominatim API (free, 1 req/sec rate limit) |
| `find_jurisdiction()` | Shapely point-in-polygon against `la_boundaries.geojson` |
| `get_rights()` | Lookup from `address_data.json` by jurisdiction ID |

### 3. Frontend (`/src/frontend`)

| File | Purpose |
|------|---------|
| `App.js` | React app entry point |
| `MapView.js` | Interactive map visualization of jurisdictions/risk |
| `components/` | Reusable UI components (search bar, rights cards, etc.) |

### 4. Utilities (`/src/utils`)

| File | Purpose |
|------|---------|
| `constants.py` | Shared configuration, API URLs, jurisdiction IDs |

### 5. Streamlit Prototype (`/streamlit`)

| File | Purpose |
|------|---------|
| `app.py` | Rapid prototype UI for address lookup (demo/testing) |

---

## Data Flow

```
1. User enters: "123 Main St, Los Angeles, CA 90012"
                          │
                          ▼
2. geocode() ───────────▶ Nominatim API
                          │
                          ▼
              Returns: (34.0522, -118.2437)
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
3a. find_jurisdiction()        3b. get_pressure_score()
    Point-in-polygon vs            Lookup zip in
    la_boundaries.geojson          zip_data_20.json
              │                       │
              ▼                       ▼
    { id: "la_city" }          { score: 72, factors: {...} }
              │                       │
              └───────────┬───────────┘
                          ▼
4. get_rights() ─────────▶ Lookup in address_data.json
                          │
                          ▼
              Returns: { rent_control: {...}, key_rights: [...], 
                         resources: [...], pressure_score: 72 }
                          │
                          ▼
5. api.py ───────────────▶ REST response to frontend
                          │
                          ▼
6. MapView.js ───────────▶ Renders interactive map + rights card
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Geocoding API | Nominatim (free) | No API key needed; sufficient for MVP |
| Boundary matching | Shapely point-in-polygon | Accurate to city boundaries (not zip codes) |
| Data format | JSON + CSV | JSON for structured rights; CSV for stats/analytics |
| Backend API | Python REST (`api.py`) | Clean separation from frontend |
| Frontend | React + Streamlit | React for production; Streamlit for rapid prototyping |
| Pressure Score | Weighted index (0–100) | Combines rent burden, poverty, unemployment |
| Hardcoded $ amounts | ❌ Avoided | Change annually; point to official bulletins instead |

---

## Jurisdictions Covered (v1.0)

| ID | Name | Legal Regime |
|----|------|--------------|
| `la_city` | City of Los Angeles | RSO + JCO |
| `la_county_unincorporated` | LA County Unincorporated | RSTPO |
| `long_beach` | City of Long Beach | AB 1482 + Local |
| `glendale` | City of Glendale | AB 1482 + Rental Rights Program |
| `pasadena` | City of Pasadena | Measure H |
| `statewide_ab1482` | California (fallback) | AB 1482 |

---

## Future Architecture (v2.0)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  ALLOWED SITES  │────▶│  LEGAL MONITOR   │────▶│  DIFF ENGINE    │
│  (allowlist)    │     │  AGENT           │     │  (detect changes)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                              ┌────────────────────────────┘
                              ▼
                   ┌─────────────────────┐     ┌─────────────────┐
                   │  HUMAN REVIEW QUEUE │────▶│  jurisdictions  │
                   │  (pending_updates)  │     │  .json UPDATE   │
                   └─────────────────────┘     └─────────────────┘
```

**Planned components:**
- `src/agents/legal_monitor.py` — scheduled scraper (allowlist-only)
- `src/agents/diff_detector.py` — flags changes vs current data
- `src/agents/llm_extractor.py` — Claude API to parse bulletins → structured JSON
- `data/pending_updates.json` — human review queue

---

## File Structure

```
justicemap-mvp/
├── data/
│   ├── address_data.json       # Verified jurisdiction rights data
│   ├── eviction_stats.csv      # Eviction statistics by area
│   ├── la_boundaries.geojson   # City boundary polygons (GIS)
│   └── zip_data_20.json        # ZIP-level risk signals & resources
├── docs/
│   ├── architecture.md         # This file
│   ├── data_sources.md         # Data source citations
│   └── notes.md                # Design decisions & roadmap
├── src/
│   ├── backend/
│   │   ├── api.py              # REST API endpoints
│   │   ├── geocode_rules.py    # Address → jurisdiction → rights
│   │   └── pressure_score.py   # Risk/pressure score calculation
│   ├── frontend/
│   │   ├── App.js              # React app entry point
│   │   ├── MapView.js          # Interactive map component
│   │   └── components/         # Reusable UI components
│   └── utils/
│       └── constants.py        # Shared constants & config
├── streamlit/
│   └── app.py                  # Streamlit prototype UI
├── tests/
│   └── test_geocode.py         # Backend test suite
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Constraints & Limitations

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| Nominatim rate limit (1 req/sec) | Slow for bulk lookups | Cache results; batch processing for analytics |
| GeoJSON accuracy | Depends on source quality | Use official LA County GIS data |
| Legal data freshness | Changes annually | Point to bulletins; future: monitoring agent |
| Not legal advice | Liability risk | Prominent disclaimers; link to official sources |

---

## References

- [LAHD Official](https://housing.lacity.gov)
- [DCBA Rent Stabilization](https://dcba.lacounty.gov/rentstabilizationprogram/)
- [CA Attorney General Housing](https://oag.ca.gov/housing)
- [Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/)
- [Shapely Documentation](https://shapely.readthedocs.io/)
- [LA County GIS Data](https://egis-lacounty.hub.arcgis.com/)
