from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Reddit
    reddit_client_id: str = os.getenv("REDDIT_CLIENT_ID", "")
    reddit_client_secret: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_user_agent: str = os.getenv("REDDIT_USER_AGENT", "AndroidTrendFetcher/1.0")
    
    # X (Twitter)
    x_bearer_token: str = os.getenv("X_BEARER_TOKEN", "")
    
    # LinkedIn
    linkedin_access_token: Optional[str] = os.getenv("LINKEDIN_ACCESS_TOKEN")
    linkedin_person_urn: Optional[str] = os.getenv("LINKEDIN_PERSON_URN")
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Schedule
    fetch_interval: int = int(os.getenv("FETCH_INTERVAL", "43200"))  # 12 hours
    post_interval: int = int(os.getenv("POST_INTERVAL", "3600"))  # 1 hour
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./linkedin_poster.db")
    
    # App
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Rate limits
    reddit_rate_limit: int = 60  # requests per minute
    x_rate_limit: int = 300  # requests per 15 minutes
    linkedin_rate_limit: int = 100  # posts per day
    
    # Content settings
    min_post_length: int = 900
    max_post_length: int = 1500
    
    # Subreddits and hashtags
    subreddits: list = ["androiddev", "android", "Kotlin", "JetpackCompose"]
    x_hashtags: list = ["#AndroidDev", "#Kotlin", "#JetpackCompose", "#AndroidDevelopment", "#MobileApp"]
    
    class Config:
        env_file = ".env"


settings = Settings()