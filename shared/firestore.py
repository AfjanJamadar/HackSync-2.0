# services/shared/firestore.py
import os
import firebase_admin
from firebase_admin import credentials, firestore
from google.auth.exceptions import DefaultCredentialsError

def init_firebase():
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CREDENTIALS")
        if cred_path:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Application Default Credentials
            firebase_admin.initialize_app()
    return firestore.client()

db = init_firebase()

def log(run_id, role, stage, content, factor_id=None, citations=None):
    doc = {
        "role": role,
        "stage": stage,
        "factorId": factor_id,
        "content": content,
        "citations": citations or [],
        "createdAt": firestore.SERVER_TIMESTAMP
    }
    return db.collection("runs").document(run_id).collection("messages").add(doc)
