

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
# Import the service function instead of having the logic here
from backend.services import extract_and_validate_pdf
main = Blueprint('main', __name__)

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
        return redirect(url_for('main.dashboard'))
    file = request.files['pdf']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('main.dashboard'))
    if file:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True) # Ensure upload folder exists
        upload_path = os.path.join(upload_folder, filename)
        file.save(upload_path)
        try:
            db = current_app.db
            if not db:
                raise ConnectionError("Database client is not initialized. Check server logs.")
            validated_data = extract_and_validate_pdf(upload_path)
            db.collection('reminders').add(validated_data)
            flash('File processed and reminder created successfully!')
        except Exception as e:
            flash(f'Processing failed: {e}')
        return redirect(url_for('main.dashboard'))

@main.route("/", methods=["GET"])
def dashboard():
    # Fetch all reminders from Firestore
    records = []
    db = current_app.db
    if db:
        try:
            docs = db.collection('reminders').stream()
            for doc in docs:
                rec = doc.to_dict()
                rec['id'] = doc.id
                records.append(rec)
        except Exception as e:
            flash(f'Error fetching records from database: {e}')
    else:
        flash('Database is not connected. Please check the application configuration.')
    return render_template("index.html", records=records)
