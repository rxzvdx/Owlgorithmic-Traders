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
                first = row.get('First', '').strip() or None
                last = row.get('Last', '').strip() or None
                suffix = row.get('Suffix', '').strip() or None
                state_dst = row.get('StateDst', '').strip() or None

                full_name = f"{first} {last}".strip()

                # Skip any empty or duplicate name-state combos
                if not full_name or not state_dst:
                    continue

                # Check for existing representative
                cursor.execute("""
                    SELECT rep_id FROM representatives
                    WHERE first_name=%s AND last_name=%s AND state_district=%s AND suffix=%s
                """, (first, last, state_dst, suffix))
                if cursor.fetchone() is None:
                    cursor.execute("""
                        INSERT INTO representatives (name, state_district, first_name, last_name, suffix)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (full_name, state_dst, first, last, suffix))
                # else: already exists, skip

    connection.commit()
    cursor.close()
    connection.close()
    print("Population of Representatives table complete.")

if __name__ == "__main__":
    main()