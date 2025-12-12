import base64
import json
import os
from datetime import datetime, timedelta, date

import google.generativeai as genai
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# --- Phase 1: Environment Setup and Initialization ---

def initialize_services():
    """Initializes Gemini API and Firebase Admin SDK."""
    print("Initializing services...")
    # Load environment variables from a .env file
    load_dotenv()

    # API Key: Read from environment variable
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)

    # Firebase/Firestore Connection
    cred = credentials.Certificate('service-account.json')
    firebase_admin.initialize_app(cred)
    db_client = firestore.client()
    print("Services initialized successfully.")
    return db_client

# --- Phase 2: Document Ingestion and Data Extraction (Gemini API) ---

def extract_trade_data_from_pdf(pdf_path: str) -> dict:
    """
    Uploads a PDF to the Gemini API and extracts structured data based on a prompt.
    """
    print(f"Uploading file: {pdf_path}...")
    # Use a suitable model like gemini-1.5-pro-latest or gemini-1.5-flash-latest
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    pdf_file = genai.upload_file(path=pdf_path, display_name="Trade Approval")
    print(f"File uploaded successfully: {pdf_file.name}")

    # Configure the request to return a JSON object
    generation_config = genai.GenerationConfig(response_mime_type="application/json")

    # A clear prompt with a JSON schema example
    prompt = """
    Based on the content of the provided trade finance approval document,
    extract the following fields and return them as a valid JSON object.

    - CFAAM_Ref: The unique reference number for the transaction.
    - Importer_Name: The full name of the importing company.
    - Date_Submitted: The date the document was submitted or created.
    - Currency_and_Amount: The currency code and the total amount.
    - Expiry_Date: The expiry date of the facility.
    - Returns_Frequency: The frequency at which returns must be submitted (e.g., Quarterly).
    - Condition_Text: The full text of the critical compliance condition related to submitting performance reports.
    """

    print("Sending extraction request to Gemini API...")
    response = model.generate_content([prompt, pdf_file], generation_config=generation_config)
    
    try:
        extracted_json = json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error decoding JSON response: {e}, Response text: {response.text}")
        raise
    genai.delete_file(pdf_file.name)
    print(f"Cleaned up uploaded file: {pdf_file.name}")

    extracted_json = json.loads(response.text)
    print("Data extracted successfully:")
    print(json.dumps(extracted_json, indent=2))
    return extracted_json


# --- Phase 3: Business Logic and Data Persistence ---

