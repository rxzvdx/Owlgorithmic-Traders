# Author(s): 
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment: 
#    Senior Project (Summer 2025) - "login.py"
# Last Update: 
#    June 8 2025
# Purpose: 
#    This script allows users to sign in/sign up with Google OAuth

from flask_dance.contrib.google import make_google_blueprint

google_blueprint = make_google_blueprint(
    client_id="799793448477-gegoft10e3fu7enm1b9q15dp72i0l0bl.apps.googleusercontent.com",
    client_secret="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",
    redirect_url="/login/google/authorized",
    redirect_to = None, # Added this to disable the auto handle of the redirect after logging in 
    scope=[
        "openid",                                           # openid is required for authentication 
        "https://www.googleapis.com/auth/userinfo.email",   # gives access to the user's email adress
        "https://www.googleapis.com/auth/userinfo.profile"  # gives access to ths user's profile information
        ],
)