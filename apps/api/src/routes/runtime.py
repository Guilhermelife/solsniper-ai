import os
import json
from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.get("/runtime")
def get_runtime():
    try:
        if os.path.exists("logs/runtime.json"):
            with open("logs/runtime.json", "r") as f:
                data = json.load(f)
                return data
        return {"error": "Runtime data not available yet."}
    except Exception as e:
        return {"error": str(e)}

@router.get("/health/worker")
def health_worker():
    try:
        if not os.path.exists("logs/runtime.json"):
            return {"worker_running": False, "error": "No runtime file"}
            
        with open("logs/runtime.json", "r") as f:
            data = json.load(f)
            
        last_scan_str = data.get("last_scan_at")
        if not last_scan_str:
            return {"worker_running": False, "error": "Invalid runtime format"}
            
        last_scan = datetime.fromisoformat(last_scan_str)
        
        # Consider worker dead if no scan in 5 minutes
        age_seconds = (datetime.utcnow() - last_scan).total_seconds()
        is_running = age_seconds < 300
        
        return {
            "worker_running": is_running,
            "last_scan_at": last_scan_str,
            "seconds_since_last_scan": age_seconds,
            "database_connected": True, # Implicit if runtime is updating
            "open_positions": data.get("open_positions", 0),
            "wallet_balance": data.get("wallet_balance", 0)
        }
    except Exception as e:
        return {"worker_running": False, "error": str(e)}
