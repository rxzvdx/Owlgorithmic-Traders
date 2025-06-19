"""
Author(s):
    Antonio Rosado
    Kashan Khan
    Imad Khan
    Alexander Schifferle
    Mike Kheang
Assignment:
    Senior Project (Summer 2025) - "downloader.py"
Last Update:
    June 8, 2025
Purpose:
    Download and extract each year's raw disclosure ZIP archive,
    saving contents under the `raw_data` directory for later processing.
"""

import os
import requests         # HTTP requests for downloading files
import zipfile          # Working with ZIP archives
from io import BytesIO  # In-memory byte streams for ZIP extraction
from collections import defaultdict
import json             # Placeholder for future JSON handling

# Directory where raw ZIPs and extracted data will be stored
RAW_DATA_DIR = "raw_data"
# Supported disclosure years
VALID_YEARS = {'2021', '2022', '2023', '2024', '2025'}
# Optional: subdirectory for House-specific files
HOUSE_DIR = "House"


def download_and_extract_disclosures(year: str):
    """
    Download the disclosure ZIP for a given year, save locally, and extract its contents.

    Args:
        year (str): Four-digit year to download (must be in VALID_YEARS).

    Returns:
        tuple(BytesIO, str): In-memory ZIP bytes and suggested filename on success.
        tuple(False, str): False and error message if the year is invalid or HTTP error.
        tuple(None, str): None and exception message on unexpected errors.
    """
    # Validate the requested year
    if year not in VALID_YEARS:
        return False, f"Invalid year: {year}"

    # Build download URL and prepare local folder
    zip_url = f'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.zip'
    year_dir = os.path.join(RAW_DATA_DIR, f"{year}_data")
    os.makedirs(year_dir, exist_ok=True)

    try:
        # Fetch the ZIP archive
        response = requests.get(zip_url)
        if response.status_code != 200:
            return False, f"Failed to download {year}. HTTP {response.status_code}"

        # Save the ZIP file to disk
        zip_path = os.path.join(year_dir, f"{year}.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)

        # Extract the ZIP contents into the year-specific directory
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall(year_dir)

        # Return the raw ZIP bytes and a descriptive filename
        return BytesIO(response.content), f"{year}_disclosures.zip"

    except Exception as e:
        # Catch-all error handling
        return None, f"Error: {str(e)}"
