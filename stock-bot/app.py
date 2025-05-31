import os
import yfinance as yf
import json
from flask import render_template


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP for local testing

# Flask framework imports
from flask import session, Flask, render_template, request, redirect, url_for, flash, current_app, after_this_request, send_file

# Custom Utilities
from utils.downloader import download_and_extract_disclosures
from utils.login import google_blueprint

# Flask-Dance imports
from flask_dance.contrib.google import google
from flask_dance.consumer import oauth_authorized

#OAuth imports
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

# Parsing logic
from flask import Flask, render_template, jsonify
import json 

# Initilize Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Register the Google OAuth blueprint under url_prefix
app.register_blueprint(google_blueprint, url_prefix="/login")

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

# Login route intiates the Google OAuth process
@app.route('/auth')
def login():
    session["after_login"] = True  # Temp flag to indicate that the user is trying to log in(for testing)
    if not google.authorized:
        return redirect(url_for('google.login'))
    return redirect(url_for('index'))

# Callback route for Google OAuth
@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Google.", category="error")
        return False
    # Fetch user info from Google
    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info.", category="error")
        return False
    user_info = resp.json()
    email = user_info["email"]
    flash(f"Successfully signed in as {email}", category="success")

    # Redirects user to index page after successful login
    if session.pop("after_login", None):
        @after_this_request
        def redirect_after_login(response):
            return redirect(url_for("index"))

    return True

# Logout route clears the session and redirects to the login page
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

# Download outes will only work if the user is logged in
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

@app.route('/dashboard')
def dashboard():
    # Goes up one level from stock-bot/ and into raw_data/
    summary_path = os.path.join(os.path.dirname(__file__), '..', 'raw_data', 'rep_summary.json')
    summary_path = os.path.abspath(summary_path)

    if not os.path.exists(summary_path):
        return "Summary file not found.", 404

    with open(summary_path, 'r') as f:
        summary_data = json.load(f)

    return render_template('dashboard.html', data=summary_data)


@app.route('/chart_view')
def chart_list():
    stocks = [
        'AAPL', 'TSLA', 'GOOGL', 'AMZN', 'MSFT',
        'NASDAQ:IXIC', 'INDEX:SPX', 'INDEX:DJI'
    ]
    return render_template('chart_list.html', stocks=stocks)

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

    return render_template('chart_view.html', symbol=display_symbol, description=description, overview=overview)


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
    'MCD': 'McDonald’s Corporation is the largest fast-food chain in the world by revenue.',
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

@app.route('/contact')
def contact():
    return render_template('contact.html')
    success, message = download_disclosures(year)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)