def enrich_and_save_data(db_client, data: dict):
    """
    Applies business logic to compute deadlines and saves the enriched data to Firestore.
    """
    print("Applying business logic and enriching data...")
    # --- Deadline Computation ---
    try:
        date_submitted_str = data.get("Date_Submitted")
        returns_frequency = data.get("Returns_Frequency", "").lower()

        if date_submitted_str and returns_frequency == "quarterly":
            date_submitted = datetime.strptime(date_submitted_str, "%d %B %Y")
            # Calculate the end of the quarter in which the document was submitted
            q_end_month = 3 * ((date_submitted.month - 1) // 3 + 1)
            quarter_end_date = datetime(date_submitted.year, q_end_month, 1) + relativedelta(months=1) - timedelta(days=1)
            
            # Due date is 14 days after quarter end
            next_due_date = quarter_end_date + timedelta(days=14)
            data["Next_Due_Date"] = next_due_date.strftime("%Y-%m-%d")

            # --- Calculate Compliance Alert Date ---
            compliance_alert_date = next_due_date - timedelta(days=7)
            data["Compliance_Alert_Date"] = compliance_alert_date.strftime("%Y-%m-%d")
            data["Initial_Alert_Date"] = compliance_alert_date.strftime("%Y-%m-%d")

    except Exception as e:
        print(f"Warning: Could not compute due dates. Error: {e}")

    # --- State Management ---
    data["Status"] = "Active"
    data["Reminder_Sent_Flag"] = False
    data["Processing_Timestamp_UTC"] = datetime.utcnow()

    # --- Firestore Write ---
    # Use CFAAM_Ref as the document ID for idempotency
    doc_id = data.get("CFAAM_Ref")
    if not doc_id:
        print("Error: CFAAM_Ref not found in extracted data. Cannot save to Firestore.")
        return

    doc_ref = db_client.collection('reminders').document(doc_id)
    doc_ref.set(data)
    print(f"Document stored in Firestore with ID: {doc_ref.id}")
    return doc_id

# --- Phase 4: Operational Simulation ---

def check_and_alert(db_client):
    """
    Simulates the reminder/escalation process by querying Firestore.
    """
    print("\n--- Running Simulated Reminder Check ---")
    today_str = date.today().strftime("%Y-%m-%d")
    
    # Query for documents that need an initial alert
    reminders_to_send = db_client.collection('reminders').where(
        'Reminder_Sent_Flag', '==', False
    ).where(
        'Initial_Alert_Date', '<=', today_str
    ).stream()

    found_reminders = False
    for reminder in reminders_to_send:
        found_reminders = True
        doc_data = reminder.to_dict()
        doc_id = reminder.id
        print(f"\n[ALERT FOUND] Document ID: {doc_id}")

        # --- Simulate Initial Alert ---
        print(f"  -> INITIAL ALERT: Agreement {doc_id} is due on {doc_data['Next_Due_Date']}.")
        print("  -> SIMULATING NOTIFICATION to Trade Officer/Relationship Manager.")

        # Update the flag in Firestore
        reminder.reference.update({'Reminder_Sent_Flag': True, 'Status': 'Initial_Alert_Sent'})
        print(f"  -> Updated Reminder_Sent_Flag to True for {doc_id}.")

    if not found_reminders:
        print("No initial alerts are due today.")

    # --- Simulate Escalation Path ---
    overdue_reminders = db_client.collection('reminders').where(
        'Next_Due_Date', '<', today_str
    ).stream()

    found_overdue = False
    for reminder in overdue_reminders:
        found_overdue = True
        doc_data = reminder.to_dict()
        doc_id = reminder.id
        due_date = datetime.strptime(doc_data['Next_Due_Date'], "%Y-%m-%d").date()
        days_overdue = (date.today() - due_date).days

        if days_overdue >= 7 and doc_data.get('Status') != 'Escalated_Compliance':
            print(f"\n[ESCALATION FOUND] Document ID: {doc_id} is {days_overdue} days overdue.")
            print("  -> FINAL ESCALATION: Notifying Head of Compliance/Risk Committee.")
            reminder.reference.update({'Status': 'Escalated_Compliance'})
        elif 0 < days_overdue < 7 and doc_data.get('Status') not in ['Overdue', 'Escalated_Compliance']:
            print(f"\n[ESCALATION FOUND] Document ID: {doc_id} is {days_overdue} days overdue.")
            print("  -> ESCALATION: Notifying Head of Trade Finance.")
            reminder.reference.update({'Status': 'Overdue'})

    if not found_overdue:
        print("No overdue items found for escalation.")

    print("--- Reminder Check Complete ---")


def main():
    """
    Main execution flow: Read PDF -> Extract Data -> Compute Logic -> Write to Firestore.
    """
    try:
        # Initialize API clients
        db = initialize_services()

        # Define the path to the document
        pdf_document_path = "sample_document.pdf" # Assumes the PDF is in the same directory

        # --- Execute Core Logic ---
        extracted_data = extract_trade_data_from_pdf(pdf_document_path)
        if extracted_data:
            enrich_and_save_data(db, extracted_data)

        # --- Run Simulation ---
        # This function would typically be run on a schedule (e.g., daily cron job)
        check_and_alert(db)

    except Exception as e:
        print(f"\nAn error occurred during execution: {e}")

if __name__ == "__main__":
    main()