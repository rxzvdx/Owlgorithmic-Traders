# Author(s): 
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment: 
#    Senior Project (Summer 2025) - "pdf_parser"
# Last Update: 
#    June 16th 2025
# Purpose: 
#    Extract stock trade information from House of Representatives financial disclosure PDFs

import fitz  # pip install PyMuPDF
from PyPDF2 import PdfReader
import re
import os

# Extract transaction rows
# This assumes one or more rows using consistent formatting
trade_pattern = re.compile(
    r"(Self|Spouse)"                             # Group 1: Owner — either "Self" or "Spouse"
    r"\s+"                                       # One or more spaces
    r"([\w\s().,&-]+?)"                          # Group 2: Asset — letters, numbers, spaces, or common punctuation (non-greedy)
    r"\s+"                                       # One or more spaces
    r"(P|S|E)"                                   # Group 3: Transaction Type — P = Purchase, S = Sale, E = Exchange
    r"\s+"                                       # One or more spaces
    r"(\d{1,2}/\d{1,2}/\d{4})"                   # Group 4: Transaction Date — format like 12/8/2020
    r"\s+"                                       # One or more spaces
    r"(\d{1,2}/\d{1,2}/\d{4})"                   # Group 5: Notification Date — same date format
    r"\s+\$?"                                    # Dollar sign (optional) preceded by one or more spaces
    r"([\d,<>.\-]+(?:\s*-\s*\$?[\d,]+)?)"        # Group 6: Amount — e.g. "$1,001 - $15,000" or "<$1,000"
)

def extract_trade_data_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    # Extract rep name and district
    name_match = re.search(r"Name:\s+Hon\.\s+(.*?)\n", text, re.IGNORECASE)
    district_match = re.search(r"State/District:\s+(.*?)\n", text)
    rep_name = name_match.group(1).strip() if name_match else None
    state_district = district_match.group(1).strip() if district_match else None

    # Capture trades line-by-line
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    trades = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Try to identify a trade block by looking for asset name followed by expected data
        if re.match(r".+\[ST\]$", line):  # Example: Kroger Company (KR) [ST]
            try:
                asset = line
                trans_type = lines[i + 1]

                # Transaction date and notification date are on the same line
                date_line = lines[i + 2]
                dates = date_line.split()
                trans_date = dates[0] if len(dates) > 0 else None
                notif_date = dates[1] if len(dates) > 1 else None

                amount_line = lines[i + 3]
                amount = amount_line.replace(",", "")


                trades.append({
                    "rep_name": rep_name,
                    "state_district": state_district,
                    "owner": None,  
                    "asset": asset,
                    "transaction_type": trans_type,
                    "transaction_date": trans_date,
                    "notification_date": notif_date,
                    "amount": amount.replace(",", ""),
                })

                i += 5  # Skip to next potential block
                continue
            except IndexError:
                pass  # Incomplete block, skip

        i += 1  # Go to next line

    return trades

# TESTING/DEBUGGING
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def parse_pdf(pdf_path):
    print(f"\nTesting PDF path: {pdf_path}")
    print(f"File exists? {os.path.exists(pdf_path)}\n")

    text = extract_text_from_pdf(pdf_path)
    matches = trade_pattern.findall(text)

    if not matches:
        print("\nNo trades found in this document. Try another or verify regex.\n")
        return

    print("\n--- MATCHED TRADE DATA ---")
    for match in matches:
        owner, asset, trans_type, trans_date, notif_date, amount = match
        print(f"Owner: {owner}")
        print(f"Asset: {asset}")
        print(f"Transaction Type: {trans_type}")
        print(f"Transaction Date: {trans_date}")
        print(f"Notification Date: {notif_date}")
        print(f"Amount: {amount}")
        print("-" * 40)

# TEST RUN
if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'House'))
    test_pdf_path = os.path.join(base_dir, 'Banks_James E Hon', '2021', '20018018.pdf')

    # DEBUGGING: Confirm file path and existence
    print("Testing PDF path:", test_pdf_path)
    print("File exists?", os.path.exists(test_pdf_path))

    if not os.path.exists(test_pdf_path):
        print("ERROR: PDF not found.")
    else:
        # Call main extraction logic
        trades = extract_trade_data_from_pdf(test_pdf_path)

        if not trades:
            print("\nNo trades found in this document. Try another or verify regex.\n")
        else:
            print(f"\nExtracted {len(trades)} trade(s):\n")
            for trade in trades:
                print(trade)
