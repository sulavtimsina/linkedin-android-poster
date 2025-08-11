from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./linkedin_poster.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50))  # reddit or x
    source_id = Column(String(255), unique=True)
    title = Column(Text)
    content = Column(Text, nullable=True)
    url = Column(Text)
    author = Column(String(255))
    score = Column(Float, default=0)
    engagement = Column(Integer, default=0)
    hashtags = Column(JSON, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    cluster_id = Column(Integer, nullable=True)
    rank_score = Column(Float, nullable=True)
    processed = Column(Boolean, default=False)


class LinkedInPost(Base):
    __tablename__ = "linkedin_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_ids = Column(JSON)  # List of related topic IDs
    content = Column(Text)
    hook = Column(Text)
    insight = Column(Text)
    takeaway = Column(Text)
    cta = Column(Text)
    sources = Column(JSON)  # List of source URLs
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="queued")  # queued, posted, failed, edited
    linkedin_post_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)


class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String(20))  # INFO, WARNING, ERROR
    component = Column(String(50))  # fetcher, generator, poster, scheduler
    message = Column(Text)
    details = Column(JSON, nullable=True)


class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Initialize default settings
    db = SessionLocal()
    try:
        default_settings = [
            ("fetch_interval", str(12 * 3600)),  # 12 hours
            ("post_interval", str(3600)),  # 1 hour
            ("paused", "false"),
            ("max_posts_per_day", "5"),
            ("min_topic_score", "10"),
        ]
        
        for key, value in default_settings:
            setting = db.query(Settings).filter(Settings.key == key).first()
            if not setting:
                setting = Settings(key=key, value=value)
                db.add(setting)
        
        db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()