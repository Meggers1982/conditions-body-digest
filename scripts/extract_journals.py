#!/usr/bin/env python3
"""
Extract journal data from PubMed_Journals_Categorized.xlsx into per-category CSVs.
Reads 5 target sheets and writes one CSV each to data/.
"""

import pandas as pd
from pathlib import Path

XLSX_PATH = Path("/Users/meaganmorris/Downloads/PubMed_Journals_Categorized.xlsx")
DATA_DIR  = Path(__file__).parent.parent / "data"
COLUMNS   = ["Journal Title", "ISSN (Print)", "ISSN (Online)", "Categories"]

SHEETS = [
    "Cancer & Oncology",
    "Brain & Mental Health",
    "Dermatology",
    "Allergy & Immunology",
    "Womens Health & Reproduction",
]

DATA_DIR.mkdir(parents=True, exist_ok=True)
xf = pd.ExcelFile(XLSX_PATH)

for sheet in SHEETS:
    df = pd.read_excel(xf, sheet_name=sheet)
    out = df[COLUMNS].copy()
    out["ISSN (Print)"]  = out["ISSN (Print)"].fillna("").astype(str).str.strip()
    out["ISSN (Online)"] = out["ISSN (Online)"].fillna("").astype(str).str.strip()
    out["Categories"]    = out["Categories"].fillna("").astype(str).str.strip()
    out = out[out["Journal Title"].notna()]
    filename = DATA_DIR / f"{sheet}.csv"
    out.to_csv(filename, index=False)
    print(f"  {sheet}: {len(out)} rows → {filename.name}")

print("Done.")
