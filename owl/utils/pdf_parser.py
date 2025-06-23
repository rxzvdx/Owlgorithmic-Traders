"""
Author(s):
    Antonio Rosado
    Kashan Khan
    Imad Khan
    Alexander Schifferle
    Mike Kheang
Assignment:
    Senior Project (Summer 2025) – "pdf_parser.py"
Last Update:
    June 16, 2025
Purpose:
    Extract stock trade information from House of Representatives
    financial disclosure PDFs and provide helper routines for testing.
"""

import os
import re

import fitz              # PyMuPDF: fast PDF text extraction (`pip install PyMuPDF`)
from PyPDF2 import PdfReader  # Alternative PDF text extractor
                          
# Regular expression to match standard trade‐info rows in extracted text
trade_pattern = re.compile(
    r"(Self|Spouse)"                             # Group 1: Owner
    r"\s+"                                       # whitespace
    r"([\w\s().,&-]+?)"                          # Group 2: Asset name (non-greedy)
    r"\s+"                                       # whitespace
    r"(P|S|E)"                                   # Group 3: Transaction type code
    r"\s+"                                       # whitespace
    r"(\d{1,2}/\d{1,2}/\d{4})"                   # Group 4: Transaction date
    r"\s+"                                       # whitespace
    r"(\d{1,2}/\d{1,2}/\d{4})"                   # Group 5: Notification date
    r"\s+\$?"                                    # optional dollar sign
    r"([\d,<>.\-]+(?:\s*-\s*\$?[\d,]+)?)"        # Group 6: Amount or range
)

def extract_trade_data_from_pdf(pdf_path: str) -> list:
    """
    Open a PDF, read text from all pages, and extract trade entries.

    Args:
        pdf_path (str): Filesystem path to a disclosure PDF.

    Returns:
        List[dict]: One dict per matched trade block, containing:
            - rep_name
            - state_district
            - owner
            - asset
            - transaction_type
            - transaction_date
            - notification_date
            - amount
    """
    # Read all text from PDF via PyMuPDF
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    # Extract representative name and district from header fields
    name_match = re.search(r"Name:\s+Hon\.\s+(.*?)\n", full_text, re.IGNORECASE)
    district_match = re.search(r"State/District:\s+(.*?)\n", full_text)
    rep_name = name_match.group(1).strip() if name_match else None
    state_district = district_match.group(1).strip() if district_match else None

    # Split into non-empty lines for easier scanning
    lines = [ln.strip() for ln in full_text.split("\n") if ln.strip()]
    trades = []
    i = 0

    # Iterate lines, looking for blocks that resemble a trade entry
    while i < len(lines):
        line = lines[i]
        # Example marker: asset line ends with "[ST]" or similar tag
        if re.match(r".+\[ST\]$", line):
            try:
                asset = line
                trans_type = lines[i + 1]              # Next line is type code
                date_parts = lines[i + 2].split()      # Next line has two dates
                trans_date = date_parts[0] if date_parts else None
                notif_date = date_parts[1] if len(date_parts) > 1 else None
                amount_line = lines[i + 3]             # Next line has amount details

                trades.append({
                    "rep_name": rep_name,
                    "state_district": state_district,
                    "owner": None,                     # Owner detection to be added
                    "asset": asset,
                    "transaction_type": trans_type,
                    "transaction_date": trans_date,
                    "notification_date": notif_date,
                    "amount": amount_line.replace(",", "")
                })
                # Advance past this block (4 lines + header)
                i += 5
                continue
            except IndexError:
                # Incomplete block at end of document
                break
        i += 1

    return trades

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Read and return the raw text of a PDF using PyPDF2.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Aggregated text of all pages.
    """
    reader = PdfReader(pdf_path)
    text_out = ""
    for page in reader.pages:
        text_out += page.extract_text() or ""
    return text_out

def parse_pdf_for_debug(pdf_path: str):
    """
    Run a quick debug extraction: print file existence, run regex
    on raw text, and display matches to the console.

    Args:
        pdf_path (str): Path to the PDF file being tested.
    """
    print(f"\nTesting PDF path: {pdf_path}")
    print("Exists:", os.path.exists(pdf_path))

    text = extract_text_from_pdf(pdf_path)
    matches = trade_pattern.findall(text)
    if not matches:
        print("\nNo trades found. Verify regex or sample PDF.\n")
        return

    print("\n--- MATCHED TRADE DATA ---")
    for owner, asset, typ, tdate, ndate, amt in matches:
        print(f"Owner: {owner}")
        print(f"Asset: {asset}")
        print(f"Type code: {typ}")
        print(f"Trans date: {tdate}")
        print(f"Notif date: {ndate}")
        print(f"Amount: {amt}")
        print("-" * 40)

# -------------------------------------------------------------------------
# Added function for consistency with upstream orchestrator:
# -------------------------------------------------------------------------
def parse_transactions(pdf_path: str) -> list:
    """
    Alias for extract_trade_data_from_pdf so upstream code just
    needs to call `parse_transactions`.
    """
    return extract_trade_data_from_pdf(pdf_path)
