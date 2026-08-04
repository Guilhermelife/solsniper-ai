import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("/{log_type}")
def get_logs(log_type: str, lines: int = 100):
    valid_logs = ["worker", "trades", "errors"]
    if log_type not in valid_logs:
        raise HTTPException(status_code=400, detail="Invalid log type")
        
    path = f"logs/{log_type}.log"
    if not os.path.exists(path):
        return {"logs": []}
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            
        return {"logs": all_lines[-lines:]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
