import requests, zipfile
from io import BytesIO

def download_disclosures(year):
    try:
        if year not in {'2021', '2022', '2023', '2024', '2025'}:
            return None, "Invalid year."

        zip_url = f'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.zip'
        
        # Download the zip file into memory
        response = requests.get(zip_url)
        if response.status_code != 200:
            return None, f"Failed to download file for {year}. HTTP {response.status_code}"

        # Create a BytesIO object from the downloaded content
        zip_buffer = BytesIO(response.content)
        
        # Verify the zip file is valid
        try:
            with zipfile.ZipFile(zip_buffer) as z:
                # Verify zip file contents
                if not any(name.endswith('FD.txt') for name in z.namelist()):
                    return None, "Invalid zip file structure"
        except zipfile.BadZipFile:
            return None, "Invalid zip file format"

        # Reset buffer position to start
        zip_buffer.seek(0)
        return zip_buffer, f"disclosures_{year}.zip"

    except Exception as e:
        return None, f"Error: {str(e)}"