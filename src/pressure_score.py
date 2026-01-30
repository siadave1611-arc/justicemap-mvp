import json

# Simple normalized weighted score (0–100)
WEIGHTS = {
    "rent_burden_pct": 0.5,
    "poverty_pct": 0.3,
    "unemployment_pct": 0.2
}

def minmax(values):
    mn, mx = min(values), max(values)
    if mx == mn:
        return [0.5 for _ in values]  # avoid divide-by-zero; neutral
    return [(v - mn) / (mx - mn) for v in values]

def main():
    with open("data/zip_data.json", "r") as f:
        data = json.load(f)

    # collect arrays for normalization
    rent = [d["signals"]["rent_burden_pct"] for d in data]
    pov  = [d["signals"]["poverty_pct"] for d in data]
    unemp= [d["signals"]["unemployment_pct"] for d in data]

    rent_n = minmax(rent)
    pov_n  = minmax(pov)
    unemp_n= minmax(unemp)

    for i, d in enumerate(data):
        score_0_1 = (
            WEIGHTS["rent_burden_pct"] * rent_n[i] +
            WEIGHTS["poverty_pct"] * pov_n[i] +
            WEIGHTS["unemployment_pct"] * unemp_n[i]
        )
        d["pressure_score_0_100"] = round(score_0_1 * 100)

    with open("data/zip_data_scored.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Wrote: data/zip_data_scored.json")

if __name__ == "__main__":
    main()
