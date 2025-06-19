"""
Author(s):
    Antonio Rosado
    Kashan Khan
    Imad Khan
    Alexander Schifferle
    Mike Kheang
Assignment:
    Senior Project (Summer 2025) - "load_reps.py"
Last Update:
    June 18, 2025
Purpose:
    Parse raw disclosure .txt files for each year and populate the
    `representatives` table in the MySQL database with
    representative metadata (name, state/district, filing info).
"""

import os
import csv
import mysql.connector          # MySQL driver
from datetime import datetime

def parse_date(date_str: str):
    """
    Convert a date string in 'MM/DD/YYYY' format to a datetime.date.

    Args:
        date_str (str): Date string from the .txt data.

    Returns:
        datetime.date or None: Parsed date or None if invalid.
    """
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").date()
    except (ValueError, TypeError):
        return None


# === CONFIGURATION ===
# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'user': 'owladmin',
    'password': 'securepassword',
    'database': 'owl'
}
# Directory containing raw .txt files per year
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw_data')


def main():
    """
    Main entry point: connect to the database, read each year's .txt,
    extract representative fields, and insert into representatives table.
    """
    # Establish database connection
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    # Process each disclosure text file for years 2021–2024
    for year in range(2021, 2025):
        txt_path = os.path.join(RAW_DATA_DIR, f"{year}_data", f"{year}FD.txt")
        if not os.path.exists(txt_path):
            print(f"File not found: {txt_path}")
            continue

        print(f"Processing file: {txt_path}")
        with open(txt_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                # Extract and sanitize fields
                prefix       = row.get('Prefix', '').strip() or None
                first        = row.get('First', '').strip() or None
                last         = row.get('Last', '').strip() or None
                suffix       = row.get('Suffix', '').strip() or None
                filing_type  = row.get('FilingType', '').strip() or None
                state_dst    = row.get('StateDst', '').strip() or None
                filing_year  = int(row.get('Year', 0)) if row.get('Year') else None
                filing_date  = parse_date(row.get('FilingDate'))
                doc_id       = row.get('DocID', '').strip() or None

                # Construct full name
                full_name = " ".join(filter(None, [first, last]))

                # Skip rows missing essential info
                if not full_name or not state_dst:
                    continue

                # Insert into the representatives table
                cursor.execute(
                    """
                    INSERT INTO representatives (
                        name, state_district, prefix, first_name, last_name,
                        suffix, filing_type, filing_year, filing_date, doc_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        full_name, state_dst, prefix, first, last,
                        suffix, filing_type, filing_year, filing_date, doc_id
                    )
                )

    # Commit all inserts and clean up
    connection.commit()
    cursor.close()
    connection.close()
    print("Population of the representatives table is complete.")


if __name__ == "__main__":
    main()
