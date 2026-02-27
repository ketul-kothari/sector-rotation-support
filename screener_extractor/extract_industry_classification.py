"""
Extract NSE Industry Classification from PDF and create a CSV file.

Output CSV columns:
    MES_code, MES_name, Sector_code, Sector_name,
    Industry_code, Industry_name, basic_industry_code, basic_industry_name
"""

import pdfplumber
import csv
import os

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
PDF_PATH   = os.path.join(DATA_DIR, "nse-indices_industry-classification-structure-2023-07.pdf")
OUTPUT_CSV = os.path.join(DATA_DIR, "nse_industry_classification.csv")


def clean(text: str) -> str:
    """Collapse newlines / extra spaces inside a cell."""
    if not text:
        return ""
    return " ".join(text.split())


def extract_rows():
    rows = []
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Skip header rows
                    if row[0] and row[0].startswith("MES_Code"):
                        continue
                    # Only keep rows that have at least a Basic_Ind_Code (col 6)
                    if not row[6]:
                        continue
                    rows.append([clean(c) for c in row])
    return rows


def forward_fill(rows):
    """Forward-fill MES / Sector / Industry columns (they only appear once per group)."""
    last = ["", "", "", "", "", "", "", "", ""]
    filled = []
    for row in rows:
        new_row = list(row)
        for i in range(9):
            if new_row[i]:
                last[i] = new_row[i]
            else:
                new_row[i] = last[i]
        filled.append(new_row)
    return filled


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Reading PDF: {PDF_PATH}")
    rows = extract_rows()
    print(f"  Raw data rows extracted: {len(rows)}")

    rows = forward_fill(rows)

    # Columns in table: 0=MES_Code, 1=MES_name, 2=Sect_Code, 3=Sector,
    #                   4=Ind_Code, 5=Industry, 6=Basic_Ind_Code, 7=Basic Industry, 8=Definition
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "MES_code", "MES_name",
            "Sector_code", "Sector_name",
            "Industry_code", "Industry_name",
            "basic_industry_code", "basic_industry_name"
        ])
        for row in rows:
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])

    print(f"  CSV written: {OUTPUT_CSV}")
    print(f"  Total basic industries: {len(rows)}")


if __name__ == "__main__":
    main()
