# Author(s): 
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment: 
#    Senior Project (Summer 2025) - "app"
# Last Update: 
#    June 8 2025
# Purpose: 
#    This script initializes the Flask app.

# ─── Standard Library Imports ────────────────────────────────────────────
import os
import glob
import json
from datetime import datetime, timedelta
from functools import lru_cache
import xml.etree.ElementTree as ET

# ─── Environment Configuration ───────────────────────────────────────────
# Allow HTTP for local testing of OAuth
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# ─── Third-Party Package Imports ─────────────────────────────────────────
import yfinance as yf
import pandas as pd

# ─── Flask Framework Imports ─────────────────────────────────────────────
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_file, send_from_directory,
    current_app, after_this_request
)

# ─── Flask-Dance (Google OAuth) Imports ──────────────────────────────────
from flask_dance.contrib.google import google
from flask_dance.consumer import oauth_authorized

# ─── OAuth Library Imports ───────────────────────────────────────────────
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

# ─── Custom Utility Imports ──────────────────────────────────────────────
from utils.downloader import download_and_extract_disclosures
from utils.login import google_blueprint
from utils.desktop_notifs import notify_user  # type: ignore

# ─── Report Lab Imports ──────────────────────────────────
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    current_user, logout_user
)
from flask import send_file

# Initilize Flask app
app = Flask(__name__)
# ── Flask-Login setup ──
login_manager = LoginManager()
login_manager.login_view = "google.login"
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id: str, email: str, name: str):
        self.id = id
        self.email = email
        self.name = name

# In-memory user store (replace with DB in production)
user_store: dict[str, User] = {}

@login_manager.user_loader
def load_user(user_id: str):
    return user_store.get(user_id)

app.secret_key = "supersecretkey"

# Register the Google OAuth blueprint under url_prefix
app.register_blueprint(google_blueprint, url_prefix="/login")

# ------ MAIN LANDING PAGE ROUTE -----
# Home page route
@app.route('/')
def index():
    user_email = None
    if google.authorized:
        try:
            resp = google.get('/oauth2/v1/userinfo')
            if resp.ok:
                user_email = resp.json().get('email')
        except TokenExpiredError:
            # OAuth token expired, redirect to login again
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("google.login"))
    return render_template('index.html', user_email=user_email, google=google)

# ─── helper to fetch today’s price + % change ─────────────────────────────────
def fetch_stock_data(symbols):
    data = {}
    for sym in symbols:
        try:
            # normalize BRK.B
            yf_sym = 'BRK-B' if sym.upper() == 'BRK.B' else sym
            t = yf.Ticker(yf_sym)
            hist = t.history(period="1d")
            if hist.empty:
                continue
            today = hist.iloc[-1]
            close = today["Close"]
            openp = today.get("Open", close)
            pct   = (close - openp) / openp * 100 if openp else 0
            data[sym] = {"price": close, "change": pct}
        except Exception:
            continue
    return data

# ------ OAUTH ROUTE -----
# Callback route for Google OAuth
@app.route('/auth')
def login():
    if not google.authorized:
        return redirect(url_for('google.login'))

    resp = google.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Failed to fetch your Google profile.", "error")
        return redirect(url_for("index"))

    info  = resp.json()
    email = info["email"]

    user = user_store.get(email)
    if not user:
        user = User(id=email, email=email, name=info.get("name", ""))
        user_store[email] = user

    login_user(user)
    flash(f"Signed in as {email}", "success")
    return redirect(url_for("index"))


# ------ DOWNLOAD ROUTE -----
# Download routes will only work if the user is logged in
@app.route('/download', methods=['POST'])
def download():
    if not google.authorized:
        flash("Please log in to download disclosures.", "error")
        return redirect(url_for('index'))

    year = request.form['year']
    file_buffer, message = download_and_extract_disclosures(year)
    
    if file_buffer is None:
        flash(message, 'error')
        return redirect(url_for('index'))
    
    try:
        return send_file(
            file_buffer,
            as_attachment=True,
            download_name=message,
            mimetype='application/zip'
        )
    except Exception as e:
        flash(f"Download failed: {str(e)}", 'error')
        return redirect(url_for('index'))

