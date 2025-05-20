# Author(s): 
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment: 
#    Senior Project (Summer 2025) - "text_phone"
# Last Update: 
#    May 20 2025
# Purpose: 
#    This script sends a text message to a specified phone number using an email-to-SMS gateway.


import smtplib  # For sending emails via SMTP
from email.mime.text import MIMEText  # For creating plain text email content

def send_text_message(phone_number, message, carrier='att'):
    """
    Sends a text message to the specified phone number using an email-to-SMS gateway.

    Args:
        phone_number (str): The recipient's phone number (digits only)
        message (str): The text message content
        carrier (str): Mobile carrier (must match key in `carrier_gateways`)

    Returns:
        dict: Status and message or error
    """

    # Mapping of carrier names to their email-to-SMS gateway domains
    carrier_gateways = {
        'att': '@txt.att.net',
        'verizon': '@vtext.com',
        'tmobile': '@tmomail.net',
        'sprint': '@messaging.sprintpcs.com'
    }

    sender_email = '###@gmail.com'  # Replace with email to be used

    # App password for your email (generated from Google > Security > App Passwords)
    sender_password = '###'  
    try:
        # Combine phone number and carrier gateway to create SMS address
        recipient_email = f"{phone_number}{carrier_gateways[carrier]}"

        # Build the email message
        msg = MIMEText(message)
        msg['Subject'] = 'SMS Message'
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Connect to the Gmail SMTP server securely
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        # Return success status
        return {
            'status': 'success',
            'message': 'SMS sent successfully'
        }

    except Exception as e:
        # Return error details if something goes wrong
        return {
            'status': 'error',
            'error_message': str(e)
        }

# Test block
if __name__ == "__main__":
    phone_number = "##########"  # Replace with recipient's number (digits only)
    message = "Your PDF investment report is complete. \n Click here:"
    
    # assuming carrier is att
    result = send_text_message(phone_number, message, carrier='att')
    print(result)
