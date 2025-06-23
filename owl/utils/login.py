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
    Revised June 23, 2025
Purpose:
    Configure Google OAuth via Flask-Dance to allow users to log in or sign up
    using their Google accounts.
"""

from flask_dance.contrib.google import make_google_blueprint

# Create the Google OAuth blueprint for Flask-Dance.
# After the Google callback, Flask-Dance will automatically hand control
# over to the 'login' endpoint in app.py.
google_blueprint = make_google_blueprint(
    client_id="799793448477-gegoft10e3fu7enm1b9q15dp72i0l0bl.apps.googleusercontent.com",
    client_secret="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",
    scope=[
        "openid",                                           # OIDC auth
        "https://www.googleapis.com/auth/userinfo.email",   # Email access
        "https://www.googleapis.com/auth/userinfo.profile"  # Profile info
    ],
    redirect_to="login"    # endpoint name of @app.route('/auth') def login()
)

# In your app factory or main module, register this blueprint:
# app.register_blueprint(google_blueprint, url_prefix="/login")
