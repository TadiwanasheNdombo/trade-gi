import google.genai
from flask import current_app
from backend.models import TradeApproval

def extract_and_validate_pdf(pdf_path: str) -> dict:
    """
    Extracts data from a PDF file using Gemini, validates it with Pydantic,
    and returns the validated data as a dictionary.
    """
    # Read PDF file bytes
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    # Configure the Gemini client
    client = google.genai.GenerativeModel(
        model_name="gemini-pro",
        api_key=current_app.config['GEMINI_API_KEY']
    )

    # Define the extraction prompt
    extraction_prompt = (
        "Extract the following fields from the attached trade approval PDF and return a JSON object with these keys: "
        "CFAAM_Ref, Importer_Name, Date_Submitted, Currency_and_Amount, Expiry_Date, Returns_Frequency, Condition_Text. "
        "For Condition_Text, extract the critical compliance condition. Format all dates as 'DD MMMM YYYY'."
    )

    # Generate content from the PDF
    response = client.generate_content(
        contents=[{"mime_type": "application/pdf", "data": pdf_bytes}, extraction_prompt],
        generation_config={"response_mime_type": "application/json"}
    )

    # Validate the extracted data using the Pydantic model
    validated_data = TradeApproval.parse_raw(response.text)
    return validated_data.dict()