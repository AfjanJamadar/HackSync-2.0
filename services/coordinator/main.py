# services/coordinator/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shared.firestore import db, log
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()


AGENT_URLS = {
    "extractor": os.getenv("EXTRACTOR_URL"),
    "pro": os.getenv("PRO_URL"),
    "con": os.getenv("CON_URL"),
    "chart": os.getenv("CHART_URL"),
    "synth": os.getenv("SYNTH_URL")
}

app = FastAPI()

class StartRun(BaseModel):
    run_id: str
    text: str = None
    pdf_path: str = None
    csv_path: str = None

def retry_post(url, payload, retries=3, backoff=1):
    for i in range(retries):
        try:
            r = requests.post(url, json=payload, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(backoff * (2 ** i))

@app.post("/start")
def start(payload: StartRun):
    run_id = payload.run_id
    db.collection("runs").document(run_id).set({
        "status": "queued",
        "createdAt": firestore.SERVER_TIMESTAMP,
        "input": {"pdf": payload.pdf_path, "csv": payload.csv_path}
    })
    log(run_id, "coordinator", "ingestion", "Run queued")
    # 1. Extraction
    ext_payload = {"run_id": run_id, "text": payload.text, "storage_pdf_path": payload.pdf_path}
    retry_post(AGENT_URLS["extractor"], ext_payload)
    log(run_id, "coordinator", "extraction", "Extractor invoked")
    # Wait for factors to appear (simple polling)
    for _ in range(30):
        docs = list(db.collection("runs").document(run_id).collection("factors").stream())
        if docs:
            break
        time.sleep(1)
    # 2. For each factor, run pro & con
    factors = list(db.collection("runs").document(run_id).collection("factors").stream())
    for f in factors:
        fid = f.id
        retry_post(AGENT_URLS["pro"], {"run_id": run_id, "factor_id": fid})
        log(run_id, "coordinator", "debate", f"Pro invoked for {fid}", fid)
        time.sleep(1)
        retry_post(AGENT_URLS["con"], {"run_id": run_id, "factor_id": fid})
        log(run_id, "coordinator", "debate", f"Con invoked for {fid}", fid)
    # 3. Chart (if CSV provided)
    if payload.csv_path:
        retry_post(AGENT_URLS["chart"], {"run_id": run_id, "csv_path": payload.csv_path})
    # 4. Synthesize
    retry_post(AGENT_URLS["synth"], {"run_id": run_id})
    db.collection("runs").document(run_id).update({"status": "done"})
    log(run_id, "coordinator", "decision", "Run completed")
    return {"ok": True}
