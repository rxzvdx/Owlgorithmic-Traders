# DEPRECATED

import csv, json, zipfile
# Standard library imports:
# - csv: to parse tab-delimited .txt data
# - json: unused in current code, but typically for storing structured data
# - zipfile: to extract contents from ZIP archive

import requests, PyPDF2
# Third-party libraries:
# - requests: to download files from the web
# - PyPDF2: (currently unused) would allow reading PDF content programmatically

# Prompt user for input
year = input("Enter the year (2021-2025): ")

# Validate user input
if year not in {'2021', '2022', '2023', '2024', '2025'}:
    raise ValueError("Invalid year. Please enter a year between 2021 and 2025.")

# URL of the ZIP file containing financial disclosures from 2021
zip_file_url = f'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.zip'

# Base URL for accessing individual PDF reports by document ID
pdf_file_url = 'https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{year}/'


# Define the local filename to save the downloaded ZIP file
zipfile_name = f'{year}.zip'
metadata_txt_filename = f'{year}FD.txt'

# Send an HTTP GET request to download the ZIP file
r = requests.get(zip_file_url)
with open(zipfile_name, 'wb') as f: # Save the downloaded ZIP file in binary write mode
    f.write(r.content)  # Write the entire content of the response to disk

# Open and extract all contents of the ZIP archive into the current directory
with zipfile.ZipFile(zipfile_name) as z:
    z.extractall('.')  # '.' means extract to the current folder

# Open the extracted tab-delimited text file which contains metadata about disclosures
with open(metadata_txt_filename) as f:
    for line in csv.reader(f, delimiter='\t'):
        pass  
        # Currently no active logic; this just iterates over each disclosure entry

        # The following blocks are examples of how to filter and download specific PDF reports
        # Each block checks for a specific member of Congress and downloads their disclosure PDF

        # Example: If the filer is McKinley (last name)
        # if line[1] == 'McKinley':
        #     date = line[7]  # Date of the report
        #     doc_id = line[8]  # Document ID used to fetch the PDF
        #     r = requests.get(f"{pdf_file_url}{doc_id}.pdf")  # Download the PDF
        #     with open(f"{doc_id}.pdf", 'wb') as pdf_file:
        #         pdf_file.write(r.content)  # Save the PDF locally

        # if line[1] == 'Moore' and line[2] == 'Blake':  # Full name match
        #     ...

        # Additional examples provided:
        # - Marie Newman
        # - Nancy Pelosi
        # - Ed Perlmutter
        # - Scott H. Peters
        # - Dean Phillips
        # - Harold Dallas Rogers

        # Each block follows the same logic:
        # 1. Match by name.
        # 2. Extract the document ID and date.
        # 3. Construct the URL and download the PDF.
        # 4. Save it using the document ID as filename.
    else:
        print(f"Download failed: HTTP {r.status_code} for {zip_file_url}")