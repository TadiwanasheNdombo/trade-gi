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
        # Always use the local service_account.json file
        service_account_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../service_account.json'))
        if not os.path.isfile(service_account_path):
            raise FileNotFoundError(f"Service account file not found at {service_account_path}")
        cred = credentials.Certificate(service_account_path)
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
