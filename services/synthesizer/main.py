# services/synthesizer/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from shared.firestore import db, log
from shared.llm import call_llm_sync
import json

app = FastAPI()

class SynthRequest(BaseModel):
    run_id: str

@app.post("/run")
async def run(req: SynthRequest):
    run_id = req.run_id
    factors = db.collection("runs").document(run_id).collection("factors").stream()
    all_debates = {}
    for f in factors:
        fid = f.id
        rounds = [r.to_dict() for r in db.collection("runs").document(run_id).collection("debates").document(fid).collection("rounds").stream()]
        all_debates[fid] = {"factor": f.to_dict(), "rounds": rounds}

    prompt = f"""
You are the SYNTHESIZER agent. Return ONLY valid JSON.
Task: For each factor return verdict (supported|contested|insufficient), a 2-3 sentence rationale, and two prioritized recommendations.

Schema:
{{
  "factor_decisions": [
    {{
      "factor_id": "str",
      "verdict": "supported|contested|insufficient",
      "score": 0,
      "rationale": "str",
      "recommendations": ["str", "str"]
    }}
  ],
  "summary": {{
    "what_worked": "str",
    "what_failed": "str",
    "why": "str",
    "how_to_improve": "str"
  }}
}}

Debates:
{json.dumps(all_debates)[:90000]}
"""
    try:
        report = call_llm_sync(prompt, require_json=True, max_output_tokens=1500)
    except Exception as e:
        await log(run_id, "synthesizer", "error", str(e))
        raise

    db.collection("runs").document(run_id).collection("report").document("final").set(report)
    await log(run_id, "synthesizer", "decision", "Final report generated")
    return {"ok": True}