# ------ STOCK CHART VIEW ROUTE -----
@app.route('/chart_view')
def chart_list():
    stocks = [
        'AAPL', 'TSLA', 'GOOGL', 'AMZN', 'MSFT',
        'NASDAQ:IXIC', 'INDEX:SPX', 'INDEX:DJI'
    ]
    return render_template('chart_list.html', stocks=stocks, google=google)

@app.route('/chart_view/<symbol>')
def view_chart(symbol):
    symbol = symbol.replace('__', ':')
    display_symbol = symbol.upper()

    # Fetch stock details
    stock = yf.Ticker(symbol)
    info = stock.info

    # Prepare company overview
    overview = {
        'name': info.get('longName', display_symbol),
        'sector': info.get('sector', 'N/A'),
        'industry': info.get('industry', 'N/A'),
        'marketCap': info.get('marketCap', 'N/A'),
        'peRatio': info.get('trailingPE', 'N/A'),
        'dividendYield': info.get('dividendYield', 'N/A'),
        '52WeekHigh': info.get('fiftyTwoWeekHigh', 'N/A'),
        '52WeekLow': info.get('fiftyTwoWeekLow', 'N/A'),
        'website': info.get('website', '#')
    }

    description = stock_info.get(display_symbol, "This chart shows real-time trading activity and price movement for the selected stock or index.")

    return render_template('chart_view.html', symbol=display_symbol, description=description, overview=overview, google=google)

# ------ FAVORITES ROUTE -----
@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    symbol = request.form.get('symbol')
    if 'favorites' not in session:
        session['favorites'] = []
    if symbol and symbol not in session['favorites']:
        session['favorites'].append(symbol)
        session.modified = True
    return redirect(url_for('view_chart', symbol=symbol))

@app.route('/favorites')
def favorites():
    favorites_list = session.get('favorites', [])
    reps_list = session.get('favorite_reps', [])  # Add this
    return render_template('favorites.html', favorites=favorites_list, favorite_reps=reps_list)

@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    symbol = request.form.get('symbol')
    if 'favorites' not in session:
        session['favorites'] = []

    if symbol in session['favorites']:
        session['favorites'].remove(symbol)
    else:
        session['favorites'].append(symbol)

    session.modified = True
    return redirect(url_for('view_chart', symbol=symbol))

@app.route('/toggle_rep_favorite', methods=['POST'])
def toggle_rep_favorite():
    rep_name = request.form.get('rep_name')
    if 'favorite_reps' not in session:
        session['favorite_reps'] = []

    if rep_name in session['favorite_reps']:
        session['favorite_reps'].remove(rep_name)
    else:
        session['favorite_reps'].append(rep_name)

    session.modified = True
    return redirect(request.referrer or url_for('favorites'))

