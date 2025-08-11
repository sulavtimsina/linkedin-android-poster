from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import uvicorn

from database import get_db, init_db, Topic, LinkedInPost, SystemLog, Settings
from scheduler import scheduler
from fetchers import RedditFetcher, XFetcher
from clustering import TopicClusterer
from post_generator import LinkedInPostGenerator
from linkedin_poster import LinkedInPoster
from config import settings
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LinkedIn Android Poster", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TopicResponse(BaseModel):
    id: int
    source: str
    title: str
    url: str
    author: str
    score: float
    engagement: int
    fetched_at: datetime
    cluster_id: Optional[int]
    rank_score: Optional[float]

class PostResponse(BaseModel):
    id: int
    content: str
    status: str
    created_at: datetime
    posted_at: Optional[datetime]
    sources: List[str]

class SettingsUpdate(BaseModel):
    fetch_interval: Optional[int]
    post_interval: Optional[int]
    paused: Optional[bool]

class ManualPostRequest(BaseModel):
    topic_ids: List[int]


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    init_db()
    if not settings.debug:
        scheduler.start()
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.stop()
    logger.info("Application stopped")


# API Routes
@app.get("/")
async def root():
    return {"message": "LinkedIn Android Poster API"}

@app.get("/api/status")
async def get_status():
    linkedin_poster = LinkedInPoster()
    return {
        "scheduler_running": scheduler.scheduler.running if hasattr(scheduler, 'scheduler') else False,
        "linkedin_configured": linkedin_poster.has_credentials(),
        "reddit_configured": bool(settings.reddit_client_id),
        "x_configured": bool(settings.x_bearer_token),
        "openai_configured": bool(settings.openai_api_key)
    }

@app.get("/api/topics", response_model=List[TopicResponse])
async def get_topics(
    limit: int = 50,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Topic).order_by(Topic.fetched_at.desc())
    
    if source:
        query = query.filter(Topic.source == source)
    
    topics = query.limit(limit).all()
    return topics

@app.get("/api/posts", response_model=List[PostResponse])
async def get_posts(
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LinkedInPost).order_by(LinkedInPost.created_at.desc())
    
    if status:
        query = query.filter(LinkedInPost.status == status)
    
    posts = query.limit(limit).all()
    return posts

@app.post("/api/posts/generate")
async def generate_post(
    request: ManualPostRequest,
    db: Session = Depends(get_db)
):
    generator = LinkedInPostGenerator()
    post_data = generator.generate_post(db, request.topic_ids)
    
    if not post_data:
        raise HTTPException(status_code=400, detail="Failed to generate post")
    
    return post_data

