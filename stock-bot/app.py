import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP for local testing

# Flask framework imports
from flask import session, Flask, render_template, request, redirect, url_for, flash, current_app, after_this_request, send_file

# Custom Utilities
from utils.downloader import download_disclosures
from utils.login import google_blueprint

# Flask-Dance imports
from flask_dance.contrib.google import google
from flask_dance.consumer import oauth_authorized

#OAuth imports
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

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
    file_buffer, message = download_disclosures(year)
    
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


if __name__ == '__main__':
    app.run(debug=True)