# services/pro/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shared.firestore import db, log
from shared.llm import call_llm_sync
import json

app = FastAPI()

class ProRequest(BaseModel):
    run_id: str
    factor_id: str

@app.post("/run")
async def run(req: ProRequest):
    run_id = req.run_id
    fdoc = db.collection("runs").document(run_id).collection("factors").document(req.factor_id).get()
    if not fdoc.exists:
        raise HTTPException(status_code=404, detail="factor not found")
    factor = fdoc.to_dict()
    prompt = f"""
You are the PRO agent. Return ONLY valid JSON. No markdown.
TASK: Provide EXACTLY 3 claims supporting why this factor is a strength.
Schema: [{{"claim_id":"str","claim":"str","evidence":{{"type":"pdf","page":int,"quote":"str"}}, "confidence":0.0}}]

FACTOR:
{factor.get("description")}

DOCUMENT_SNIPPETS:
{json.dumps(factor.get("evidence", {}))}
"""
    try:
        pro_claims = call_llm_sync(prompt, require_json=True)
    except Exception as e:
        await log(run_id, "pro", "error", str(e), req.factor_id)
        raise HTTPException(status_code=500, detail="LLM failed")

    # append to debates rounds
    rounds_ref = db.collection("runs").document(run_id).collection("debates").document(req.factor_id).collection("rounds")
    rounds_ref.add({"round": 1, "pro": pro_claims, "con": {}, "createdAt": db.write_timestamp if hasattr(db, 'write_timestamp') else None})
    await log(run_id, "pro", "debate", f"Pro produced {len(pro_claims)} claims", req.factor_id)
    return {"ok": True}
