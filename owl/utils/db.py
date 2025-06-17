# Author(s): 
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment: 
#    Senior Project (Summer 2025) - "db.py"
# Last Update: 
#    June 16th 2025
# Purpose: 
#    Fill db with info (user info, rep info, trade info)

import os
import mysql.connector # type: ignore
from pdf_parser import extract_trade_data_from_pdf
from datetime import datetime

# === DATABASE CONNECTION ===
db = mysql.connector.connect(
    host='localhost',
    user='owladmin',
    password='securepassword',
    database='owl'
)
cursor = db.cursor()

# BASE DIRECTORY WITH PDF FILES 
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",'..', 'house'))

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

            # Insert representative if not already there
            rep_name = trades[0]['rep_name']
            state_district = trades[0]['state_district']
            cursor.execute("SELECT rep_id FROM representatives WHERE name=%s AND state_district=%s", (rep_name, state_district))
            result = cursor.fetchone()

            if result:
                rep_id = result[0]
            else:
                cursor.execute("INSERT INTO representatives (name, state_district) VALUES (%s, %s)", (rep_name, state_district))
                db.commit()
                rep_id = cursor.lastrowid

            # Insert all trades
            for trade in trades:
                if not trade['transaction_date'] or not trade['notification_date']:
                    print(f"Skipping trade with missing date: {trade}")
                    continue
                try:
                    formatted_trans_date = datetime.strptime(trade['transaction_date'], "%m/%d/%Y").date()
                    formatted_notif_date = datetime.strptime(trade['notification_date'], "%m/%d/%Y").date()
                except ValueError:
                    print(f"Skipping trade due to bad date format: {trade}")
                    continue

                cursor.execute("""
                    INSERT INTO trades (rep_id, owner, asset_name, transaction_type, transaction_date, notification_date, amount_range)
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
            print(f"Loaded trades from {file}")

# CLEANUP 
cursor.close()
db.close()
print("All trades loaded into the database.")

