from flask import Flask
import os
import sys
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    # --- App Configuration ---
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key-for-dev')
    app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY')

    # --- Service Initializations ---
    # Initialize Firebase Admin SDK
    try:
        gcp_service_account_str = os.environ.get('GCP_SERVICE_ACCOUNT')
        if not gcp_service_account_str:
            raise ValueError("GCP_SERVICE_ACCOUNT environment variable not set or empty.")

        # The service account can be a path to a file or a JSON string
        if os.path.isfile(gcp_service_account_str):
             cred = credentials.Certificate(gcp_service_account_str)
        else:
            gcp_service_account_info = json.loads(gcp_service_account_str)
            cred = credentials.Certificate(gcp_service_account_info)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)

        app.db = firestore.client()
        print("Firebase initialized successfully.", file=sys.stdout)
    except Exception as e:
        print(f"CRITICAL: Failed to initialize Firebase Admin SDK: {e}", file=sys.stderr)
        app.db = None

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
