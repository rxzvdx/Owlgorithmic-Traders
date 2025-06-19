# -*- coding: utf-8 -*-
"""
Author(s):
    Antonio Rosado
    Kashan Khan
    Imad Khan
    Alexander Schifferle
    Mike Kheang
Assignment:
    Senior Project (Summer 2025) - "stock_bot.py"
Last Update:
    May 28, 2025
Purpose:
    Download and extract ZIP archives of financial disclosures for each year,
    parse metadata text files, and optionally download individual PDF reports
    organized by filer name under a House directory.
"""

import os
import requests       # HTTP requests for downloading ZIPs and PDFs
import zipfile        # Handling ZIP archive extraction
import csv            # Reading tab-delimited metadata files
import re             # Sanitizing directory names with regex
from datetime import datetime

# === Constants and Directory Configuration ===
YEARS = ['2021', '2022', '2023', '2024', '2025']
BASE_URL = 'https://disclosures-clerk.house.gov/public_disc'
ROOT_DIR = os.getcwd()  # Base path of the current working directory
HOUSE_DIR = os.path.join(ROOT_DIR, 'House')
RAW_DATA_DIR = os.path.join(ROOT_DIR, 'Raw Data')
LOGS_DIR = os.path.abspath(os.path.join(ROOT_DIR, '..', 'Terminal Logs'))

# Ensure all required directories exist before proceeding
os.makedirs(HOUSE_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Log file paths
log_path = os.path.join(LOGS_DIR, 'download_log.txt')
error_log_path = os.path.join(LOGS_DIR, 'failed_downloads.txt')

# Clear previous logs at start
open(log_path, 'w').close()
open(error_log_path, 'w').close()


def sanitize_name(name: str) -> str:
    """
    Remove illegal filesystem characters from a name string.
    """
    return re.sub(r'[<>:"/\\|?*]', '', name)


def log(message: str, error: bool = False):
    """
    Append a timestamped message to the main log, and on error also to the error log.
    Prints to console as well.
    """
    timestamp = datetime.now()
    with open(log_path, 'a') as lf:
        lf.write(f"{timestamp} - {message}\n")
    if error:
        with open(error_log_path, 'a') as ef:
            ef.write(f"{timestamp} - {message}\n")
    print(message)


def download_and_extract(year: str) -> str:
    """
    Download the ZIP archive for a given year, extract its contents to RAW_DATA_DIR,
    and return the path to the extracted metadata text file or None on failure.
    """
    zip_url = f"{BASE_URL}/financial-pdfs/{year}FD.zip"
    zip_path = os.path.join(RAW_DATA_DIR, f"{year}.zip")
    metadata_path = os.path.join(RAW_DATA_DIR, f"{year}FD.txt")

    try:
        r = requests.get(zip_url)
        if r.status_code != 200:
            log(f"Failed to download ZIP for {year}: HTTP {r.status_code}", error=True)
            return None

        # Write ZIP to disk
        with open(zip_path, 'wb') as f:
            f.write(r.content)
        log(f"Downloaded ZIP: {zip_path}")

        # Extract all contents, including metadata .txt
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(RAW_DATA_DIR)
        log(f"Extracted contents of ZIP: {zip_path}")

        return metadata_path
    except Exception as e:
        log(f"Error downloading/extracting {year}: {e}", error=True)
        return None


def download_pdfs(year: str, metadata_path: str):
    """
    Read the metadata text file for a year and download individual PDF reports
    to subdirectories under HOUSE_DIR named by filer (Last_First).
    """
    pdf_base_url = f"{BASE_URL}/ptr-pdfs/{year}/"

    # Open the metadata file and iterate rows
    with open(metadata_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            # Skip rows lacking required fields
            if len(row) < 9:
                continue
            last, first, doc_id = row[1], row[2], row[8]
            if not doc_id.isdigit():
                continue

            # Build a safe directory name and create it
            name_dir = sanitize_name(f"{last}_{first}")
            year_dir = os.path.join(HOUSE_DIR, name_dir, year)
            os.makedirs(year_dir, exist_ok=True)

            # Download and save the PDF
            pdf_url = f"{pdf_base_url}{doc_id}.pdf"
            pdf_path = os.path.join(year_dir, f"{doc_id}.pdf")
            try:
                r = requests.get(pdf_url)
                if r.status_code == 200:
                    with open(pdf_path, 'wb') as pdf_file:
                        pdf_file.write(r.content)
                    log(f"Downloaded: {pdf_path}")
                else:
                    log(f"Failed: {pdf_url} (HTTP {r.status_code})", error=True)
            except Exception as e:
                log(f"Error downloading {pdf_url}: {e}", error=True)


# === Main execution loop ===
for year in YEARS:
    metadata = download_and_extract(year)
    if metadata:
        download_pdfs(year, metadata)
