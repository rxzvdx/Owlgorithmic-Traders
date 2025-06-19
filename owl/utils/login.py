"""
Author(s):
    Antonio Rosado
    Kashan Khan
    Imad Khan
    Alexander Schifferle
    Mike Kheang
Assignment:
    Senior Project (Summer 2025) - "login.py"
Last Update:
    Revised June 19, 2025
Purpose:
    Configure Google OAuth via Flask-Dance to allow users to log in or sign up
    using their Google accounts.
"""

from flask_dance.contrib.google import make_google_blueprint

# Create the Google OAuth blueprint for Flask-Dance
google_blueprint = make_google_blueprint(
    client_id="799793448477-gegoft10e3fu7enm1b9q15dp72i0l0bl.apps.googleusercontent.com",
    client_secret="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",
    # After successful auth, Google will redirect here
    redirect_url="/login/google/authorized",
    # Disable the default redirect_to handler so you can control post-login flow
    redirect_to=None,
    scope=[
        "openid",                                           # Required for OIDC authentication
        "https://www.googleapis.com/auth/userinfo.email",   # Access to user's email address
        "https://www.googleapis.com/auth/userinfo.profile"  # Access to user's basic profile info
    ],
)

# To use this blueprint, register it in the Flask app:
# app.register_blueprint(google_blueprint, url_prefix="/login")
