# services/extractor/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shared.firestore import db, log
from shared.llm import call_llm_sync
import json
import uuid
from pypdf import PdfReader

app = FastAPI()

class ExtractRequest(BaseModel):
    run_id: str
    storage_pdf_path: str = None
    text: str = None

def extract_text_from_pdf_path(path):
    # path could be a local path; for demo we accept pre-extracted text or local PDF path
    try:
        reader = PdfReader(path)
        texts = []
        for i, page in enumerate(reader.pages):
            snippet = page.extract_text() or ""
            texts.append({"page": i+1, "text": snippet})
        return texts
    except Exception:
        return []

@app.post("/run")
async def run(req: ExtractRequest):
    run_id = req.run_id
    if not req.text and not req.storage_pdf_path:
        raise HTTPException(status_code=400, detail="Provide text or storage_pdf_path")
    # obtain document text
    snippets = []
    if req.text:
        snippets = [{"page": None, "text": req.text}]
    else:
        snippets = extract_text_from_pdf_path(req.storage_pdf_path)

    all_text = "\n\n".join([s["text"] for s in snippets])
    prompt = f"""
You are the FACTOR EXTRACTION agent.
Return ONLY valid JSON. No markdown.
Task: Extract 6-10 independent policy evaluation factors from the document.
Schema: [{{"id":"str","title":"str","description":"str","evidence":{{"page":"int|null","quote":"str"}}}}]

DOCUMENT_TEXT:
{all_text[:40000]}
"""

    try:
        factors = call_llm_sync(prompt, require_json=True)
    except Exception as e:
        await log(run_id, "extractor", "extraction_error", str(e))
        raise HTTPException(status_code=500, detail="LLM failed: "+str(e))

    # Validate & write to Firestore
    for f in factors:
        fid = f.get("id") or str(uuid.uuid4())
        doc = {
            "title": f.get("title"),
            "description": f.get("description"),
            "evidence": f.get("evidence"),
            "status": "pending"
        }
        db.collection("runs").document(run_id).collection("factors").document(fid).set(doc)

    await log(run_id, "extractor", "extraction", f"Extracted {len(factors)} factors")
    return {"ok": True, "count": len(factors)}

