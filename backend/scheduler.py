from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from database import get_db, Settings, SystemLog
from fetchers import RedditFetcher, XFetcher
from clustering import TopicClusterer
from post_generator import LinkedInPostGenerator
from linkedin_poster import LinkedInPoster
import asyncio

logger = logging.getLogger(__name__)


class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.reddit_fetcher = RedditFetcher()
        self.x_fetcher = XFetcher()
        self.clusterer = TopicClusterer()
        self.post_generator = LinkedInPostGenerator()
        self.linkedin_poster = LinkedInPoster()
        
    def start(self):
        # Add jobs
        self.scheduler.add_job(
            func=self.fetch_topics_job,
            trigger=IntervalTrigger(seconds=self._get_fetch_interval()),
            id='fetch_topics',
            name='Fetch trending topics',
            replace_existing=True
        )
        
        self.scheduler.add_job(
            func=self.generate_and_post_job,
            trigger=IntervalTrigger(seconds=self._get_post_interval()),
            id='generate_post',
            name='Generate and post content',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    def pause(self):
        self.scheduler.pause()
        logger.info("Scheduler paused")
    
    def resume(self):
        self.scheduler.resume()
        logger.info("Scheduler resumed")
    
    def update_intervals(self, fetch_interval: int, post_interval: int):
        # Update fetch job
        self.scheduler.reschedule_job(
            'fetch_topics',
            trigger=IntervalTrigger(seconds=fetch_interval)
        )
        
        # Update post job
        self.scheduler.reschedule_job(
            'generate_post',
            trigger=IntervalTrigger(seconds=post_interval)
        )
        
        logger.info(f"Updated intervals: fetch={fetch_interval}s, post={post_interval}s")
    
    def _get_fetch_interval(self) -> int:
        db = next(get_db())
        try:
            setting = db.query(Settings).filter(Settings.key == "fetch_interval").first()
            return int(setting.value) if setting else 43200  # 12 hours default
        finally:
            db.close()
    
    def _get_post_interval(self) -> int:
        db = next(get_db())
        try:
            setting = db.query(Settings).filter(Settings.key == "post_interval").first()
            return int(setting.value) if setting else 3600  # 1 hour default
        finally:
            db.close()
    
    def _is_paused(self) -> bool:
        db = next(get_db())
        try:
            setting = db.query(Settings).filter(Settings.key == "paused").first()
            return setting.value.lower() == "true" if setting else False
        finally:
            db.close()
    
    async def fetch_topics_job(self):
        if self._is_paused():
            logger.info("Skipping fetch job - scheduler is paused")
            return
        
        db = next(get_db())
        try:
            self._log_activity(db, "fetcher", "Starting topic fetch job")
            
            # Fetch from Reddit
            reddit_topics = self.reddit_fetcher.fetch_trending_topics(db)
            logger.info(f"Fetched {len(reddit_topics)} topics from Reddit")
            
            # Fetch from X
            x_topics = await self.x_fetcher.fetch_trending_topics(db)
            logger.info(f"Fetched {len(x_topics)} topics from X")
            
            # Cluster and rank topics
            top_topics = self.clusterer.cluster_and_rank_topics(db)
            logger.info(f"Clustered topics, got {len(top_topics)} top topics")
            
            self._log_activity(
                db, "fetcher", 
                f"Fetch job completed. Reddit: {len(reddit_topics)}, X: {len(x_topics)}, Top: {len(top_topics)}"
            )
            
        except Exception as e:
            error_msg = f"Error in fetch job: {str(e)}"
            logger.error(error_msg)
            self._log_activity(db, "fetcher", error_msg, level="ERROR")
        finally:
            db.close()
    
    async def generate_and_post_job(self):
        if self._is_paused():
            logger.info("Skipping post job - scheduler is paused")
            return
        
        db = next(get_db())
        try:
            self._log_activity(db, "poster", "Starting post generation job")
            
            # Get top ranked topics for post generation
            from .database import Topic
            top_topics = db.query(Topic).filter(
                Topic.processed == True,
                Topic.rank_score.isnot(None)
            ).order_by(Topic.rank_score.desc()).limit(3).all()
            
            if not top_topics:
                logger.info("No topics available for post generation")
                return
            
            # Generate post
            topic_ids = [t.id for t in top_topics]
            post_data = self.post_generator.generate_post(db, topic_ids)
            
            if not post_data:
                logger.error("Failed to generate post")
                return
            
            # Try to post to LinkedIn if credentials are available
            if self.linkedin_poster.has_credentials():
                result = await self.linkedin_poster.post_to_linkedin(db, post_data["id"])
                
                if result["success"]:
                    self._log_activity(db, "poster", f"Successfully posted to LinkedIn: {result.get('post_id')}")
                else:
                    self._log_activity(db, "poster", f"Failed to post to LinkedIn: {result['message']}", level="ERROR")
            else:
                self._log_activity(db, "poster", "Post generated but LinkedIn credentials not configured")
            
        except Exception as e:
            error_msg = f"Error in post job: {str(e)}"
            logger.error(error_msg)
            self._log_activity(db, "poster", error_msg, level="ERROR")
        finally:
            db.close()
    
    def _log_activity(self, db: Session, component: str, message: str, level: str = "INFO"):
        log_entry = SystemLog(
            level=level,
            component=component,
            message=message
        )
        db.add(log_entry)
        try:
            db.commit()
        except:
            db.rollback()


# Global scheduler instance
scheduler = TaskScheduler()