# ------ STOCK CHART ROUTE -----
# Global stock information dictionary
stock_info = {
    'AAPL': 'Apple Inc. is a technology company known for the iPhone, Mac, and innovative hardware and software.',
    'MSFT': 'Microsoft Corporation is a global leader in software, cloud computing, and enterprise technology solutions.',
    'NVDA': 'Nvidia Corporation designs GPUs for gaming and AI computing, and plays a key role in data center innovation.',
    'AMZN': 'Amazon.com Inc. dominates e-commerce and cloud services globally through AWS.',
    'GOOGL': 'Alphabet Inc. is the parent company of Google, focused on search, ads, cloud, and AI.',
    'META': 'Meta Platforms Inc. operates Facebook, Instagram, and develops AR/VR platforms like Meta Quest.',
    'TSLA': 'Tesla Inc. designs and manufactures electric vehicles and clean energy products.',
    'BRK.B': 'Berkshire Hathaway is a diversified holding company led by Warren Buffett.',
    'UNH': 'UnitedHealth Group provides healthcare benefits and services across the U.S.',
    'JNJ': 'Johnson & Johnson develops pharmaceuticals, medical devices, and consumer health products.',
    'V': 'Visa Inc. is a global payments technology company enabling digital payments worldwide.',
    'PG': 'Procter & Gamble produces consumer goods including hygiene, beauty, and health products.',
    'JPM': 'JPMorgan Chase is the largest U.S. bank, offering financial and investment services.',
    'HD': 'The Home Depot is the largest home improvement retailer in the U.S.',
    'MA': 'Mastercard is a global payments company offering transaction processing and security.',
    'XOM': 'Exxon Mobil Corporation is a major oil and gas company with global operations.',
    'PFE': 'Pfizer Inc. is a leading pharmaceutical company known for vaccines and therapies.',
    'KO': 'The Coca-Cola Company produces non-alcoholic beverages including Coca-Cola and other brands.',
    'PEP': 'PepsiCo Inc. is a global food and beverage company known for Pepsi, Frito-Lay, and more.',
    'BAC': 'Bank of America offers banking and financial services to individuals and businesses.',
    'CSCO': 'Cisco Systems Inc. is a networking hardware and cybersecurity company.',
    'DIS': 'The Walt Disney Company operates in media, entertainment, and theme parks.',
    'CMCSA': 'Comcast Corporation provides cable, broadband, and owns NBCUniversal.',
    'VZ': 'Verizon Communications Inc. is a major telecom provider in the U.S.',
    'ADBE': 'Adobe Inc. develops creative and marketing software such as Photoshop and Acrobat.',
    'NFLX': 'Netflix Inc. is a global streaming content platform producing original films and series.',
    'INTC': 'Intel Corporation manufactures semiconductors and processors for computers and servers.',
    'T': 'AT&T Inc. provides wireless, broadband, and media services.',
    'WMT': 'Walmart Inc. is the largest global retailer by revenue, operating supercenters and e-commerce.',
    'MRK': 'Merck & Co. is a pharmaceutical company focused on vaccines and oncology.',
    'ABT': 'Abbott Laboratories develops diagnostics, medical devices, and nutritional products.',
    'CRM': 'Salesforce Inc. is a leading cloud software company for customer relationship management.',
    'NKE': 'Nike Inc. designs, markets, and sells athletic apparel, footwear, and equipment.',
    'ORCL': 'Oracle Corporation provides database software and cloud computing infrastructure.',
    'COST': 'Costco Wholesale is a membership-based warehouse club with global operations.',
    'MCD': "McDonald's Corporation is the largest fast-food chain in the world by revenue.",
    'LLY': 'Eli Lilly and Company is a pharmaceutical company known for diabetes and cancer therapies.',
    'DHR': 'Danaher Corporation designs and manufactures medical and industrial tools and technology.',
    'MDT': 'Medtronic plc is a medical technology company specializing in devices and therapies.',
    'BMY': 'Bristol-Myers Squibb is a pharmaceutical company focused on oncology and immunology.',
    'TMO': 'Thermo Fisher Scientific provides laboratory instruments and services to the life sciences.',
    'NEE': 'NextEra Energy Inc. is a major U.S. energy company focusing on renewables.',
    'UPS': 'United Parcel Service is a logistics and package delivery company.',
    'PM': 'Philip Morris International manufactures and sells tobacco products worldwide.',
    'CVX': 'Chevron Corporation is a global oil and gas company involved in exploration and production.',
    'QCOM': 'Qualcomm Inc. creates semiconductors and wireless technologies for mobile devices.',
    'TXN': 'Texas Instruments designs semiconductors for industrial, automotive, and consumer electronics.',
    'UNP': 'Union Pacific operates one of the largest freight rail networks in the U.S.',
    'LIN': 'Linde plc is a multinational industrial gas and engineering company.',
    'AVGO': 'Broadcom Inc. is a semiconductor and infrastructure software company.'
}

# Add this after the stock_info dictionary
# Cache for stock data
stock_cache = {}
CACHE_DURATION = timedelta(minutes=5)

