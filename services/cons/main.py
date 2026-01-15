# services/con/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shared.firestore import db, log
from shared.llm import call_llm_sync
import json

app = FastAPI()

class ConRequest(BaseModel):
    run_id: str
    factor_id: str

@app.post("/run")
async def run(req: ConRequest):
    run_id = req.run_id
    rounds_ref = db.collection("runs").document(run_id).collection("debates").document(req.factor_id).collection("rounds")
    latest = list(rounds_ref.order_by("createdAt", direction=firestore.Query.DESCENDING).limit(1).stream())
    if not latest:
        raise HTTPException(status_code=404, detail="No pro round found")
    pro_json = latest[0].to_dict().get("pro")
    prompt = f"""
You are the CON agent. Return ONLY valid JSON.
TASK: For each pro claim, produce a Line-by-line rebuttal.
Schema: [{{"claim_id":"str","undermined": true|false,"rebuttal":"str","evidence":{{"type":"pdf|null","page":int|null,"quote":"str|null"}}, "risk_level":"low|medium|high"}}]

PRO_CLAIMS:
{json.dumps(pro_json)}
"""
    try:
        con_json = call_llm_sync(prompt, require_json=True)
    except Exception as e:
        await log(run_id, "con", "error", str(e), req.factor_id)
        raise HTTPException(status_code=500, detail="LLM failed")

    # update latest round with con
    rounds_ref.document(latest[0].id).update({"con": con_json})
    await log(run_id, "con", "debate", f"Con produced rebuttals", req.factor_id)
    return {"ok": True}
