import os
import json
from fastapi import APIRouter

router = APIRouter(prefix="/market", tags=["Market"])

@router.get("/latest")
def get_latest_scan():
    path = "logs/latest_scan.json"
    if not os.path.exists(path):
        return {"tokens": []}
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            tokens = json.load(f)
        return {"tokens": tokens}
    except Exception as e:
        return {"tokens": [], "error": str(e)}

@router.get("/live-signals")
def get_live_signals():
    path = "logs/live_signals.json"
    if not os.path.exists(path):
        return {"signals": []}
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            signals = json.load(f)
        return {"signals": signals}
    except Exception as e:
        return {"signals": [], "error": str(e)}
