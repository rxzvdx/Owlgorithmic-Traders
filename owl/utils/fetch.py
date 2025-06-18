# Author(s): 
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment: 
#    Senior Project (Summer 2025) - "fetch.py"
# Last Update: 
#    June 8 2025
# Purpose: 
#    This script manually downloads PDFs for each representative based on DOC_ID from raw data, 
#    and places them by name of Rep. in "House" directory.

import os
import json
from collections import defaultdict

HOUSE_DIR = "house"

def summarize_disclosures(base_dir=HOUSE_DIR):
    reps_data = defaultdict(lambda: defaultdict(list))  # {rep_name: {year: [pdfs]}}

    for rep_folder in os.listdir(base_dir):
        rep_path = os.path.join(base_dir, rep_folder)
        if not os.path.isdir(rep_path):
            continue

        for year_folder in os.listdir(rep_path):
            year_path = os.path.join(rep_path, year_folder)
            if not os.path.isdir(year_path):
                continue

            pdfs = [f for f in os.listdir(year_path) if f.lower().endswith('.pdf')]
            reps_data[rep_folder][year_folder] = pdfs

    return reps_data


def display_summary(reps_data):
    print(f"{'Representative':<30} {'Year':<6} {'# PDFs':<7}")
    print("-" * 50)

    for rep, years in reps_data.items():
        for year, pdfs in sorted(years.items()):
            print(f"{rep:<30} {year:<6} {len(pdfs):<7}")


def save_summary_to_json(reps_data, filename="rep_summary.json"):
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    raw_data_dir = os.path.join(parent_dir, 'raw_data')
    os.makedirs(raw_data_dir, exist_ok=True)

    file_path = os.path.join(raw_data_dir, filename)

    with open(file_path, 'w') as f:
        json.dump(reps_data, f, indent=2)

    print(f"\nSaved summary to {file_path}")


if __name__ == "__main__":
    data = summarize_disclosures()
    display_summary(data)
    save_summary_to_json(data)
