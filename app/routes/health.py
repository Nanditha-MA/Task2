from fastapi import APIRouter
from sqlalchemy import text
from app.core.database import engine
import time

router = APIRouter()

start_time = time.time()

@router.get("/health")
def health_check():
    db_status = "up"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except:
        db_status = "down"
    uptime = round(time.time() - start_time, 2)
    return {
        "status": "ok",
        "database": db_status,
        "uptime_seconds": uptime
    }