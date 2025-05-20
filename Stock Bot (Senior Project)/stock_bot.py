# Author(s): 
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment: 
#    Senior Project (Summer 2025) - "Stock Bot"
# Last Update: 
#    May 20 2025
# Purpose: 
#    This script downloads a ZIP archive of financial disclosures, extracts its contents,
#    reads a tab-delimited text file with metadata about each disclosure,
#    and (optionally) downloads specific individual reports in PDF format
#    based on the name of the filer.



import csv, json, zipfile
# Standard library imports:
# - csv: to parse tab-delimited .txt data
# - json: unused in current code, but typically for storing structured data
# - zipfile: to extract contents from ZIP archive

import requests, PyPDF2
# Third-party libraries:
# - requests: to download files from the web
# - PyPDF2: (currently unused) would allow reading PDF content programmatically

# URL of the ZIP file containing financial disclosures from 2021
zip_file_url = 'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2021FD.ZIP'

# Base URL for accessing individual PDF reports by document ID
pdf_file_url = 'https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2021/'

# Send an HTTP GET request to download the ZIP file
r = requests.get(zip_file_url)

# Define the local filename to save the downloaded ZIP file
zipfile_name = '2021.zip'

# Save the downloaded ZIP file in binary write mode
with open(zipfile_name, 'wb') as f:
    f.write(r.content)  # Write the entire content of the response to disk

# Open and extract all contents of the ZIP archive into the current directory
with zipfile.ZipFile(zipfile_name) as z:
    z.extractall('.')  # '.' means extract to the current folder

# Open the extracted tab-delimited text file which contains metadata about disclosures
with open('2021FD.txt') as f:
    for line in csv.reader(f, delimiter='\t'):
        pass  # Currently no active logic; this just iterates over each disclosure entry

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

