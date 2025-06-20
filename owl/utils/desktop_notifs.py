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


# CODE FOR OTHER PLATFORMS
# from plyer import notification

# notification.notify(
#     title='Owlgorithmic Alert',
#     message='Stock prices updated successfully!',
#     app_name='Owlgorithmic',
#     timeout=5  # seconds
# )

# import platform
# import subprocess

# def notify_user(title: str, message: str) -> None:
#     """
#     Send a desktop notification with a given title and message.

#     Args:
#         title (str): The notification title displayed in the system tray.
#         message (str): The notification body text shown to the user.
#     """
#     system = platform.system()

#     if system == "Darwin":  # macOS
#         subprocess.run([
#             "osascript", "-e",
#             f'display notification "{message}" with title "{title}"'
#         ])
#     elif system == "Linux":
#         # Requires notify-send to be installed (common on most Linux distros)
#         subprocess.run(["notify-send", title, message])
#     elif system == "Windows":
#         try:
#             from plyer import notification
#             notification.notify(
#                 title=title,
#                 message=message,
#                 timeout=10
#             )
#         except Exception as e:
#             print(f"[WARN] Notification failed on Windows: {e}")
#     else:
#         print(f"[INFO] Notification: {title} - {message}")