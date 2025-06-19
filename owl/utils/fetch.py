"""
Author(s):
    Antonio Rosado
    Kashan Khan
    Imad Khan
    Alexander Schifferle
    Mike Kheang
Assignment:
    Senior Project (Summer 2025) - "fetch.py"
Last Update:
    Revised June 19, 2025
Purpose:
    Summarize and organize PDF disclosures for each representative
    from the raw 'house' directory and save a summary JSON.
"""

import os
import json
from collections import defaultdict

# Directory where per-representative PDF folders reside
HOUSE_DIR = "house"


def summarize_disclosures(base_dir: str = HOUSE_DIR) -> dict:
    """
    Walk through the house directory, collecting PDF filenames by representative and year.

    Args:
        base_dir (str): Path to the root 'house' directory containing subfolders per rep.

    Returns:
        dict: Nested dict in the form {rep_name: {year: [pdf_filenames]}}
    """
    reps_data = defaultdict(lambda: defaultdict(list))

    # Iterate each representative folder
    for rep_folder in os.listdir(base_dir):
        rep_path = os.path.join(base_dir, rep_folder)
        if not os.path.isdir(rep_path):
            continue  # Skip non-directory files

        # Iterate each year subfolder for that representative
        for year_folder in os.listdir(rep_path):
            year_path = os.path.join(rep_path, year_folder)
            if not os.path.isdir(year_path):
                continue  # Skip non-directory files

            # List all PDF files in the year's folder
            pdfs = [f for f in os.listdir(year_path) if f.lower().endswith('.pdf')]
            reps_data[rep_folder][year_folder] = pdfs

    return reps_data


def display_summary(reps_data: dict) -> None:
    """
    Print a table summarizing the number of PDFs per representative per year.

    Args:
        reps_data (dict): Output from summarize_disclosures().
    """
    header = f"{'Representative':<30} {'Year':<6} {'# PDFs':<7}"
    print(header)
    print('-' * len(header))

    # Print each summary line
    for rep, years in reps_data.items():
        for year, pdfs in sorted(years.items()):
            print(f"{rep:<30} {year:<6} {len(pdfs):<7}")


def save_summary_to_json(reps_data: dict, filename: str = "rep_summary.json") -> None:
    """
    Save the summarized data to a JSON file under raw_data directory.

    Args:
        reps_data (dict): Data to serialize.
        filename (str): JSON filename.
    """
    # Determine project root and ensure raw_data exists
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    raw_data_dir = os.path.join(project_root, 'raw_data')
    os.makedirs(raw_data_dir, exist_ok=True)

    file_path = os.path.join(raw_data_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(reps_data, f, indent=2)

    print(f"Saved summary to {file_path}")


if __name__ == "__main__":
    # Summarize PDF counts
    data = summarize_disclosures()
    # Display a console table
    display_summary(data)
    # Persist summary to JSON for downstream use
    save_summary_to_json(data)
