import requests
import json
from flask import session


def send_gift_code_sms(phone_number, gift_code):
    """Send gift code via SMS using the specified API"""
    SMS_API_URL = "https://restapi.tobeprecisesms.com/api"
    SMS_USERNAME = "AjmalOTP"
    SMS_PASSWORD = "AJmt6301"
    SMS_SENDER = "Ajmal One"
    """
    Sends the gift code via SMS using the configured SMS API.

    Args:
        phone_number (str): The UAE-formatted recipient phone number.
        gift_code (str): The gift code to be sent.

    Returns:
        tuple: (success (bool), message (str)) – Whether sending was successful and the message to show.
    """
    message = f"Thank you for visiting Ajmal! Here is your special gift code: {gift_code}. Present this code at any Ajmal store in the UAE to claim your gift."
    url = f"{SMS_API_URL}/SendSMS/SingleSMS/?Username={SMS_USERNAME}&Password={SMS_PASSWORD}"

    payload = {
        "Message": message,
        "MobileNumbers": phone_number,
        "SenderName": SMS_SENDER
    }
    # Add this near the top of sms_utils.py
    DEBUG_MODE = True  # or False depending on what you want

    try:
        # Avoid sending SMS in test mode (use session or env flag)
        if 'test_mode' in session and session['test_mode']:
            if DEBUG_MODE:
                print("[DEBUG] Test mode enabled. Skipping actual SMS sending.")
            return True, "Gift code generated (test mode)!"

        response = requests.post(url, data=payload, timeout=10)

        if DEBUG_MODE:
            print(f"[DEBUG] Gift code SMS API response: {response.status_code}, Body: {response.text}")

        if response.status_code == 200:
            return True, "Gift code sent successfully!"
        else:
            return False, "We've generated your gift code! (SMS not sent)"
    except Exception as e:
        if DEBUG_MODE:
            print(f"[DEBUG] Exception while sending gift code SMS: {str(e)}")
        return False, "We've generated your gift code! (SMS exception)"