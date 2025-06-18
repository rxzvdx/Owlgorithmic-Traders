# Author(s):
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment:
#    Senior Project (Summer 2025) - "load_trades.py"
# Last Update:
#    Revised June 18th 2025
# Purpose:
#    Fill db "trades" table with trade info

import os
import mysql.connector  # type: ignore
from pdf_parser import extract_trade_data_from_pdf
from datetime import datetime
import logging

# === SETUP LOGGING ===
log_file_path = os.path.join(os.path.dirname(__file__), 'load_trades.log')
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# === DATABASE CONNECTION ===
db = mysql.connector.connect(
    host='localhost',
    user='owladmin',
    password='securepassword',
    database='owl'
)
cursor = db.cursor()

# BASE DIRECTORY WITH PDF FILES
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "house"))

def normalize_name(name: str) -> str:
    return ' '.join(name.lower().strip().replace(',', '').split())

# LOOP THROUGH ALL FILES
for rep_folder in os.listdir(base_dir):
    rep_path = os.path.join(base_dir, rep_folder)
    if not os.path.isdir(rep_path):
        continue

    for year_folder in os.listdir(rep_path):
        year_path = os.path.join(rep_path, year_folder)
        if not os.path.isdir(year_path):
            continue

        for file in os.listdir(year_path):
            if not file.endswith('.pdf'):
                continue

            pdf_path = os.path.join(year_path, file)
            trades = extract_trade_data_from_pdf(pdf_path)

            if not trades:
                continue

            # Get representative ID
            rep_name = normalize_name(trades[0]['rep_name'])
            state_district = trades[0]['state_district'].strip()

            try:
                cursor.execute(
                    "SELECT rep_id, name FROM representatives WHERE state_district = %s",
                    (state_district,)
                )
                all_reps = cursor.fetchall()

                rep_id = None
                for rep_row in all_reps:
                    db_name = normalize_name(rep_row[1])
                    if rep_name == db_name:
                        rep_id = rep_row[0]
                        break

                if not rep_id:
                    msg = f"Rep not found: {rep_name} ({state_district})"
                    print(msg)
                    logging.warning(msg)
                    continue

                for trade in trades:
                    if not trade['transaction_date'] or not trade['notification_date']:
                        msg = f"Skipping trade with missing date: {trade}"
                        print(msg)
                        logging.warning(msg)
                        continue
                    try:
                        formatted_trans_date = datetime.strptime(trade['transaction_date'], "%m/%d/%Y").date()
                        formatted_notif_date = datetime.strptime(trade['notification_date'], "%m/%d/%Y").date()
                    except ValueError:
                        msg = f"Skipping trade due to bad date format: {trade}"
                        print(msg)
                        logging.warning(msg)
                        continue

                    cursor.execute("""
                        INSERT INTO trades (
                            rep_id, owner, asset_name, transaction_type,
                            transaction_date, notification_date, amount_range
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        rep_id,
                        trade['owner'],
                        trade['asset'],
                        trade['transaction_type'],
                        formatted_trans_date,
                        formatted_notif_date,
                        trade['amount']
                    ))
                db.commit()
                msg = f"Loaded trades from {file}"
                print(msg)
                logging.info(msg)

            except mysql.connector.Error as e:
                msg = f"DB error processing {file} for {rep_name} ({state_district}): {e}"
                print(msg)
                logging.error(msg)
                db.rollback()
                continue

# CLEANUP
cursor.close()
db.close()
print("All trades loaded into the database.")
logging.info("All trades loaded into the database.")
