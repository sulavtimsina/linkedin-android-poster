import praw
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Topic
from config import settings
import time

logger = logging.getLogger(__name__)


class RedditFetcher:
    def __init__(self):
        self.reddit = None
        self.rate_limit_reset = datetime.now()
        self.requests_made = 0
        
    def _init_reddit(self):
        if not self.reddit:
            self.reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent
            )
    
    def _check_rate_limit(self):
        if datetime.now() > self.rate_limit_reset:
            self.requests_made = 0
            self.rate_limit_reset = datetime.now() + timedelta(minutes=1)
        
        if self.requests_made >= settings.reddit_rate_limit:
            sleep_time = (self.rate_limit_reset - datetime.now()).total_seconds()
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
                self.requests_made = 0
    
    def fetch_trending_topics(self, db: Session) -> List[Dict]:
        self._init_reddit()
        topics_data = []
        
        for subreddit_name in settings.subreddits:
            try:
                self._check_rate_limit()
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Fetch hot posts
                for submission in subreddit.hot(limit=10):
                    self.requests_made += 1
                    
                    # Skip if already exists
                    existing = db.query(Topic).filter(
                        Topic.source_id == f"reddit_{submission.id}"
                    ).first()
                    
                    if existing:
                        continue
                    
                    topic = Topic(
                        source="reddit",
                        source_id=f"reddit_{submission.id}",
                        title=submission.title,
                        content=submission.selftext[:1000] if submission.selftext else None,
                        url=f"https://reddit.com{submission.permalink}",
                        author=str(submission.author) if submission.author else "deleted",
                        score=float(submission.score),
                        engagement=submission.num_comments,
                        hashtags=[f"#{subreddit_name}"],
                        fetched_at=datetime.utcnow()
                    )
                    
                    db.add(topic)
                    topics_data.append({
                        "title": topic.title,
                        "url": topic.url,
                        "score": topic.score
                    })
                    
                    logger.info(f"Fetched Reddit post: {submission.title[:50]}...")
                
                # Also fetch top posts from last 24 hours
                for submission in subreddit.top(time_filter="day", limit=5):
                    self._check_rate_limit()
                    self.requests_made += 1
                    
                    existing = db.query(Topic).filter(
                        Topic.source_id == f"reddit_{submission.id}"
                    ).first()
                    
                    if existing:
                        continue
                    
                    topic = Topic(
                        source="reddit",
                        source_id=f"reddit_{submission.id}",
                        title=submission.title,
                        content=submission.selftext[:1000] if submission.selftext else None,
                        url=f"https://reddit.com{submission.permalink}",
                        author=str(submission.author) if submission.author else "deleted",
                        score=float(submission.score),
                        engagement=submission.num_comments,
                        hashtags=[f"#{subreddit_name}"],
                        fetched_at=datetime.utcnow()
                    )
                    
                    db.add(topic)
                    topics_data.append({
                        "title": topic.title,
                        "url": topic.url,
                        "score": topic.score
                    })
                
            except Exception as e:
                logger.error(f"Error fetching from r/{subreddit_name}: {str(e)}")
                continue
        
        try:
            db.commit()
            logger.info(f"Successfully saved {len(topics_data)} new Reddit topics")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving Reddit topics: {str(e)}")
            raise
        
        return topics_data