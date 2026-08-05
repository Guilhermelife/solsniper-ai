import time
import os
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from apps.common.database import get_db

router = APIRouter()

API_START_TIME = time.time()

@router.get("/health")
def health(db: Session = Depends(get_db)):
    
    # 1. API Telemetry
    api_uptime = time.time() - API_START_TIME
    api_telemetry = {
        "status": "Running",
        "version": "0.1.0",
        "uptime_seconds": api_uptime,
        "total_requests": 0  # To be implemented if middleware added, or leave placeholder
    }
    
    # 2. Database Telemetry
    db_status = "Disconnected"
    db_latency = 0
    try:
        t0 = time.time()
        db.execute(text("SELECT 1"))
        db_latency = (time.time() - t0) * 1000.0
        db_status = "Connected"
    except Exception:
        pass
        
    db_telemetry = {
        "status": db_status,
        "latency_ms": db_latency,
        "total_tables": 0, # Optional
        "size_mb": 0       # Optional
    }
    
    # 3. Worker Daemon Telemetry
    worker_telemetry = {
        "status": "Stopped",
        "last_heartbeat": None,
        "last_scan_at": None,
        "scans_performed": 0,
        "tokens_analyzed": 0,
        "signals_generated": 0,
        "trades_executed": 0,
        "open_positions": 0,
        "cpu_usage_percent": 0.0,
        "memory_usage_percent": 0.0,
        "loop_duration_seconds": 0.0
    }
    
    if os.path.exists("logs/runtime.json"):
        try:
            with open("logs/runtime.json", "r") as f:
                runtime = json.load(f)
                
            last_scan_at = runtime.get("last_scan_at")
            if last_scan_at:
                try:
                    last_scan_dt = datetime.fromisoformat(last_scan_at)
                    # Support naive strings from worker (utcnow)
                    if last_scan_dt.tzinfo is None:
                        last_scan_dt = last_scan_dt.replace(tzinfo=timezone.utc)
                    age_seconds = (datetime.now(timezone.utc) - last_scan_dt).total_seconds()
                    
                    if age_seconds < 120:
                        worker_telemetry["status"] = "Running"
                        
                    worker_telemetry["last_heartbeat"] = last_scan_at
                except:
                    pass
                    
            worker_telemetry.update({
                "last_scan_at": runtime.get("last_scan_at"),
                "scans_performed": runtime.get("scans_performed", 0),
                "tokens_analyzed": runtime.get("tokens_analyzed", 0),
                "signals_generated": runtime.get("signals_generated", 0),
                "trades_executed": runtime.get("trades_executed", 0),
                "open_positions": runtime.get("open_positions", 0),
                "cpu_usage_percent": runtime.get("cpu_usage_percent", 0.0),
                "memory_usage_percent": runtime.get("memory_usage_percent", 0.0),
                "loop_duration_seconds": runtime.get("loop_duration_seconds", 0.0)
            })
        except Exception:
            pass
            
    return {
        "api": api_telemetry,
        "database": db_telemetry,
        "worker": worker_telemetry
    }