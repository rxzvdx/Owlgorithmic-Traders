import os
import json
import requests
import zipfile
from collections import defaultdict
from io import BytesIO

RAW_DATA_DIR = "raw_data"
VALID_YEARS = {'2021', '2022', '2023', '2024', '2025'}
HOUSE_DIR = "House"

def download_and_extract_disclosures(year):
    if year not in VALID_YEARS:
        return False, f"Invalid year: {year}"

    zip_url = f'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.zip'
    year_dir = os.path.join(RAW_DATA_DIR, f"{year}_data")
    os.makedirs(year_dir, exist_ok=True)

    try:
        response = requests.get(zip_url)
        if response.status_code != 200:
            return False, f"Failed to download {year}. HTTP {response.status_code}"

        zip_path = os.path.join(year_dir, f"{year}.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)

        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall(year_dir)

        return True, f"{year} data downloaded and extracted successfully."
    except Exception as e:
        return False, f"Error downloading {year}: {str(e)}"

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

def save_summary_to_json(reps_data, json_path=os.path.join(RAW_DATA_DIR, "rep_summary.json")):
    with open(json_path, 'w') as f:
        json.dump(reps_data, f, indent=2)
    print(f"\nSaved summary to {json_path}")

if __name__ == "__main__":
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    for year in VALID_YEARS:
        success, message = download_and_extract_disclosures(year)
        print(message)

    summary = summarize_disclosures()
    save_summary_to_json(summary)
