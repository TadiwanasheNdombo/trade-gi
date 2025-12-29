

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import logging
from werkzeug.utils import secure_filename
import os
# Import the service function instead of having the logic here
from backend.services import extract_and_validate_pdf, send_compliance_reminders

main = Blueprint('main', __name__)

# Ensure UPLOAD_FOLDER is set in app config
def ensure_upload_folder(app):
    if not app.config.get('UPLOAD_FOLDER'):
        app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@main.record_once
def setup_upload_folder(state):
    ensure_upload_folder(state.app)

@main.route("/reminders", methods=["GET"])
def reminders_page():
    # Placeholder page for reminders
    return render_template("reminders.html")

@main.route("/calendar", methods=["GET"])
def calendar_page():
    # Redirect to compliance calendar for now
    return render_template("compliance_calendar.html")

@main.route("/compliance-calendar", methods=["GET"])
def compliance_calendar_page():
    return render_template("compliance_calendar.html")

@main.route("/agreements", methods=["GET"])
def agreements_page():
    return render_template("agreements.html")

@main.route("/analytics", methods=["GET"])
def analytics_page():
    return render_template("analytics.html")

@main.route("/settings", methods=["GET"])
def settings_page():
    return render_template("settings.html")

@main.route("/upload", methods=["GET", "POST"])
def upload_pdf():
    if request.method == "GET":
        return render_template("upload.html")
    if 'pdf' not in request.files:
        flash('No file part')
        logging.error("No file part in request.files")
        return redirect(url_for('main.dashboard'))
    file = request.files['pdf']
    if file.filename == '':
        flash('No selected file')
        logging.error("No selected file")
        return redirect(url_for('main.dashboard'))
    if file:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        try:
            os.makedirs(upload_folder, exist_ok=True) # Ensure upload folder exists
            upload_path = os.path.join(upload_folder, filename)
            file.save(upload_path)
            logging.info(f"File saved at {upload_path}")
            try:
                validated_data = extract_and_validate_pdf(upload_path)
                logging.info(f"Extracted data: {validated_data}")
                # Show extracted data for review before saving
                return render_template("review.html", extracted=validated_data)
            except Exception as extraction_error:
                error_msg = f"Extraction/validation failed: {extraction_error}"
                flash(error_msg)
                logging.error(error_msg)
                return render_template("upload.html", error=error_msg)
        except Exception as e:
            error_msg = f"File save failed: {e}"
            flash(error_msg)
            logging.error(error_msg)
            return render_template("upload.html", error=error_msg)
# Route to confirm and save reviewed data
@main.route("/confirm-review", methods=["POST"])
def confirm_review():
    db = current_app.db
    if not db:
        flash("Database client is not initialized. Check server logs.")
        return redirect(url_for('main.dashboard'))
    try:
        reviewed_data = dict(request.form)
        db.collection('trade_agreements').add(reviewed_data)
        flash('File processed and reminder created successfully!')
    except Exception as e:
        flash(f'Failed to save reviewed data: {e}')
    return redirect(url_for('main.dashboard'))

@main.route("/", methods=["GET"])
def dashboard():
    # Fetch all reminders from Firestore
    records = []
    db = current_app.db
    if db:
        try:
            docs = db.collection('trade_agreements').stream()
            for doc in docs:
                rec = doc.to_dict()
                rec['id'] = doc.id
                records.append(rec)
        except Exception as e:
            flash(f'Error fetching records from database: {e}')
    else:
        flash('Database is not connected. Please check the application configuration.')
    return render_template("index.html", records=records)

@main.route("/run-reminders", methods=["GET", "POST"])
def trigger_reminders():
    # Simple security check
    auth_token = request.headers.get('X-Auth-Token') or request.args.get('token')
    expected_token = os.environ.get('ADMIN_AUTH_TOKEN')
    print(f"Expected token: {expected_token!r}")
    print(f"Received token: {auth_token!r}")
    if not expected_token or auth_token != expected_token:
        return {"error": "Unauthorized access"}, 401

    result = send_compliance_reminders()
    return result
