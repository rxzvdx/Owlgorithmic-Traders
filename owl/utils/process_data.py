"""
Author(s):
    Antonio Rosado
    Kashan Khan
    Imad Khan
    Alexander Schifferle
    Mike Kheang
Assignment:
    Senior Project (Summer 2025) - "process_data.py"
Last Update:
    Revised June 22, 2025
Purpose:
    Parse Rep. transactions from PDFs into a JSON as a fail-safe when DB is down
"""

import os
import json
from fetch      import summarize_disclosures
from pdf_parser import parse_transactions
from concurrent.futures import ProcessPoolExecutor

# -----------------path setup -----------------------------------------------------------------------
HERE        = os.path.dirname(__file__)                         # .../owl/utils
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))  # .../Owlgorithmic-Traders
HOUSE_DIR   = os.path.join(PROJECT_ROOT, "house")               # .../Owlgorithmic-Traders/house
DATA_DIR    = os.path.join(PROJECT_ROOT, "term_logs")           # .../Owlgorithmic-Traders/term_logs
CACHE_FILE  = os.path.join(DATA_DIR, "trades_cache.json")
LOG_FILE    = os.path.join(DATA_DIR, "processed.txt")
# ---------------------------------------------------------------------------------------------------

def parse_one(task):
    """
    Top-level helper so it can be pickled by ProcessPoolExecutor.
    Expects a tuple (rep_name, year, pdf_path), returns
    (rep_name, year, pdf_path, [parsed_transactions])
    """
    rep, year, pdf_path = task
    txs = parse_transactions(pdf_path)
    return rep, year, pdf_path, txs

def build_cache():
    # load already-done set
    processed = set()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            processed = set(line.strip() for line in f if line.strip())

    # gather every PDF that still needs parsing
    summary = summarize_disclosures(base_dir=HOUSE_DIR)
    tasks = []
    for rep, years in summary.items():
        for year, pdfs in years.items():
            for fname in pdfs:
                path = os.path.join(HOUSE_DIR, rep, year, fname)
                if path not in processed:
                    tasks.append((rep, year, path))
    cache = {}

    # parse in parallel
    with ProcessPoolExecutor() as pool:
        for rep, year, pdf_path, txs in pool.map(parse_one, tasks):
            entry = cache.setdefault(rep, {"filings": [], "transactions": []})
            entry["filings"].append({
                "year": year,
                "doc_id": os.path.splitext(os.path.basename(pdf_path))[0]
            })
            entry["transactions"].extend(txs)
            processed.add(pdf_path)

    # write out cache and updated log
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(sorted(processed)))

    print(f"Cache written to {CACHE_FILE}")
    print(f"Processed log updated at {LOG_FILE}")

if __name__ == "__main__":
    build_cache()
