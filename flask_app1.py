from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import os
import re
from database.operations import save_form_data, phone_occurrence_count
from database.connection import init_database_tables
import random
import string
import requests
'''import webbrowser
import threading
import time'''
from database.connection import init_connection
from database.sms_utils import send_gift_code_sms  # Adjust the path as needed
from dotenv import load_dotenv
load_dotenv()
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Testing DB connection...")

#print("Testing DB connection...")
#engine = init_connection()
#print("Engine:", engine)

try:
    print("Testing DB connection...")
    engine = init_connection()
    print("Engine:", engine)
except Exception as e:
    logger.error("Database connection failed: %s", str(e))
    raise

app = Flask(__name__)
#app.secret_key = os.urandom(24)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
# Required for session management

# SMS Service Credentials
SMS_API_URL = os.environ.get("SMS_API_URL")
SMS_USERNAME = os.environ.get("SMS_USERNAME")
SMS_PASSWORD = os.environ.get("SMS_PASSWORD")
SMS_SENDER = os.environ.get("SMS_SENDER")

# Initialize database tables
init_database_tables()

'''def open_browser():
    time.sleep(1)  # Wait a moment for the server to start
    webbrowser.open_new('http://127.0.0.1:5000/ajmalfeedback-4D732203-CEFA-4827-AFE2-113853D5B053')'''
# Utility functions
def generate_otp():
    """Generate a 6-digit OTP code"""
    return ''.join(random.choices(string.digits, k=6))

def send_sms_otp(phone_number, otp_code):
    """Send OTP via SMS using the specified API"""
    message = f"Your Ajmal Feedback Form verification code is: {otp_code}"
    url = f"{SMS_API_URL}/SendSMS/SingleSMS/?Username={SMS_USERNAME}&Password={SMS_PASSWORD}"
    payload = {
        "Message": message,
        "MobileNumbers": phone_number,
        "SenderName": SMS_SENDER
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False

def format_uae_number(phone_number):
    """Validate and format UAE phone number"""
    phone_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    if phone_number.startswith('+971'):
        return phone_number
    if phone_number.startswith('0'):
        return '+971' + phone_number[1:]
    if phone_number.startswith('971'):
        return '+' + phone_number
    if len(phone_number) == 9 and phone_number.startswith(('50', '54', '55', '56', '58')):
        return '+971' + phone_number
    return None

# Routes
# Routes

@app.route('/test')
def test():
    return "Hello, Azure!"

@app.route('/<store_url_id>')
def index(store_url_id):
    # Extract UUID from the store_url_id using regex
    match = re.search(r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})$', store_url_id, re.IGNORECASE)
    if match:
        store_id = match.group(1)
        session['store_id'] = store_id
        session['store_url_id'] = store_url_id  # Save full slug
    else:
        return "Invalid store URL", 404

    # Initialize session
    session.setdefault('form_data', {})
    session.setdefault('otp_verified', False)

    # No OTP check here anymore
    return redirect(url_for('language_selection'))



@app.route('/')
def home():
    # Redirect to default store for testing
    return redirect('/ajmalfeedback-14FB5A88-C0F2-4EA9-B804-0A6DE1E28EE6')


@app.route('/language', methods=['GET', 'POST'])
def language_selection():
    if request.method == 'POST':
        selected_language = request.form.get('language')
        session['language'] = selected_language
        session.setdefault('form_data', {})
        session['form_data']['language'] = selected_language
        session['page'] = 2
        return redirect(url_for('intro'))  # Now goes to gift info page
    return render_template('language.html')


@app.route('/intro')
def intro():
    # Show thank you and gift info, and ask for mobile number if needed
    return render_template('intro.html')


@app.route('/start_survey', methods=['POST'])
def start_survey():
    # Begin the actual survey here
    return redirect(url_for('first_visit'))


@app.route('/first-visit', methods=['GET', 'POST'])
def first_visit():
    if request.method == 'POST':
        session['form_data']['first_visit'] = request.form.get('first_visit')
        session['page'] = 3
        return redirect(url_for('satisfaction'))
    return render_template('first_visit.html')


@app.route('/satisfaction', methods=['GET', 'POST'])
def satisfaction():
    if request.method == 'POST':
        session['form_data']['satisfaction'] = request.form.get('satisfaction')
        session['page'] = 4
        return redirect(url_for('satisfaction_reason'))
    return render_template('satisfaction.html')

@app.route("/satisfaction_reason", methods=["GET", "POST"])
def satisfaction_reason():
    if request.method == "POST":
        session.setdefault('form_data', {})
        if session['form_data']['satisfaction'] == "No":
            reason = request.form.get("dissatisfaction_reason", "").strip().lower()
            reason_text = request.form.get("dissatisfaction_reason_text", "").strip()

            session['form_data']['dissatisfaction_reason'] = reason
            session['form_data']['dissatisfaction_reason_text'] = reason_text
            session.modified = True

            if reason == "product":
                return redirect(url_for("product_feedback"))
            elif reason == "staff":
                return redirect(url_for("staff_feedback"))
            elif reason == "ambience":
                return redirect(url_for("ambience_feedback"))
            else:
                return redirect(url_for("additional_feedback"))

        else:
            session['form_data']['satisfaction_reason'] = request.form.get("satisfaction_reason")
            session.modified = True
            print("Satisfaction-related data being saved:", session['form_data'])
            return redirect(url_for('additional_feedback'))
    print(session['form_data'])
    return render_template("satisfaction_reason.html")

