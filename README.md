# Trade Finance Compliance Automation Script

This project is a local Python script designed to automate the extraction and management of compliance conditions from trade finance approval documents. It uses the Google Gemini API to intelligently extract structured data from a PDF, calculates critical compliance deadlines, and persists the information in a Firebase Firestore database for tracking and alerting.

## Technology Stack

- **Primary Language:** Python
- **Core Libraries:**
  - `google-generativeai`: For interacting with the Gemini API.
  - `firebase-admin`: To connect and interact with the Firestore database.
  - `python-dotenv`: For managing environment variables (like API keys).
  - `python-dateutil`: For robust date and time manipulation.
- **Data Services:**
  - **Google Gemini API:** For AI-powered data extraction from PDF documents.
  - **Firebase Cloud Firestore:** As a NoSQL database for storing and managing compliance data.

## Features

- **AI-Powered Data Extraction:** Leverages the Gemini API to read a PDF and extract key-value pairs into a structured JSON format.
- **Automated Deadline Calculation:** Computes the `Next_Due_Date` and `Compliance_Alert_Date` based on the extracted document details.
- **Persistent Storage:** Saves the enriched data to a Firestore collection, using the unique transaction reference as the document ID.
- **Simulated Alerting:** Includes a function to query the database and simulate sending initial alerts and escalations based on due dates.
- **Secure Credential Management:** Uses a `.env` file for the API key and a `.gitignore` file to protect sensitive credentials.

## Setup and Installation

Follow these steps to get the project running on your local machine.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <repository-name>
```

### 2. Create a `requirements.txt` File

Create a file named `requirements.txt` and add the following lines:

```
google-generativeai
firebase-admin
python-dotenv
python-dateutil
```

Then, install the dependencies:

```bash
pip install -r requirements.txt
```

### 3. Set Up Credentials

1.  **Gemini API Key**: Create a file named `.env` and add your API key:
    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```
2.  **Firebase Service Account**: Download your `service-account.json` file from your Google Cloud/Firebase project and place it in the root directory of this project.

> **Note**: The `.gitignore` file is already configured to prevent your `.env` and `service-account.json` files from being uploaded to GitHub.

### 4. Place the Document

Ensure the PDF document you want to process (e.g., `sample_document.pdf`) is in the root directory.

## Usage

Once the setup is complete, you can run the script from your terminal:

```bash
python main.py
```

The script will:
1. Initialize the connection to Google and Firebase services.
2. Process the PDF file with the Gemini API.
3. Apply business logic and save the data to Firestore.
4. Run a simulated check for any due or overdue alerts.