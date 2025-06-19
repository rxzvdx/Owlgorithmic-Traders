"""
Author(s):
    Antonio Rosado
    Kashan Khan
    Imad Khan
    Alexander Schifferle
    Mike Kheang
Assignment:
    Senior Project (Summer 2025) - "desktop_notifs.py"
Last Update:
    June 16th 2025
Purpose:
    This script creates desktop notifications for a user
    who has opted in to personalized investment plans.
"""

from plyer import notification  # desktop notification library


def notify_user(title: str, message: str) -> None:
    """
    Send a desktop notification with a given title and message.

    This function should only be called when the user has opted in
    to receive personalized investment plan alerts.

    Args:
        title (str): The notification title displayed in the system tray.
        message (str): The notification body text shown to the user.
    """
    # Trigger the desktop notification
    notification.notify(
        title=title,         # Title of the notification pop-up
        message=message,     # Main content of the notification
        timeout=10           # Display duration in seconds before auto-dismissal
    )
