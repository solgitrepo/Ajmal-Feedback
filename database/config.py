# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access your SMS API credentials
SMS_API_URL = os.getenv("SMS_API_URL")
SMS_USERNAME = os.getenv("SMS_USERNAME")
SMS_PASSWORD = os.getenv("SMS_PASSWORD")
SMS_SENDER = os.getenv("SMS_SENDER")

# Debug mode flag
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
