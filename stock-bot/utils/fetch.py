import os
import json
from collections import defaultdict

HOUSE_DIR = "House"

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
    with open(filename, 'w') as f:
        json.dump(reps_data, f, indent=2)
    print(f"\nSaved summary to {filename}")


if __name__ == "__main__":
    data = summarize_disclosures()
    display_summary(data)
    save_summary_to_json(data)
