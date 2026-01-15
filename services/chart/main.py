# services/chart/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shared.firestore import db, log
import pandas as pd
import json

app = FastAPI()

class ChartRequest(BaseModel):
    run_id: str
    csv_path: str = None
    indicator: str = None
    data: list = None  # optionally send data inline

@app.post("/run")
async def run(req: ChartRequest):
    run_id = req.run_id
    # For hackathon: support inline data or server-local csv_path
    if req.data:
        df = pd.DataFrame(req.data)
    elif req.csv_path:
        df = pd.read_csv(req.csv_path)
    else:
        raise HTTPException(status_code=400, detail="Provide csv_path or data")

    # Basic vega-lite spec for time series with year and value columns
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {"values": df.to_dict(orient="records")},
        "mark": "line",
        "encoding": {
            "x": {"field": "year", "type": "temporal"},
            "y": {"field": "value", "type": "quantitative"}
        }
    }

    db.collection("runs").document(run_id).collection("artifacts").add({
        "type": "chart",
        "spec": spec,
        "meta": {"rows": len(df)}
    })
    await log(run_id, "chart", "decision", "Chart spec generated")
    return {"ok": True, "spec": spec}
