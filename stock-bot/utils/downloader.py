# Author(s): 
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment: 
#    Senior Project (Summer 2025) - "Stock Bot"
# Last Update: 
#    June 8 2025
# Purpose: 
#    This script downloads each raw disclosure, and extracts it.

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
        return None, f"Error: {str(e)}"