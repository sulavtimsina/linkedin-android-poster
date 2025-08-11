import httpx
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
import json

logger = logging.getLogger(__name__)


class XFetcher:
    def __init__(self):
        self.bearer_token = settings.x_bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.rate_limit_reset = datetime.now()
        self.requests_made = 0
    
    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "AndroidTrendFetcher/1.0"
        }
    
    def _check_rate_limit(self):
        if datetime.now() > self.rate_limit_reset:
            self.requests_made = 0
            self.rate_limit_reset = datetime.now() + timedelta(minutes=15)
        
        if self.requests_made >= settings.x_rate_limit:
            sleep_time = (self.rate_limit_reset - datetime.now()).total_seconds()
            if sleep_time > 0:
                logger.info(f"X API rate limit reached. Sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
                self.requests_made = 0
    
    async def fetch_trending_topics(self, db: Session) -> List[Dict]:
        if not self.bearer_token:
            logger.warning("X Bearer token not configured. Skipping X fetching.")
            return []
        
        topics_data = []
        
        async with httpx.AsyncClient() as client:
            for hashtag in settings.x_hashtags:
                try:
                    self._check_rate_limit()
                    
                    # Search for recent tweets with the hashtag
                    params = {
                        "query": f"{hashtag} -is:retweet lang:en",
                        "max_results": 20,
                        "tweet.fields": "created_at,author_id,public_metrics,entities",
                        "expansions": "author_id",
                        "user.fields": "username"
                    }
                    
                    response = await client.get(
                        f"{self.base_url}/tweets/search/recent",
                        headers=self._get_headers(),
                        params=params
                    )
                    
                    self.requests_made += 1
                    
                    if response.status_code == 200:
                        data = response.json()
                        tweets = data.get("data", [])
                        users = {u["id"]: u["username"] for u in data.get("includes", {}).get("users", [])}
                        
                        for tweet in tweets:
                            # Skip if already exists
                            existing = db.query(Topic).filter(
                                Topic.source_id == f"x_{tweet['id']}"
                            ).first()
                            
                            if existing:
                                continue
                            
                            metrics = tweet.get("public_metrics", {})
                            
                            topic = Topic(
                                source="x",
                                source_id=f"x_{tweet['id']}",
                                title=tweet["text"][:200],
                                content=tweet["text"],
                                url=f"https://twitter.com/{users.get(tweet['author_id'], 'user')}/status/{tweet['id']}",
                                author=users.get(tweet["author_id"], "unknown"),
                                score=float(metrics.get("like_count", 0) + metrics.get("retweet_count", 0) * 2),
                                engagement=metrics.get("reply_count", 0) + metrics.get("quote_count", 0),
                                hashtags=[hashtag] + self._extract_hashtags(tweet),
                                fetched_at=datetime.utcnow()
                            )
                            
                            db.add(topic)
                            topics_data.append({
                                "title": topic.title,
                                "url": topic.url,
                                "score": topic.score
                            })
                            
                            logger.info(f"Fetched X post: {tweet['text'][:50]}...")
                    
                    elif response.status_code == 429:
                        logger.warning("X API rate limit hit. Waiting...")
                        self.rate_limit_reset = datetime.now() + timedelta(minutes=15)
                        break
                    else:
                        logger.error(f"X API error: {response.status_code} - {response.text}")
                        
                except Exception as e:
                    logger.error(f"Error fetching X posts for {hashtag}: {str(e)}")
                    continue
        
        try:
            db.commit()
            logger.info(f"Successfully saved {len(topics_data)} new X topics")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving X topics: {str(e)}")
            raise
        
        return topics_data
    
    def _extract_hashtags(self, tweet: Dict) -> List[str]:
        hashtags = []
        entities = tweet.get("entities", {})
        
        for hashtag in entities.get("hashtags", []):
            hashtags.append(f"#{hashtag['tag']}")
        
        return hashtags