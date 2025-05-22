import os, requests, zipfile, csv

def download_disclosures(year):
    try:
        if year not in {'2021', '2022', '2023', '2024', '2025'}:
            return False, "Invalid year."

        zip_url = f'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.zip'
        pdf_base_url = f'https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{year}/'
        zip_filename = f'{year}.zip'
        metadata_txt = f'{year}FD.txt'

        r = requests.get(zip_url)
        if r.status_code != 200:
            return False, f"Failed to download file for {year}. HTTP {r.status_code}"

        with open(zip_filename, 'wb') as f:
            f.write(r.content)

        with zipfile.ZipFile(zip_filename) as z:
            z.extractall('.')

        # Optional: Verify content
        if not os.path.exists(metadata_txt):
            return False, "Metadata TXT file not found after extraction."

        return True, f"Successfully downloaded and extracted disclosures for {year}."
    except Exception as e:
        return False, f"Error: {str(e)}"