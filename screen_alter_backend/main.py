import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

try:
    from . import database, auth
    from .database import get_db, User, Config, Alert, MonitoringLog
except (ImportError, ValueError):
    import database, auth
    from database import get_db, User, Config, Alert, MonitoringLog

app = FastAPI(title="Screen Alter Backend")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- Dependencies ---

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

# --- Endpoints ---

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "username": user.username}

@app.get("/config")
async def get_config(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    config = db.query(Config).filter(Config.user_id == current_user.id).first()
    if not config:
        # Create default config if not exists
        config = Config(
            user_id=current_user.id,
            keywords="[]",
            capture_region="null",
            reference_images="[]"
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return {
        "monitor_interval": config.monitor_interval,
        "ocr_engine": config.ocr_engine,
        "keywords": json.loads(config.keywords),
        "capture_region": json.loads(config.capture_region) if config.capture_region != "null" else None,
        "reference_images": json.loads(config.reference_images)
    }

@app.post("/config")
async def update_config(config_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    config = db.query(Config).filter(Config.user_id == current_user.id).first()
    if not config:
        config = Config(user_id=current_user.id)
        db.add(config)
    
    if "monitor_interval" in config_data:
        config.monitor_interval = config_data["monitor_interval"]
    if "ocr_engine" in config_data:
        config.ocr_engine = config_data["ocr_engine"]
    if "keywords" in config_data:
        config.keywords = json.dumps(config_data["keywords"], ensure_ascii=False)
    if "capture_region" in config_data:
        config.capture_region = json.dumps(config_data["capture_region"])
    if "reference_images" in config_data:
        config.reference_images = json.dumps(config_data["reference_images"], ensure_ascii=False)
    
    db.commit()
    return {"message": "Config updated successfully"}

@app.post("/alerts")
async def create_alert(alert_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alert = Alert(
        user_id=current_user.id,
        detected_keyword=alert_data.get("detected_keyword"),
        screenshot_path=alert_data.get("screenshot_path"),
        detection_method=alert_data.get("detection_method"),
        similarity_score=alert_data.get("similarity_score"),
        alert_sent=alert_data.get("alert_sent", False)
    )
    db.add(alert)
    db.commit()
    return {"id": alert.id, "message": "Alert recorded"}

@app.get("/alerts")
async def get_alerts(limit: int = 50, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.user_id == current_user.id)\
               .order_by(Alert.created_at.desc()).limit(limit).all()
    return [
        {
            "id": a.id,
            "created_at": a.created_at.isoformat(),
            "detected_keyword": a.detected_keyword,
            "screenshot_path": a.screenshot_path,
            "detection_method": a.detection_method,
            "similarity_score": a.similarity_score,
            "alert_sent": a.alert_sent
        } for a in alerts
    ]

@app.post("/logs")
async def create_log(log_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log = MonitoringLog(
        user_id=current_user.id,
        result_status=log_data.get("result_status"),
        details=log_data.get("details"),
        screenshot_path=log_data.get("screenshot_path"),
        check_time=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    return {"id": log.id}

@app.get("/stats")
async def get_stats(days: int = 7, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Basic stats
    total_alerts = db.query(Alert).filter(Alert.user_id == current_user.id).count()
    sent_alerts = db.query(Alert).filter(Alert.user_id == current_user.id, Alert.alert_sent == True).count()
    
    return {
        "total_alerts": total_alerts,
        "alerts_sent": sent_alerts,
        "period_days": days
    }

# Initialization helper
@app.on_event("startup")
def startup_event():
    # Example: Create tables if using SQLite for dev, but we expect MySQL
    # database.Base.metadata.create_all(bind=database.engine)
    
    # Check if a default user exists for testing
    db = database.SessionLocal()
    if db.query(User).count() == 0:
        test_user = User(
            username="admin",
            password_hash=auth.hash_password("admin123")
        )
        db.add(test_user)
        db.commit()
        print("Default user 'admin' created with password 'admin123'")
    db.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
