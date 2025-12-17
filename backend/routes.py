from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import sys
import traceback
import json
import firebase_admin
from firebase_admin import credentials, firestore as fs
import google.genai
from backend.models import TradeApproval

main = Blueprint('main', __name__)

# Firebase/Gemini setup (reuse from main.py or refactor to config)
# Securely load credentials from environment variable
try:
    gcp_service_account_str = os.environ.get('GCP_SERVICE_ACCOUNT')
    if not gcp_service_account_str:
        raise ValueError("GCP_SERVICE_ACCOUNT environment variable not set.")
    
    gcp_service_account_info = json.loads(gcp_service_account_str)
    cred = credentials.Certificate(gcp_service_account_info)
except Exception as e:
    print(f"CRITICAL: Failed to initialize Firebase Admin SDK: {e}", file=sys.stderr)
    # In a real app, you might want to exit or handle this more gracefully
    cred = None # Ensure cred is defined

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
db = fs.client()

@main.route("/agreements", methods=["GET"])
def agreements_page():
    return render_template("agreements.html")
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

@main.route("/analytics", methods=["GET"])
def analytics_page():
    return render_template("analytics.html")

@main.route("/settings", methods=["GET"])
def settings_page():
    return render_template("settings.html")


def extract_and_validate(pdf_path):
    # Read PDF
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    # Gemini extraction
    extraction_prompt = (
        "Extract the following fields from the attached trade approval PDF and return a JSON object with these keys: "
        "CFAAM_Ref, Importer_Name, Date_Submitted, Currency_and_Amount, Expiry_Date, Returns_Frequency, Condition_Text. "
        "For Condition_Text, extract the critical compliance condition (e.g., 'Cangrow Trading (Pvt) Ltd shall submit a quarterly performance report...'). "
        "Format all dates as 'DD MMMM YYYY'.")
    client = google.genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        api_key=GEMINI_API_KEY
    )
    response = client.generate_content(
        contents=[
            {"mime_type": "application/pdf", "data": pdf_bytes},
            extraction_prompt
        ],
        generation_config={"response_mime_type": "application/json"}
    )
    data = response.json()
    # Pydantic validation
    validated = TradeApproval(**data)
    return validated.dict()

@main.route("/upload", methods=["GET", "POST"])
def upload_pdf():
    if request.method == "GET":
        return render_template("upload.html")
    if 'pdf' not in request.files:
        flash('No file part')
        return redirect(url_for('main.dashboard'))
    file = request.files['pdf']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('main.dashboard'))
    if file:
        filename = secure_filename(file.filename)
        upload_path = os.path.join('uploads', filename)
        file.save(upload_path)
        try:
            validated_data = extract_and_validate(upload_path)
            db.collection('reminders').add(validated_data)
            flash('File uploaded, extracted, validated, and stored!')
        except Exception as e:
            flash(f'Processing failed: {e}')
        return redirect(url_for('main.dashboard'))

@main.route("/", methods=["GET"])
def dashboard():
    # Fetch all reminders from Firestore
    records = []
    try:
        docs = db.collection('reminders').stream()
        for doc in docs:
            rec = doc.to_dict()
            rec['id'] = doc.id
            records.append(rec)
    except Exception as e:
        flash(f'Error fetching records: {e}')
    return render_template("index.html", records=records)