@app.route("/product_feedback", methods=["GET", "POST"])
def product_feedback():
    if request.method == "POST":
        session.setdefault('form_data', {})
        product_reasons = request.form.getlist("product_reasons")
        session['form_data']['product_reasons'] = product_reasons  # Correct key
        session.modified=True
        print("Saved product reasons:", session['form_data'])
        return redirect(url_for("additional_feedback"))
    language = session.get('form_data', {}).get('language', 'English')
    print(session['form_data'])
    return render_template("product_feedback.html", language=language)


@app.route("/staff_feedback", methods=["GET", "POST"])
def staff_feedback():
    if request.method == "POST":
        session.setdefault('form_data', {})
        staff_reasons = request.form.getlist("staff_reasons")
        session['form_data']['staff_reasons'] = staff_reasons  # Correct key
        session.modified=True
        print("Saved staff reasons:", session['form_data'])
        return redirect(url_for("additional_feedback"))
    language = session.get('form_data', {}).get('language', 'English')
    print(session['form_data'])
    return render_template("staff_feedback.html", language=language)


@app.route("/ambience_feedback", methods=["GET", "POST"])
def ambience_feedback():
    if request.method == "POST":
        session.setdefault('form_data', {})
        ambience_reasons = request.form.getlist("ambience_reasons")
        session['form_data']['ambience_reasons'] = ambience_reasons  # Correct key
        session.modified=True
        print("Saved ambience reasons:", session['form_data'])
        return redirect(url_for("additional_feedback"))
    language = session.get('form_data', {}).get('language', 'English')
    print(session['form_data'])
    return render_template("ambience_feedback.html",language=language)



@app.route("/additional_feedback", methods=["GET", "POST"])
def additional_feedback():
    if request.method == "POST":
        session.setdefault('form_data', {})
        session['form_data']['additional_feedback'] = request.form.get("additional_feedback")
        session.modified = True
        return redirect(url_for("nps"))  # ✅ Go to NPS page next
    print("Form data at additional_feedback:", session.get('form_data', {}))
    return render_template("additional_feedback.html")




@app.route('/nps', methods=['GET', 'POST'])
def nps():
    if request.method == 'POST':
        session['form_data']['nps'] = request.form.get('nps')
        session['page'] = 7
        return redirect(url_for('contact_info'))
    return render_template('nps.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact_info():
    if request.method == 'POST':
        session['form_data']['name'] = request.form.get('name')
        session['form_data']['email'] = request.form.get('email')
        store_id = session.get('store_id')  # Get store_id from session
        if session['form_data'] and store_id:
            session['submitted'] = True
            return redirect(url_for('verify_phone'))

        else:
            flash('Failed to save your feedback. Please try again.', 'error')
    print("Final form data being saved:", session.get("form_data"))
    return render_template('contact.html')

@app.route('/thank-you', methods=['GET'])
def thank_you():
    store_id = session.get('store_id')
    form_data = session.get('form_data', {})

    if form_data:
        phone = form_data.get('phone')
        
        if not phone:
            flash("Phone number is missing.", "error")
            return redirect(url_for('verify_phone'))

        phone_count = phone_occurrence_count(phone)

        session['form_data']['phone_count'] = phone_count
        session.modified = True

        # Inject store_id for DB saving
        form_data['store_id'] = store_id

        success, gift_code, is_first_time, sms_message = save_form_data(form_data)

        if success:
            return render_template(
                "thank_you.html",
                gift_code=gift_code,
                is_first_time=is_first_time,
                sms_message=sms_message
            )
        else:
            return "There was an error saving your response.", 500

    session.clear()
    return redirect('/')


@app.route('/verify-phone', methods=['GET', 'POST'])
def verify_phone():
    if request.method == 'POST':
        phone = request.form.get('phone')
        formatted_phone = format_uae_number(phone)
        if formatted_phone:
            otp = generate_otp()
            session['otp_code'] = otp
            if 'form_data' not in session:
                session['form_data'] = {}
            session['form_data']['phone'] = formatted_phone
            if send_sms_otp(formatted_phone, otp):
                session['otp_sent'] = True
                return redirect(url_for('enter_otp'))
            else:
                flash('Failed to send OTP. Please try again.', 'error')
        else:
            flash('Invalid phone number format. Please enter a valid UAE number.', 'error')
    return render_template('verify_phone.html')

@app.route('/enter-otp', methods=['GET', 'POST'])
def enter_otp():
    if request.method == 'POST':
        if request.form.get('otp') == session.get('otp_code'):
            session['otp_verified'] = True
            return redirect(url_for('thank_you'))  # 🚨 changed from 'language_selection'
        else:
            flash('Invalid OTP. Please try again.', 'error')
    return render_template('enter_otp.html')
@app.route('/start-over')
def start_over():
    session.clear()
    return redirect(url_for('language_selection'))  # or your actual starting route


if __name__ == '__main__':
    # threading.Thread(target=open_browser).start()
    # app.run(debug=True)
   