@app.route('/api/stock/<symbol>')
def stock_api(symbol):
    try:
        # Normalize symbol for yfinance
        if symbol.upper() == 'BRK.B':
            yf_symbol = 'BRK-B'
        else:
            yf_symbol = symbol
        # Check cache first
        current_time = datetime.now()
        if symbol in stock_cache:
            cached_data, cache_time = stock_cache[symbol]
            if current_time - cache_time < CACHE_DURATION:
                return jsonify(cached_data)

        # If not in cache or cache expired, fetch new data
        stock = yf.Ticker(yf_symbol)
        info = stock.info
        
        # Get the current price and previous close
        current_price = info.get('regularMarketPrice', 0)
        previous_close = info.get('regularMarketPreviousClose', current_price)
        
        # Calculate the percentage change
        if previous_close and previous_close != 0:
            change = ((current_price - previous_close) / previous_close) * 100
        else:
            change = 0
            
        data = {
            'symbol': symbol,
            'price': current_price,
            'change': change
        }
        
        # Update cache
        stock_cache[symbol] = (data, current_time)
            
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------ CONTACT PAGE ROUTE -----
@app.route('/contact')
def contact():
    return render_template('contact.html', google=google)

def get_stock_company_name(ticker):
    """Get company name from stock ticker using the stock_info dictionary"""
    return stock_info.get(ticker.upper(), f"{ticker.upper()} Corporation")

