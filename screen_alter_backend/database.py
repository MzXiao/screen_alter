import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# MySQL configuration from environment variables
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "bbe0a7763e097baf")
MYSQL_HOST = os.getenv("MYSQL_HOST", "8.134.58.148")
MYSQL_PORT = os.getenv("MYSQL_PORT", "5306")
MYSQL_DB = os.getenv("MYSQL_DB", "screen_alter")

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,       # 关键：执行查询前先检测连接是否有效，失效则重连
        pool_recycle=3600,        # 关键：连接存活超过 1 小时自动回收重建
        pool_size=5,              # 连接池基础大小
        max_overflow=10           # 允许临时溢出的连接数
                       )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    config = relationship("Config", back_populates="user", uselist=False)
    alerts = relationship("Alert", back_populates="user")
    logs = relationship("MonitoringLog", back_populates="user")

class Config(Base):
    __tablename__ = "configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    monitor_interval = Column(Integer, default=60)
    ocr_engine = Column(String(50), default='paddleocr')
    keywords = Column(Text) # JSON string
    capture_region = Column(Text) # JSON string
    reference_images = Column(Text) # JSON string
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="config")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    detected_keyword = Column(String(255))
    screenshot_path = Column(String(255))
    detection_method = Column(String(50))
    similarity_score = Column(Float)
    alert_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="alerts")

class MonitoringLog(Base):
    __tablename__ = "monitoring_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    result_status = Column(String(50)) # SUCCESS, DETECTED, FAILED
    details = Column(Text)
    screenshot_path = Column(String(255))
    check_time = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="logs")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
