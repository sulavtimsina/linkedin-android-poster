#!/usr/bin/env python3
import click
import asyncio
import logging
from sqlalchemy.orm import Session
from .database import get_db, init_db
from .fetchers import RedditFetcher, XFetcher
from .clustering import TopicClusterer
from .post_generator import LinkedInPostGenerator
from .linkedin_poster import LinkedInPoster
from .scheduler import scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """LinkedIn Android Poster CLI"""
    pass


@cli.command()
def init():
    """Initialize the database"""
    click.echo("Initializing database...")
    init_db()
    click.echo("Database initialized!")


@cli.command()
def fetch_now():
    """Manually fetch trending topics"""
    click.echo("Fetching trending topics...")
    
    db = next(get_db())
    try:
        reddit_fetcher = RedditFetcher()
        x_fetcher = XFetcher()
        
        # Fetch from Reddit
        reddit_topics = reddit_fetcher.fetch_trending_topics(db)
        click.echo(f"Fetched {len(reddit_topics)} topics from Reddit")
        
        # Fetch from X
        x_topics = asyncio.run(x_fetcher.fetch_trending_topics(db))
        click.echo(f"Fetched {len(x_topics)} topics from X")
        
        # Cluster topics
        clusterer = TopicClusterer()
        top_topics = clusterer.cluster_and_rank_topics(db)
        click.echo(f"Clustered and ranked topics, got {len(top_topics)} top topics")
        
        click.echo("Fetch completed!")
        
    except Exception as e:
        click.echo(f"Error during fetch: {str(e)}", err=True)
    finally:
        db.close()


@cli.command()
@click.option('--topic-ids', '-t', multiple=True, type=int, help='Topic IDs to use for post generation')
def generate_now(topic_ids):
    """Generate a LinkedIn post"""
    click.echo("Generating LinkedIn post...")
    
    db = next(get_db())
    try:
        generator = LinkedInPostGenerator()
        
        if not topic_ids:
            # Get top ranked topics
            from .database import Topic
            top_topics = db.query(Topic).filter(
                Topic.processed == True,
                Topic.rank_score.isnot(None)
            ).order_by(Topic.rank_score.desc()).limit(3).all()
            
            if not top_topics:
                click.echo("No topics available for post generation", err=True)
                return
                
            topic_ids = [t.id for t in top_topics]
            click.echo(f"Using top {len(topic_ids)} topics")
        
        post_data = generator.generate_post(db, list(topic_ids))
        
        if post_data:
            click.echo(f"Generated post with {post_data['char_count']} characters")
            click.echo(f"Post ID: {post_data['id']}")
            click.echo("\nContent preview:")
            click.echo("-" * 50)
            click.echo(post_data['content'][:200] + "..." if len(post_data['content']) > 200 else post_data['content'])
            click.echo("-" * 50)
        else:
            click.echo("Failed to generate post", err=True)
            
    except Exception as e:
        click.echo(f"Error during generation: {str(e)}", err=True)
    finally:
        db.close()


@cli.command()
@click.argument('post_id', type=int)
def post_now(post_id):
    """Post a specific LinkedIn post"""
    click.echo(f"Posting LinkedIn post {post_id}...")
    
    db = next(get_db())
    try:
        poster = LinkedInPoster()
        
        if not poster.has_credentials():
            click.echo("LinkedIn credentials not configured", err=True)
            return
        
        result = asyncio.run(poster.post_to_linkedin(db, post_id))
        
        if result["success"]:
            click.echo("Post published successfully!")
            click.echo(f"LinkedIn Post ID: {result.get('post_id', 'N/A')}")
        else:
            click.echo(f"Failed to post: {result['message']}", err=True)
            
    except Exception as e:
        click.echo(f"Error during posting: {str(e)}", err=True)
    finally:
        db.close()


@cli.command()
def start_scheduler():
    """Start the scheduler"""
    click.echo("Starting scheduler...")
    try:
        scheduler.start()
        click.echo("Scheduler started! Press Ctrl+C to stop.")
        
        # Keep the scheduler running
        try:
            while True:
                asyncio.run(asyncio.sleep(1))
        except KeyboardInterrupt:
            click.echo("\nStopping scheduler...")
            scheduler.stop()
            click.echo("Scheduler stopped.")
            
    except Exception as e:
        click.echo(f"Error starting scheduler: {str(e)}", err=True)


@cli.command()
def status():
    """Show system status"""
    from .config import settings
    
    click.echo("LinkedIn Android Poster Status")
    click.echo("=" * 40)
    
    # Check configuration
    click.echo(f"Reddit configured: {'✓' if settings.reddit_client_id else '✗'}")
    click.echo(f"X configured: {'✓' if settings.x_bearer_token else '✗'}")
    click.echo(f"OpenAI configured: {'✓' if settings.openai_api_key else '✗'}")
    
    linkedin_poster = LinkedInPoster()
    click.echo(f"LinkedIn configured: {'✓' if linkedin_poster.has_credentials() else '✗'}")
    
    # Check database
    db = next(get_db())
    try:
        from .database import Topic, LinkedInPost
        
        total_topics = db.query(Topic).count()
        total_posts = db.query(LinkedInPost).count()
        queued_posts = db.query(LinkedInPost).filter(LinkedInPost.status == 'queued').count()
        posted_posts = db.query(LinkedInPost).filter(LinkedInPost.status == 'posted').count()
        
        click.echo(f"\nDatabase Statistics:")
        click.echo(f"Total topics: {total_topics}")
        click.echo(f"Total posts: {total_posts}")
        click.echo(f"Queued posts: {queued_posts}")
        click.echo(f"Posted posts: {posted_posts}")
        
    except Exception as e:
        click.echo(f"Database error: {str(e)}", err=True)
    finally:
        db.close()


@cli.command()
@click.option('--limit', default=10, help='Number of recent items to show')
def logs(limit):
    """Show recent system logs"""
    db = next(get_db())
    try:
        from .database import SystemLog
        
        logs = db.query(SystemLog).order_by(SystemLog.timestamp.desc()).limit(limit).all()
        
        click.echo(f"Recent {len(logs)} system logs:")
        click.echo("=" * 60)
        
        for log in logs:
            timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            click.echo(f"[{timestamp}] {log.level} - {log.component}: {log.message}")
            
    except Exception as e:
        click.echo(f"Error fetching logs: {str(e)}", err=True)
    finally:
        db.close()


if __name__ == '__main__':
    cli()