# ------ REP/PROFILE ROUTE -----
@app.route('/politician/<name>')
def politician_profile(name):
    # Decode the URL-encoded name
    politician_name = name.replace('+', ' ')
    print(f"Looking for politician: {politician_name}")
    
    # Initialize data structures
    filings = []
    transactions = []
    stock_holdings = {}
    detailed_trades = []  # NEW: for trades_cache.json
    
    # Process data from all years
    base_path = os.path.join(os.path.dirname(__file__), 'raw_data')
    
    # --- Load detailed trades from trades_cache.json ---
    trades_cache_path = os.path.join(os.path.dirname(__file__), '..', 'term_logs', 'trades_cache.json')
    try:
        import json
        with open(trades_cache_path, 'r', encoding='utf-8') as f:
            trades_data = json.load(f)
        # Try exact match, fallback to partial match
        if politician_name in trades_data:
            detailed_trades = trades_data[politician_name].get('transactions', [])
        else:
            # Fuzzy match: ignore underscores, spaces, and case, and require all name parts to be present
            def normalize(s):
                return s.replace('_', ' ').replace('.', '').lower()
            norm_name_parts = [part for part in normalize(politician_name).split() if part]
            best_key = None
            for key in trades_data:
                norm_key = normalize(key)
                if all(part in norm_key for part in norm_name_parts):
                    best_key = key
                    break
            if best_key:
                detailed_trades = trades_data[best_key].get('transactions', [])
    except Exception as e:
        detailed_trades = []
    
    if not os.path.exists(base_path):
        print("raw_data directory not found")
        return render_template("politician_profile.html", 
                             politician={'name': politician_name, 'state_district': 'N/A'},
                             stats={'total_filings': 0, 'years_active': 0, 'total_transactions': 0, 'unique_stocks': 0},
                             filings=[], transactions=[], stock_holdings=[], detailed_trades=[], google=google)
    
    # Process .txt files for filing information
    for year_folder in os.listdir(base_path):
        year_path = os.path.join(base_path, year_folder)
        if not os.path.isdir(year_path):
            continue
            
        year = year_folder.replace('_data', '')
        print(f"Processing year: {year}")
        
        # Look for .txt files first
        txt_files = [f for f in os.listdir(year_path) if f.endswith('.txt')]
        for txt_file in txt_files:
            txt_path = os.path.join(year_path, txt_file)
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        parts = line.strip().split('\t')
                        if len(parts) >= 9:  # Need at least 9 columns
                            # Check if this line matches our politician
                            first = parts[2] if len(parts) > 2 else ''  # Column 2 is First name
                            last = parts[1] if len(parts) > 1 else ''   # Column 1 is Last name
                            current_name = f"{first} {last}".strip()
                            
                            # More flexible name matching
                            if (current_name.lower() == politician_name.lower() or 
                                politician_name.lower() in current_name.lower() or
                                current_name.lower() in politician_name.lower()):
                                print(f"Found match: {current_name} in {txt_file}")
                                filings.append({
                                    'year': parts[6] if len(parts) > 6 else year,  # Column 6 is Year
                                    'filing_type': parts[4] if len(parts) > 4 else 'N/A',  # Column 4 is FilingType
                                    'date': parts[7] if len(parts) > 7 else 'N/A',  # Column 7 is FilingDate
                                    'doc_id': parts[8] if len(parts) > 8 else 'N/A',  # Column 8 is DocID
                                    'state_district': parts[5] if len(parts) > 5 else 'N/A'  # Column 5 is StateDst
                                })
            except Exception as e:
                print(f"Error processing {txt_path}: {e}")
                continue
    
    print(f"Found {len(filings)} filings")
    
    # Process .xml files for transaction details
    for year_folder in os.listdir(base_path):
        year_path = os.path.join(base_path, year_folder)
        if not os.path.isdir(year_path):
            continue
            
        xml_files = [f for f in os.listdir(year_path) if f.endswith('.xml')]
        for xml_file in xml_files:
            xml_path = os.path.join(year_path, xml_file)
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                
                # Check if this XML file contains data for our politician
                member_elements = root.findall('Member')
                for member in member_elements:
                    first = member.findtext('First', default='')
                    last = member.findtext('Last', default='')
                    current_name = f"{first} {last}".strip()
                    
                    # More flexible name matching
                    if (current_name.lower() == politician_name.lower() or 
                        politician_name.lower() in current_name.lower() or
                        current_name.lower() in politician_name.lower()):
                        print(f"Found XML match: {current_name} in {xml_file}")
                        # Get transaction information
                        txn_info = root.find("TransactionInformation")
                        if txn_info is not None:
                            for txn in txn_info.findall("Transaction"):
                                ticker = txn.findtext('Ticker', default='N/A')
                                transaction_data = {
                                    'date': txn.findtext('TransactionDate', default='N/A'),
                                    'ticker': ticker,
                                    'type': txn.findtext('Type', default='N/A'),
                                    'owner': txn.findtext('Owner', default='N/A'),
                                    'amount': txn.findtext('Amount', default='N/A'),
                                    'description': txn.findtext('AssetDescription', default='N/A')
                                }
                                transactions.append(transaction_data)
                                
                                # Track stock holdings
                                if ticker != 'N/A':
                                    if ticker not in stock_holdings:
                                        stock_holdings[ticker] = {
                                            'count': 0,
                                            'last_date': transaction_data['date'],
                                            'company_name': get_stock_company_name(ticker)
                                        }
                                    stock_holdings[ticker]['count'] += 1
                                    if transaction_data['date'] > stock_holdings[ticker]['last_date']:
                                        stock_holdings[ticker]['last_date'] = transaction_data['date']
                                        
            except ET.ParseError:
                print(f"Failed to parse XML: {xml_path}")
                continue
            except Exception as e:
                print(f"Error processing {xml_path}: {e}")
                continue
    
    print(f"Found {len(transactions)} transactions")
    print(f"Found {len(stock_holdings)} unique stocks")
    
    # Calculate statistics
    years_active = len(set(filing['year'] for filing in filings))
    unique_stocks = len(stock_holdings)
    
    # Convert stock_holdings dict to list for template
    stock_holdings_list = [
        {
            'ticker': ticker,
            'company_name': data['company_name'],
            'count': data['count'],
            'last_date': data['last_date']
        }
        for ticker, data in stock_holdings.items()
    ]
    
    # Sort by transaction count
    stock_holdings_list.sort(key=lambda x: x['count'], reverse=True)
    
    # Get state/district from first filing
    state_district = 'N/A'
    if filings:
        # Get state/district from the first filing that has it
        for filing in filings:
            if filing.get('state_district') and filing['state_district'] != 'N/A':
                state_district = filing['state_district']
                break
    
    stats = {
        'total_filings': len(filings),
        'years_active': years_active,
        'total_transactions': len(transactions),
        'unique_stocks': unique_stocks
    }
    
    politician = {
        'name': politician_name,
        'state_district': state_district
    }
    
    print(f"Final stats: {stats}")
    
    return render_template("politician_profile.html", 
                         politician=politician,
                         stats=stats,
                         filings=filings,
                         transactions=transactions,
                         stock_holdings=stock_holdings_list,
                         detailed_trades=detailed_trades,
                         google=google)

