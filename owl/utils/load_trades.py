"""
Author(s):
    Antonio Rosado
    Kashan Khan
    Imad Khan
    Alexander Schifferle
    Mike Kheang
Assignment:
    Senior Project (Summer 2025) - "load_trades.py"
Last Update:
    Revised June 18, 2025
Purpose:
    Walk through all downloaded PDF disclosures, extract trade data for each
    representative, match to DB rep_id, and insert trade records into the
    `trades` table.
"""

import os
import logging
from datetime import datetime
import mysql.connector      # type: ignore
from pdf_parser import extract_trade_data_from_pdf

# === SETUP LOGGING ===
log_file_path = os.path.join(os.path.dirname(__file__), 'load_trades.log')
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# === DATABASE CONFIGURATION ===
DB_CONFIG = {
    'host': 'localhost',
    'user': 'owladmin',
    'password': 'securepassword',
    'database': 'owl'
}

# Establish a persistent DB connection and cursor
db = mysql.connector.connect(**DB_CONFIG)
cursor = db.cursor()

# Directory tree where per-rep PDF folders reside
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'house'))


def normalize_name(name: str) -> str:
    """
    Normalize a representative's name string for DB matching:
    - Lowercase
    - Strip commas
    - Collapse extra whitespace

    Args:
        name (str): Raw name (e.g., 'Smith, John')
    Returns:
        str: Normalized name (e.g., 'john smith')
    """
    return ' '.join(name.lower().replace(',', '').split())


# === MAIN PROCESSING LOOP ===
for rep_folder in os.listdir(BASE_DIR):
    rep_path = os.path.join(BASE_DIR, rep_folder)
    if not os.path.isdir(rep_path):
        continue  # Skip non-directory files

    # Each rep_folder contains subfolders by year
    for year_folder in os.listdir(rep_path):
        year_path = os.path.join(rep_path, year_folder)
        if not os.path.isdir(year_path):
            continue

        # Process each PDF in the year directory
        for filename in os.listdir(year_path):
            if not filename.lower().endswith('.pdf'):
                continue

            pdf_path = os.path.join(year_path, filename)
            trades = extract_trade_data_from_pdf(pdf_path)
            if not trades:
                continue  # No trades found in PDF

            # Match representative by name and state district
            rep_name_norm = normalize_name(trades[0]['rep_name'])
            state_district = trades[0]['state_district'].strip()

            try:
                # Query all reps for this district
                cursor.execute(
                    "SELECT rep_id, name FROM representatives WHERE state_district = %s",
                    (state_district,)
                )
                candidates = cursor.fetchall()

                # Find exact name match among candidates
                rep_id = None
                for rid, db_name in candidates:
                    if normalize_name(db_name) == rep_name_norm:
                        rep_id = rid
                        break

                if rep_id is None:
                    msg = f"Rep not found: {rep_name_norm} ({state_district})"
                    logging.warning(msg)
                    continue

                # Insert each trade record into DB
                for trade in trades:
                    date_str = trade.get('transaction_date')
                    notif_str = trade.get('notification_date')
                    if not date_str or not notif_str:
                        logging.warning(f"Skipping incomplete trade: {trade}")
                        continue

                    # Parse date strings into date objects
                    try:
                        trans_date = datetime.strptime(date_str, "%m/%d/%Y").date()
                        notif_date = datetime.strptime(notif_str, "%m/%d/%Y").date()
                    except ValueError:
                        logging.warning(f"Invalid date format in trade: {trade}")
                        continue

                    # Perform insertion
                    cursor.execute(
                        """
                        INSERT INTO trades (
                            rep_id, owner, asset_name, transaction_type,
                            transaction_date, notification_date, amount_range
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            rep_id,
                            trade['owner'],
                            trade['asset'],
                            trade['transaction_type'],
                            trans_date,
                            notif_date,
                            trade['amount']
                        )
                    )
                db.commit()
                logging.info(f"Loaded trades from {filename} for rep_id {rep_id}")

            except mysql.connector.Error as err:
                logging.error(f"DB error ({filename}): {err}")
                db.rollback()
                continue

# CLEANUP: close DB resources
cursor.close()
db.close()
logging.info("All trades loaded successfully.")
print("All trades loaded into the database.")