@app.post("/api/posts/{post_id}/publish")
async def publish_post(post_id: int, db: Session = Depends(get_db)):
    linkedin_poster = LinkedInPoster()
    result = await linkedin_poster.post_to_linkedin(db, post_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(LinkedInPost).filter(LinkedInPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.status == "posted":
        raise HTTPException(status_code=400, detail="Cannot delete published posts")
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted"}

@app.put("/api/posts/{post_id}")
async def update_post(post_id: int, content: str, db: Session = Depends(get_db)):
    post = db.query(LinkedInPost).filter(LinkedInPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.status == "posted":
        raise HTTPException(status_code=400, detail="Cannot edit published posts")
    
    post.content = content
    post.status = "edited"
    db.commit()
    
    return {"message": "Post updated"}

@app.get("/api/logs")
async def get_logs(
    limit: int = 100,
    component: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SystemLog).order_by(SystemLog.timestamp.desc())
    
    if component:
        query = query.filter(SystemLog.component == component)
    
    logs = query.limit(limit).all()
    return logs

@app.get("/api/settings")
async def get_settings(db: Session = Depends(get_db)):
    settings_dict = {}
    settings_records = db.query(Settings).all()
    
    for setting in settings_records:
        settings_dict[setting.key] = setting.value
    
    return settings_dict

@app.put("/api/settings")
async def update_settings(
    settings_update: SettingsUpdate,
    db: Session = Depends(get_db)
):
    updates = settings_update.dict(exclude_unset=True)
    
    for key, value in updates.items():
        setting = db.query(Settings).filter(Settings.key == key).first()
        
        if setting:
            setting.value = str(value)
            setting.updated_at = datetime.utcnow()
        else:
            setting = Settings(key=key, value=str(value))
            db.add(setting)
    
    db.commit()
    
    # Update scheduler intervals if changed
    if 'fetch_interval' in updates or 'post_interval' in updates:
        fetch_interval = int(db.query(Settings).filter(Settings.key == "fetch_interval").first().value)
        post_interval = int(db.query(Settings).filter(Settings.key == "post_interval").first().value)
        scheduler.update_intervals(fetch_interval, post_interval)
    
    # Handle pause/resume
    if 'paused' in updates:
        if updates['paused']:
            scheduler.pause()
        else:
            scheduler.resume()
    
    return {"message": "Settings updated"}

# Manual operations
@app.post("/api/fetch-now")
async def fetch_now(background_tasks: BackgroundTasks):
    background_tasks.add_task(scheduler.fetch_topics_job)
    return {"message": "Fetch job started"}

@app.post("/api/generate-now")
async def generate_now(background_tasks: BackgroundTasks):
    background_tasks.add_task(scheduler.generate_and_post_job)
    return {"message": "Generate job started"}

@app.post("/api/scheduler/pause")
async def pause_scheduler():
    scheduler.pause()
    return {"message": "Scheduler paused"}

@app.post("/api/scheduler/resume")
async def resume_scheduler():
    scheduler.resume()
    return {"message": "Scheduler resumed"}

# Test endpoints for API verification
@app.post("/api/test-reddit")
async def test_reddit():
    """Test Reddit API by fetching a quality Android development post"""
    import praw
    from sources_config import REDDIT_SOURCES
    
    try:
        reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent
        )
        
        def is_quality_post(post, config):
            """Check if a post meets quality criteria"""
            title_lower = post.title.lower()
            content_lower = (post.selftext or "").lower()
            
            # Check minimum requirements
            if post.score < config.get("min_score", 0):
                return False
            if post.num_comments < config.get("min_comments", 0):
                return False
            if post.stickied:
                return False
            
            # Check for excluded keywords
            exclude_keywords = config.get("keywords_exclude", [])
            for keyword in exclude_keywords:
                if keyword.lower() in title_lower or keyword.lower() in content_lower:
                    return False
            
            # Check for required keywords
            required_keywords = config.get("keywords_required", [])
            if required_keywords:
                has_required = any(
                    keyword.lower() in title_lower or keyword.lower() in content_lower
                    for keyword in required_keywords
                )
                if not has_required:
                    return False
            
            return True
        
        # Try androiddev first with quality filtering
        config = REDDIT_SOURCES.get("androiddev", {})
        if config.get("enabled", True):
            subreddit = reddit.subreddit("androiddev")
            
            # Try hot posts first
            for post in subreddit.hot(limit=20):
                if is_quality_post(post, config):
                    return {
                        "title": post.title,
                        "author": str(post.author) if post.author else "deleted",
                        "score": post.score,
                        "comments": post.num_comments,
                        "content": post.selftext[:1000] if post.selftext else None,
                        "url": f"https://reddit.com{post.permalink}",
                        "subreddit": "androiddev",
                        "created": datetime.fromtimestamp(post.created_utc).isoformat(),
                        "quality_filtered": True
                    }
            
            # Try top posts of the week
            for post in subreddit.top(time_filter="week", limit=20):
                if is_quality_post(post, config):
                    return {
                        "title": post.title,
                        "author": str(post.author) if post.author else "deleted",
                        "score": post.score,
                        "comments": post.num_comments,
                        "content": post.selftext[:1000] if post.selftext else None,
                        "url": f"https://reddit.com{post.permalink}",
                        "subreddit": "androiddev",
                        "created": datetime.fromtimestamp(post.created_utc).isoformat(),
                        "quality_filtered": True,
                        "from_top_week": True
                    }
        
        # Try kotlin subreddit as backup
        config = REDDIT_SOURCES.get("kotlin", {})
        if config.get("enabled", True):
            subreddit = reddit.subreddit("kotlin")
            for post in subreddit.hot(limit=15):
                if is_quality_post(post, config):
                    return {
                        "title": post.title,
                        "author": str(post.author) if post.author else "deleted",
                        "score": post.score,
                        "comments": post.num_comments,
                        "content": post.selftext[:1000] if post.selftext else None,
                        "url": f"https://reddit.com{post.permalink}",
                        "subreddit": "kotlin",
                        "created": datetime.fromtimestamp(post.created_utc).isoformat(),
                        "quality_filtered": True
                    }
        
        # If no quality posts found, return a message
        return {
            "title": "No quality Android development posts found at this time",
            "message": "Try again later - we filter for posts with technical content, sufficient engagement, and LinkedIn-worthy topics",
            "suggestions": [
                "Posts about Jetpack Compose updates",
                "Kotlin coroutines best practices", 
                "Android architecture patterns",
                "Performance optimization techniques",
                "New API announcements"
            ]
        }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reddit API error: {str(e)}")

@app.post("/api/test-openai")
async def test_openai(request: dict):
    """Test OpenAI API by summarizing provided text"""
    import openai
    
    try:
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates concise summaries of Android development posts. Focus on the key technical points and insights."
                },
                {
                    "role": "user",
                    "content": f"Summarize this Android development post in 2-3 sentences, focusing on the key technical insights:\n\n{text}"
                }
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content.strip()
        
        return {
            "summary": summary,
            "model": "gpt-4-turbo-preview",
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")


# Serve static files (React app) - commented out for development
# app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )