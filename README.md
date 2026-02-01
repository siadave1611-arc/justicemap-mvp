## Data Integrity: Verified vs Variable Fields

This project distinguishes between **verified claims** (confirmed via official sources) and **variable items** (that change on jurisdiction schedules and must be re-checked at runtime).

### ✅ Verified Claims

| Claim | Source |
|-------|--------|
| LA City RSO 3% rent cap | [housing.lacity.gov/renter-protections-2](https://housing.lacity.gov/renter-protections-2) |
| LA City utility adder eliminated Feb 2, 2026 | [housing.lacity.gov/rso-rent-increase-calculator](https://housing.lacity.gov/rso-rent-increase-calculator) |
| LA City JCO 3-day filing requirement | [housing.lacity.gov/.../just-cause-for-eviction-ordinance-jco](https://housing.lacity.gov/residents/just-cause-for-eviction-ordinance-jco) |
| Pasadena 2.25% rent cap (Oct 2025–Sep 2026) | [cityofpasadena.net/rent-stabilization/rent-control-overview](https://www.cityofpasadena.net/rent-stabilization/rent-control-overview/) |
| Glendale 7% rent increase triggers relocation | [glendalerentalrights.com/guides-1](https://www.glendalerentalrights.com/guides-1) |

### ⚠️ Variable / Must Re-Check

These values change on jurisdiction-specific schedules (typically annually on July 1 or Oct 1):

- **Relocation assistance dollar amounts** — updated annually by LAHD/DCBA
- **LA County RSTPO exact percentage** — verify via [DCBA rent increase bulletin](https://dcba.lacounty.gov/rentstabilizationprogram/)
- **AB 1482 statewide cap** — varies by region/year; use [calculator](https://tenantprotections.org/calculator)
- **Registration fees** — check each city's fee schedule

### Methodology

Jurisdictions are summarized from official program pages. This dataset is designed for educational lookup tools, not legal advice. Users should always verify current values via linked official sources before relying on any specific claim.

> 📄 See [`docs/SOURCES.md`](docs/SOURCES.md) for complete source documentation.
