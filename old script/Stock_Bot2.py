import csv, zipfile
import requests

# URLs for the zip file and the base PDF file path
zip_file_url = 'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2021FD.ZIP'
pdf_file_url = 'https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2021/'

# Download the zip file
zipfile_name = '2021.zip'
r = requests.get(zip_file_url)
with open(zipfile_name, 'wb') as f:
    f.write(r.content)

# Extract the zip contents
with zipfile.ZipFile(zipfile_name) as z:
    z.extractall('.')

# Open the metadata text file and download PDFs based on specific names
with open('2021FD.txt') as f:
    for line in csv.reader(f, delimiter='\t'):
        if len(line) < 9:
            continue  # Skip malformed lines

     #    if line[1] == 'McKinley':
     #        doc_id = line[8]
     #        r = requests.get(f"{pdf_file_url}{doc_id}.pdf")
     #        with open(f"{doc_id}.pdf", 'wb') as pdf_file:
     #            pdf_file.write(r.content)

     #    if line[1] == 'Moore' and line[2] == 'Blake':
     #        doc_id = line[8]
     #        r = requests.get(f"{pdf_file_url}{doc_id}.pdf")
     #        with open(f"{doc_id}.pdf", 'wb') as pdf_file:
     #            pdf_file.write(r.content)

     #    if line[1] == 'Newman' and line[2] == 'Marie':
     #        doc_id = line[8]
     #        r = requests.get(f"{pdf_file_url}{doc_id}.pdf")
     #        with open(f"{doc_id}.pdf", 'wb') as pdf_file:
     #            pdf_file.write(r.content)

        if line[1] == 'Pelosi':
            doc_id = line[8]
            r = requests.get(f"{pdf_file_url}{doc_id}.pdf")
            with open(f"{doc_id}.pdf", 'wb') as pdf_file:
                pdf_file.write(r.content)

     #    if line[1] == 'Perlmutter' and line[2] == 'Ed':
     #        doc_id = line[8]
     #        r = requests.get(f"{pdf_file_url}{doc_id}.pdf")
     #        with open(f"{doc_id}.pdf", 'wb') as pdf_file:
     #            pdf_file.write(r.content)

     #    if line[1] == 'Peters' and line[2] == 'Scott H.':
     #        doc_id = line[8]
     #        r = requests.get(f"{pdf_file_url}{doc_id}.pdf")
     #        with open(f"{doc_id}.pdf", 'wb') as pdf_file:
     #            pdf_file.write(r.content)

     #    if line[1] == 'Phillips' and line[2] == 'Dean':
     #        doc_id = line[8]
     #        r = requests.get(f"{pdf_file_url}{doc_id}.pdf")
     #        with open(f"{doc_id}.pdf", 'wb') as pdf_file:
     #            pdf_file.write(r.content)

     #    if line[1] == 'Rogers' and line[2] == 'Harold Dallas':
     #        doc_id = line[8]
     #        r = requests.get(f"{pdf_file_url}{doc_id}.pdf")
     #        with open(f"{doc_id}.pdf", 'wb') as pdf_file:
     #            pdf_file.write(r.content)
