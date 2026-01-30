# JusticeMap MVP — Eviction Access Snapshot (LA County)

JusticeMap is a prototype that explores **access-to-justice** through a simple, data-driven lens.
Given a ZIP code, the project surfaces:
- **eviction/tenant-rights resources**
- a lightweight **“Pressure Score (0–100)”** summarizing risk signals
- clear next-step guidance for residents

> **Disclaimer:** This is not legal advice. This is an educational prototype.

## Why this project
Eviction and housing instability are not evenly distributed. This project asks:
**How can we make rights + resources more visible at the neighborhood level?**

## What’s in this repo
- `data/zip_data.json` — curated ZIP-level resource + signal dataset
- `src/pressure_score.py` — computes a normalized weighted Pressure Score
- `data/zip_data_scored.json` — output with computed scores
- `docs/notes.md` — design + future roadmap

## Pressure Score (0–100)
The score is a **normalized weighted index** built from:
- rent burden %
- poverty %
- unemployment %

Weights (v1):
- rent burden: 0.5
- poverty: 0.3
- unemployment: 0.2

## How to run
```bash
python src/pressure_score.py
