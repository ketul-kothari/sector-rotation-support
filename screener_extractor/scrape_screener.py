"""
Scrape screener.in for all NSE stocks per basic industry.

Reads: nse_industry_classification.csv
Output: screener_stocks_by_industry.csv

Output columns:
    macro_sector_name, sector_name, industry_name, basic_industry_name,
    company, symbol, market_cap

Usage:
    python scrape_screener.py

Notes:
  - BSE-only stocks (symbol is a pure number) are skipped and logged.
  - Pagination is handled automatically.
  - A polite delay is added between requests to avoid rate-limiting.
"""

import csv
import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup

# Force UTF-8 output on Windows to avoid cp1252 encoding errors
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR     = os.path.join(BASE_DIR, "data")
INPUT_CSV    = os.path.join(DATA_DIR, "nse_industry_classification.csv")
OUTPUT_CSV   = os.path.join(DATA_DIR, "screener_stocks_by_industry.csv")
SKIPPED_CSV  = os.path.join(DATA_DIR, "screener_skipped_bse_stocks.csv")

# ── Config ───────────────────────────────────────────────────────────────────
BASE_URL        = "https://www.screener.in"
REQUEST_DELAY   = 1.5   # seconds between page requests
REQUEST_TIMEOUT = 20    # seconds
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def build_market_url(mes_code, sector_code, industry_code, basic_code, page=1):
    path = f"/market/{mes_code}/{sector_code}/{industry_code}/{basic_code}/"
    if page > 1:
        return f"{BASE_URL}{path}?page={page}"
    return f"{BASE_URL}{path}"


def get_page(url: str) -> BeautifulSoup | None:
    """Fetch a URL and return a BeautifulSoup object, or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "lxml")
        print(f"    [WARN] HTTP {resp.status_code} for {url}")
        return None
    except Exception as exc:
        print(f"    [ERROR] Request failed for {url}: {exc}")
        return None


def parse_total_pages(soup: BeautifulSoup) -> int:
    """Return the total number of pages from the pagination widget."""
    pagination = soup.find("div", class_="pagination")
    if not pagination:
        return 1
    links = pagination.find_all("a", href=True)
    max_page = 1
    for link in links:
        m = re.search(r"page=(\d+)", link["href"])
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def parse_stocks(soup: BeautifulSoup, industry_info: dict, skipped_log: list) -> list[dict]:
    """
    Parse the stock table on a screener.in market page.
    Returns a list of dicts with the output columns.
    BSE stocks (numeric symbol) are appended to skipped_log and excluded.
    """
    results = []
    table = soup.find("table")
    if not table:
        return results

    rows = table.find_all("tr")[1:]  # skip header

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue

        name_cell = cells[1]
        link_tag  = name_cell.find("a", href=True)

        if not link_tag:
            continue

        href = link_tag["href"]                          # e.g. /company/LT/consolidated/
        company_name = link_tag.get_text(strip=True)

        # Extract symbol from URL
        m = re.match(r"^/company/([^/]+)/", href)
        if not m:
            continue
        symbol = m.group(1)

        # Skip BSE stocks (symbol is a pure number in the company URL)
        if re.match(r"^\d+$", symbol):
            print(f"    [SKIP BSE] {company_name} | URL: {href} | industry: {industry_info['basic_industry_name']}")
            skipped_log.append({
                "reason": "BSE stock (numeric symbol)",
                "company": company_name,
                "symbol": symbol,
                "url": href,
                "basic_industry": industry_info["basic_industry_name"],
            })
            continue

        # Market cap is column index 4 (0-based)
        market_cap_text = cells[4].get_text(strip=True).replace(",", "")

        results.append({
            "macro_sector_name":    industry_info["MES_name"],
            "sector_name":          industry_info["Sector_name"],
            "industry_name":        industry_info["Industry_name"],
            "basic_industry_name":  industry_info["basic_industry_name"],
            "company":              company_name,
            "symbol":               symbol,
            "market_cap":           market_cap_text,
        })

    return results


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Load industry classification
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        industries = list(csv.DictReader(f))

    total = len(industries)
    print(f"Loaded {total} basic industries from {INPUT_CSV}\n")

    all_stocks   = []
    skipped_log  = []

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as out_f:
        fieldnames = [
            "macro_sector_name", "sector_name", "industry_name",
            "basic_industry_name", "company", "symbol", "market_cap"
        ]
        writer = csv.DictWriter(out_f, fieldnames=fieldnames)
        writer.writeheader()

        for idx, ind in enumerate(industries, start=1):
            mes_code      = ind["MES_code"]
            sector_code   = ind["Sector_code"]
            industry_code = ind["Industry_code"]
            basic_code    = ind["basic_industry_code"]
            basic_name    = ind["basic_industry_name"]

            print(f"({idx}/{total}) {basic_name}  [{basic_code}]")

            page_num    = 1
            total_pages = 1
            page_stocks = 0

            while page_num <= total_pages:
                url  = build_market_url(mes_code, sector_code, industry_code, basic_code, page_num)
                soup = get_page(url)

                if soup is None:
                    print(f"    Skipping page {page_num} — failed to fetch")
                    break

                if page_num == 1:
                    total_pages = parse_total_pages(soup)
                    if total_pages > 1:
                        print(f"    Pages: {total_pages}")

                stocks = parse_stocks(soup, ind, skipped_log)
                writer.writerows(stocks)
                out_f.flush()
                page_stocks += len(stocks)
                all_stocks.extend(stocks)

                page_num += 1
                if page_num <= total_pages:
                    time.sleep(REQUEST_DELAY)

            print(f"    -> {page_stocks} NSE stocks collected")
            time.sleep(REQUEST_DELAY)

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Done.")
    print(f"  Total NSE stocks saved : {len(all_stocks)}")
    print(f"  Total skipped (BSE)    : {len(skipped_log)}")
    print(f"  Output CSV             : {OUTPUT_CSV}")

    if skipped_log:
        with open(SKIPPED_CSV, "w", newline="", encoding="utf-8") as sf:
            skip_fields = ["reason", "company", "symbol", "url", "basic_industry"]
            sw = csv.DictWriter(sf, fieldnames=skip_fields)
            sw.writeheader()
            sw.writerows(skipped_log)
        print(f"  Skipped stocks CSV     : {SKIPPED_CSV}")


if __name__ == "__main__":
    main()