# ------ DASHBOARD ROUTE -----
@app.route('/dashboard')
def dashboard():
    base_path = os.path.join(os.path.dirname(__file__), 'raw_data')
    disclosures = []

    if not os.path.exists(base_path):
        print("raw_data not found")
        return render_template("dashboard.html", disclosures=[], google=google)

    for year_folder in os.listdir(base_path):
        year_path = os.path.join(base_path, year_folder)
        if not os.path.isdir(year_path):
            continue

        for file in os.listdir(year_path):
            if file.endswith('.xml'):
                file_path = os.path.join(year_path, file)
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    transactions = root.find("TransactionInformation")
                    if transactions is None:
                        continue

                    for txn in transactions.findall("Transaction"):
                        disclosures.append({
                            'year': year_folder.replace('_data', ''),
                            'file': file,
                            'date': txn.findtext('TransactionDate', default='N/A'),
                            'ticker': txn.findtext('Ticker', default='N/A'),
                            'owner': txn.findtext('Owner', default='N/A'),
                            'type': txn.findtext('Type', default='N/A'),
                            'desc': txn.findtext('AssetDescription', default='N/A'),
                            'amount': txn.findtext('Amount', default='N/A')
                        })
                except ET.ParseError:
                    print(f"Failed to parse XML: {file_path}")
                    continue

    return render_template("dashboard.html", disclosures=disclosures, google=google)

@app.route('/api/disclosures')
def disclosures_api():
    # This path is correct based on your screenshot
    raw_data_dir = os.path.join(os.path.dirname(__file__), 'raw_data')

    data = []

    for year_folder in os.listdir(raw_data_dir):
        folder_path = os.path.join(raw_data_dir, year_folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith('.xml'):
                    xml_path = os.path.join(folder_path, file)
                    print(f"Processing: {xml_path}")

                    try:
                        tree = ET.parse(xml_path)
                        root = tree.getroot()

                        for member in root.findall('Member'):
                            name = f"{member.findtext('First', default='')} {member.findtext('Last', default='')}".strip()
                            state = member.findtext('StateDst', default='N/A')
                            filing_type = member.findtext('FilingType', default='N/A')
                            date = member.findtext('FilingDate', default='N/A')
                            year = member.findtext('Year', default=year_folder.split('_')[0])

                            data.append({
                                'name': name,
                                'state': state,
                                'type': filing_type,
                                'date': date,
                                'year': year
                            })
                    except Exception as e:
                        print(f"Error processing {xml_path}: {e}")

    if not data:
        return {'error': 'No disclosures found'}, 404

    return jsonify(data)

# ------ DISCLOSURE PROCESSING ROUTE -----
@app.route('/disclosures')
def disclosures_page():
    user_email = None
    if google.authorized:
        try:
            resp = google.get('/oauth2/v1/userinfo')
            if resp.ok:
                user_email = resp.json().get('email')
        except TokenExpiredError:
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("google.login"))

    return render_template('disclosures.html', user_email=user_email, google=google)

from flask import send_from_directory

@app.route('/disclosures/<year_folder>/<filename>')
def serve_disclosure(year_folder, filename):
    folder_path = os.path.join(os.path.dirname(__file__), 'raw_data', year_folder)
    return send_from_directory(folder_path, filename)

# ------ PROPER FLASK FLOW -----
@app.context_processor
def inject_google():
    return dict(google=google)

# ------ DESKTOP NOTIFICATION ROUTE -----
# dummy user lookup function, will replace later
class MockUser:
    def __init__(self, email):
        self.email = email
        self.opt_in = True
        self.first_name = "John"

def get_user_by_email(email):
    # in prod, will fetch from db
    return MockUser(email or "default@example.com")

