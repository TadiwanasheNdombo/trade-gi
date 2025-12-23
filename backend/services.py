import google.generativeai as genai
from flask import current_app
from backend.models import TradeApproval
import os
import smtplib
import ssl
import logging
from datetime import datetime
from email.message import EmailMessage

def extract_and_validate_pdf(pdf_path: str) -> dict:
    """
    Extracts data from a PDF file using Gemini, validates it with Pydantic,
    and returns the validated data as a dictionary.
    """
    # Read PDF file bytes
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    # Configure the Gemini client
    genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    # Define the extraction prompt (explicitly list all required fields)
    extraction_prompt = (
        "Extract the following fields from the attached trade approval PDF and return a JSON object with these exact keys: "
        "CFAAM_Ref, Importer_Name, Date_Submitted, Currency_and_Amount, Expiry_Date, Returns_Frequency, Condition_Text, "
        "Next_Due_Date, Compliance_Alert_Date, Status, Reminder_Sent_Flag, Initial_Alert_Date. "
        "For Condition_Text, extract the critical compliance condition. "
        "Format all dates as 'DD MMMM YYYY'. "
        "For Reminder_Sent_Flag, return true or false. "
        "If any field is not present in the PDF, return null for that field."
    )

    # Generate content from the PDF
    response = model.generate_content([
        {"mime_type": "application/pdf", "data": pdf_bytes},
        extraction_prompt
    ], generation_config={"response_mime_type": "application/json"})

    # Validate the extracted data using the Pydantic model
    validated_data = TradeApproval.parse_raw(response.text)
    return validated_data.dict()

def send_compliance_reminders() -> dict:
    """
    Queries trade_agreements, checks expiry dates, and sends email reminders
    for clients with deadlines 30, 15, or 5 days away.
    """
    db = current_app.db
    if not db:
        return {"status": "error", "message": "Database not connected"}

    # Retrieve environment variables
    gmail_user = os.environ.get('GMAIL_ADDRESS')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')

    if not gmail_user or not gmail_password:
        logging.error("Gmail credentials are not set in environment variables.")
        return {"status": "error", "message": "Server email configuration missing"}

    collection_ref = db.collection('trade_agreements')
    docs = collection_ref.stream()
    
    sent_count = 0
    today = datetime.now().date()

    for doc in docs:
        data = doc.to_dict()
        expiry_str = data.get('Expiry_Date')
        
        if not expiry_str:
            continue

        try:
            # Parse Expiry Date (DD MMMM YYYY)
            expiry_date = datetime.strptime(expiry_str, "%d %B %Y").date()
            days_until = (expiry_date - today).days

            # Check if deadline is exactly 30, 15, or 5 days away
            if days_until in [30, 15, 5]:
                # Check if we already sent a notification today
                last_notif = data.get('last_notification_date')
                if last_notif == str(today):
                    continue

                # Prepare Email
                importer_name = data.get('Importer_Name', 'Valued Client')
                ref_number = data.get('CFAAM_Ref', 'Unknown Ref')
                condition_text = data.get('Condition_Text', 'Please review your trade agreement conditions.')
                # Note: Assuming 'Client_Email' exists in the doc. If not, this will skip sending.
                recipient_email = data.get('Client_Email') 

                if recipient_email:
                    msg = EmailMessage()
                    msg['Subject'] = f"Compliance Alert: Action Required for {ref_number}"
                    msg['From'] = gmail_user
                    msg['To'] = recipient_email
                    msg.set_content(
                        f"Dear {importer_name},\n\n"
                        f"This is a reminder that your trade agreement (Ref: {ref_number}) expires on {expiry_str}.\n"
                        f"Time remaining: {days_until} days.\n\n"
                        f"Requirement from Exchange Control Act:\n{condition_text}\n\n"
                        f"Please ensure all obligations are met to avoid penalties.\n\n"
                        f"Sincerely,\nTrade Compliance Team"
                    )

                    # Send via Gmail SMTP
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                        smtp.login(gmail_user, gmail_password)
                        smtp.send_message(msg)
                    
                    # Update Firestore with last notification date
                    doc.reference.update({
                        'last_notification_date': str(today),
                        'Reminder_Sent_Flag': True
                    })
                    sent_count += 1
                    logging.info(f"Reminder sent to {recipient_email} for {ref_number}")
                else:
                    logging.warning(f"No email address found for document {doc.id}")

        except Exception as e:
            logging.error(f"Error processing document {doc.id}: {e}")
            continue

    return {"status": "success", "emails_sent": sent_count}