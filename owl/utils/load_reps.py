# Author(s):
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment:
#    Senior Project (Summer 2025) - "load_reps.py"
# Last Update:
#    June 18 2025
# Purpose:
#    This script loads "Representatives" table in database with rep and required fields.

import os
import csv
import mysql.connector
from datetime import datetime

# === DATABASE CONNECTION ===
db = mysql.connector.connect(
    host='localhost',
    user='owladmin',
    password='securepassword',
    database='owl'
)

# raw_data directory
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw_data')

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").date()
    except (ValueError, TypeError):
        return None

def main():
    connection = db
    cursor = connection.cursor()

    for year in range(2021, 2025):
        txt_path = os.path.join(RAW_DATA_DIR, f"{year}_data", f"{year}FD.txt")
        if not os.path.exists(txt_path):
            print(f"File not found: {txt_path}")
            continue

        print(f"Processing: {txt_path}")
        with open(txt_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                prefix = row.get('Prefix', '').strip() or None
                first = row.get('First', '').strip() or None
                last = row.get('Last', '').strip() or None
                suffix = row.get('Suffix', '').strip() or None
                filing_type = row.get('FilingType', '').strip() or None
                state_dst = row.get('StateDst', '').strip() or None
                filing_year = int(row.get('Year', 0)) if row.get('Year') else None
                filing_date = parse_date(row.get('FilingDate'))
                doc_id = row.get('DocID', '').strip() or None

                full_name = f"{first} {last}".strip()

                # Skip any empty or duplicate name-state combos
                if not full_name or not state_dst:
                    continue

                cursor.execute("""
                    INSERT INTO representatives (
                        name, state_district, prefix, first_name, last_name,
                        suffix, filing_type, filing_year, filing_date, doc_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    full_name, state_dst, prefix, first, last,
                    suffix, filing_type, filing_year, filing_date, doc_id
                ))

    connection.commit()
    cursor.close()
    connection.close()
    print("Population of Representatives table complete.")

if __name__ == "__main__":
    main()