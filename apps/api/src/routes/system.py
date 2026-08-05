import os
import psutil
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from apps.common.database import get_db
from apps.common.models.position import Position
from apps.common.models.settings import SystemSettings
from apps.common.models.signal import Signal

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/")
def get_system_stats():
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu_usage_percent": cpu_percent,
        "ram_usage_percent": memory.percent,
        "ram_total_gb": round(memory.total / (1024**3), 2),
        "ram_used_gb": round(memory.used / (1024**3), 2),
        "disk_usage_percent": disk.percent,
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "disk_used_gb": round(disk.used / (1024**3), 2)
    }

@router.get("/badges")
def get_sidebar_badges(db: Session = Depends(get_db)):
    # 1. Open Positions
    open_positions = db.query(Position).filter(Position.status == "OPEN").count()
    
    # 2. Max Open Positions
    settings = db.query(SystemSettings).first()
    max_open_positions = settings.max_open_positions if settings else 5
    
    # 3. Pending Signals (now WATCHING in HFT mode)
    pending_signals = db.query(Signal).filter(Signal.confirmation_status == "WATCHING").count()
    
    # 4. Scanned Tokens (Live Market)
    scanned_tokens = 0
    try:
        if os.path.exists("logs/latest_scan.json"):
            with open("logs/latest_scan.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                scanned_tokens = len(data) if isinstance(data, list) else 0
    except Exception:
        pass
        
    # 5. Error Logs
    error_warnings = 0
    try:
        if os.path.exists("logs/errors.log"):
            with open("logs/errors.log", "r", encoding="utf-8") as f:
                error_warnings = sum(1 for line in f if line.strip())
    except Exception:
        pass
        
    return {
        "open_positions": open_positions,
        "max_open_positions": max_open_positions,
        "pending_signals": pending_signals,
        "scanned_tokens": scanned_tokens,
        "error_warnings": error_warnings
    }
