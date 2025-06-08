# Author(s): 
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment: 
#    Senior Project (Summer 2025) - "Stock Bot"
# Last Update: 
#    May 28 2025
# Purpose: 
#    This script downloads a ZIP archive of financial disclosures, extracts its contents,
#    reads a tab-delimited text file with metadata about each disclosure,
#    and (optionally) downloads specific individual reports in PDF format
#    based on the name of the filer.

import os
import requests
import zipfile
import csv
import re
from datetime import datetime

# Constants
YEARS = ['2021', '2022', '2023', '2024', '2025']
BASE_URL = 'https://disclosures-clerk.house.gov/public_disc'
ROOT_DIR = os.getcwd()
HOUSE_DIR = os.path.join(ROOT_DIR, 'House')
RAW_DATA_DIR = os.path.join(ROOT_DIR, 'Raw Data')
LOGS_DIR = os.path.abspath(os.path.join(ROOT_DIR, '..', 'Terminal Logs'))

# Create required directories
os.makedirs(HOUSE_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Paths for logs
log_path = os.path.join(LOGS_DIR, 'download_log.txt')
error_log_path = os.path.join(LOGS_DIR, 'failed_downloads.txt')

# Clean old logs
open(log_path, 'w').close()
open(error_log_path, 'w').close()

# Helper to clean directory names
def sanitize_name(name):
    return re.sub(r'[<>:"/\\|?*]', '', name)

# Logging function
def log(message, error=False):
    with open(log_path, 'a') as lf:
        lf.write(f"{datetime.now()} - {message}\n")
    if error:
        with open(error_log_path, 'a') as ef:
            ef.write(f"{datetime.now()} - {message}\n")
    print(message)

# Download and extract ZIP + TXT
def download_and_extract(year):
    zip_url = f"{BASE_URL}/financial-pdfs/{year}FD.zip"
    zip_path = os.path.join(RAW_DATA_DIR, f"{year}.zip")
    metadata_path = os.path.join(RAW_DATA_DIR, f"{year}FD.txt")

    try:
        r = requests.get(zip_url)
        if r.status_code != 200:
            log(f"Failed to download ZIP for {year}: HTTP {r.status_code}", error=True)
            return None

        with open(zip_path, 'wb') as f:
            f.write(r.content)
        log(f"Downloaded ZIP: {zip_path}")

        with zipfile.ZipFile(zip_path) as z:
            z.extractall(RAW_DATA_DIR)
        log(f"Extracted contents of ZIP: {zip_path}")

        return metadata_path
    except Exception as e:
        log(f"Error downloading/extracting {year}: {e}", error=True)
        return None

# Download PDFs from metadata
def download_pdfs(year, metadata_path):
    pdf_base_url = f"{BASE_URL}/ptr-pdfs/{year}/"

    with open(metadata_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) < 9:
                continue
            last, first, doc_id = row[1], row[2], row[8]
            if not doc_id.isdigit():
                continue

            name_dir = sanitize_name(f"{last}_{first}")
            year_dir = os.path.join(HOUSE_DIR, name_dir, year)
            os.makedirs(year_dir, exist_ok=True)

            pdf_url = f"{pdf_base_url}{doc_id}.pdf"
            pdf_path = os.path.join(year_dir, f"{doc_id}.pdf")

            try:
                r = requests.get(pdf_url)
                if r.status_code == 200:
                    with open(pdf_path, 'wb') as f:
                        f.write(r.content)
                    log(f"Downloaded: {pdf_path}")
                else:
                    log(f"Failed: {pdf_url} (HTTP {r.status_code})", error=True)
            except Exception as e:
                log(f"Error downloading {pdf_url}: {e}", error=True)

# Run process for all years
for year in YEARS:
    metadata = download_and_extract(year)
    if metadata:
        download_pdfs(year, metadata)