@app.route('/create_plan', methods=['POST'])
def create_plan():
    if not google.authorized:
        flash("Please log in to create your plan.", "error")
        return redirect(url_for("index"))
    
    # placeholder for user info from db
    user = get_user_by_email(session.get('email')) # type: ignore
    
    # personalized plan logic here
    # (e.g., fetch user preferences, generate a report, etc.)
    
    # notify user only if they are opted in
    if user.opt_in:
        notify_user(
            title="Your personalized plan is ready!",
            message=f"{user.first_name}, your personalized investment plan has been created. Check your dashboard for a full view!"
        )
    flash("Your plan was created successfully.", "success")
    return redirect(url_for("dashboard"))

@app.route('/favorites/pdf')
@login_required
def favorites_pdf():
    # 1) load both lists from the session
    favorites       = session.get('favorites', [])
    favorite_reps   = session.get('favorite_reps', [])

    # 2) build the PDF in memory
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=(8.5 * 72, 11 * 72))
    styles = getSampleStyleSheet()
    story  = []

    # Title
    story.append(Paragraph(f"{current_user.name}'s Favorites", styles['Title']))
    story.append(Spacer(1, 12))

    # ─── Favorite Stocks ────────────────────────────────────────────────────────
    story.append(Paragraph("Favorite Stocks", styles['Heading2']))
    story.append(Spacer(1, 6))
    stock_data = [["Symbol"]]
    for symbol in favorites:
        stock_data.append([symbol])

    stock_tbl = Table(stock_data)
    stock_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR',   (0, 0), (-1, 0), colors.black),
        ('GRID',        (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',       (0, 0), (-1, 0), 'CENTER'),
    ]))
    story.append(stock_tbl)

    # ─── Favorite Representatives ──────────────────────────────────────────────
    if favorite_reps:
        story.append(Spacer(1, 12))
        story.append(Paragraph("Favorite Representatives", styles['Heading2']))
        story.append(Spacer(1, 6))

        rep_data = [["Representative"]]
        for rep in favorite_reps:
            rep_data.append([rep])

        rep_tbl = Table(rep_data)
        rep_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR',   (0, 0), (-1, 0), colors.black),
            ('GRID',        (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN',       (0, 0), (-1, 0), 'CENTER'),
        ]))
        story.append(rep_tbl)

    # 3) finalize and send
    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"favorites_{current_user.id}.pdf",
        mimetype='application/pdf'
    )


@app.route('/recommendations/pdf')
@login_required
def recommendations_pdf():
    favs = session.get('favorites', [])
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=(8.5*72, 11*72))
    styles = getSampleStyleSheet()
    story  = [
        Paragraph(f"{current_user.name}'s Stock Recommendations", styles["Title"]),
        Spacer(1,12)
    ]

    # Table header: include SMAs
    rows = [["Symbol","Price","20d SMA","50d SMA","Recommendation"]]

    for sym in favs:
        try:
            t    = yf.Ticker(sym)
            hist = t.history(period="60d")      # need ≥50 days
            if len(hist) < 20:
                continue

            close = hist["Close"].iloc[-1]
            sma20 = hist["Close"].iloc[-20:].mean()
            sma50 = hist["Close"].iloc[-50:].mean() if len(hist) >= 50 else None

            # simple crossover rule
            if sma50 and sma20 > sma50:
                rec = "Buy"
            else:
                rec = "Hold"

            rows.append([
                sym,
                f"${close:.2f}",
                f"${sma20:.2f}",
                f"${sma50:.2f}" if sma50 else "n/a",
                rec
            ])
        except Exception:
            rows.append([sym, "error", "error", "error", "n/a"])

    tbl = Table(rows, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("GRID",       (0,0),(-1,-1),0.5,colors.grey),
        ("FONTNAME",   (0,0),(-1,0),"Helvetica-Bold"),
        ("ALIGN",      (1,1),(-1,-1),"CENTER"),
    ]))
    story.append(tbl)

    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"recommendations_{current_user.id}.pdf",
        mimetype="application/pdf"
    )

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

# ------ MAIN -----
if __name__ == '__main__':
    app.run(debug=True)