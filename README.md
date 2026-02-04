## Data Integrity: Verified vs Variable Fields

JusticeMap distinguishes between **verified claims** (confirmed via official government sources) and **variable items** (values that change on jurisdiction-specific schedules and must be re-checked at time of use).

### ✅ Verified Claims

| Claim | Source |
|-------|--------|
| LA City RSO 3% rent cap (Jul 2025–Jun 2027) | [LAHD Renter Protections](https://housing.lacity.gov/renter-protections-2) |
| LA City utility adder eliminated Feb 2, 2026 | [LAHD RSO Rent Increase Calculator](https://housing.lacity.gov/rso-rent-increase-calculator) |
| LA City JCO 3-business-day filing requirement | [LAHD Just Cause Ordinance](https://housing.lacity.gov/residents/just-cause-for-eviction-ordinance-jco) |
| Pasadena 2.25% rent cap (Oct 2025–Sep 2026) | [Pasadena Rent Stabilization Overview](https://www.cityofpasadena.net/rent-stabilization/rent-control-overview/) |
| Glendale 7% rent increase triggers relocation | [Glendale Rental Rights Guides](https://www.glendalerentalrights.com/guides-1) |

### ⚠️ Variable / Must Re-Check

The following values change on jurisdiction-specific schedules (typically annually on July 1 or October 1) and **must be verified at runtime** using official sources:

- **Relocation assistance dollar amounts** — updated annually by LAHD / DCBA
- **LA County RSTPO rent cap percentage** — verify via [DCBA Rent Stabilization Program](https://dcba.lacounty.gov/rentstabilizationprogram/)
- **AB 1482 statewide rent cap** — varies by region and year; verify using the [Tenant Protections Calculator](https://tenantprotections.org/calculator)
- **Registration fees** — confirm via individual city fee schedules

### Methodology

Jurisdiction rules are summarized from official city, county, and state program pages and municipal codes. ZIP codes are used as an accessibility-oriented proxy for regional conditions; **legal jurisdiction ultimately depends on address-level boundaries**.

This dataset is designed for educational and informational lookup tools. Users should always verify current values through linked official sources before relying on any specific claim.

> 📄 See [`docs/SOURCES.md`](docs/SOURCES.md) for complete source documentation.

> ⚠️ **Data Notice:** Eviction statistics are synthetic/demo data for MVP. 
> Real data pipeline planned for v2.0 (Census ACS + court records).
