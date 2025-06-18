# Author(s): 
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment: 
#    Senior Project (Summer 2025) - "desktop_notifs.py"
# Last Update: 
#    June 16th 2025
# Purpose: 
#    This script creates desktop notifications for a user
#    for personalized investment plans if they "opt-in".

from plyer import notification
def notify_user(title: str, message: str):
    # Function is only called if user is opted in
    notification.notify(
        title=title,
        message=message,
        timeout=10 # in secs
    )    
