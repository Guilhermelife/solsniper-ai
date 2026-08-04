import os
import psutil
from fastapi import APIRouter

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
