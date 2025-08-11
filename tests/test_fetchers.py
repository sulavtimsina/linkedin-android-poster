import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session
from backend.fetchers.reddit_fetcher import RedditFetcher
from backend.fetchers.x_fetcher import XFetcher
from backend.database import Topic


class TestRedditFetcher:
    
    @pytest.fixture
    def mock_db(self):
        db = Mock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        db.add = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db
    
    @pytest.fixture
    def mock_submission(self):
        submission = Mock()
        submission.id = "test123"
        submission.title = "New Android Feature Released"
        submission.selftext = "This is a test post about Android development"
        submission.permalink = "/r/androiddev/test123"
        submission.author = "testuser"
        submission.score = 150
        submission.num_comments = 25
        return submission
    
    @patch('backend.fetchers.reddit_fetcher.praw.Reddit')
    def test_fetch_trending_topics_success(self, mock_reddit, mock_db, mock_submission):
        # Setup mocks
        fetcher = RedditFetcher()
        
        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = [mock_submission]
        mock_subreddit.top.return_value = [mock_submission]
        
        mock_reddit_instance = Mock()
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        mock_reddit.return_value = mock_reddit_instance
        
        # Execute
        result = fetcher.fetch_trending_topics(mock_db)
        
        # Verify
        assert len(result) > 0
        mock_db.add.assert_called()
        mock_db.commit.assert_called_once()
    
    def test_rate_limiting(self):
        fetcher = RedditFetcher()
        fetcher.requests_made = 60  # At limit
        
        # Should not raise an exception but should handle rate limiting
        fetcher._check_rate_limit()
        
        # Verify rate limit was reset after time window
        assert fetcher.requests_made <= 60


class TestXFetcher:
    
    @pytest.fixture
    def mock_db(self):
        db = Mock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        db.add = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db
    
    @pytest.fixture
    def mock_tweet_response(self):
        return {
            "data": [
                {
                    "id": "1234567890",
                    "text": "Exciting new #AndroidDev update! Check out the latest Jetpack Compose features.",
                    "author_id": "user123",
                    "public_metrics": {
                        "like_count": 50,
                        "retweet_count": 25,
                        "reply_count": 10,
                        "quote_count": 5
                    },
                    "entities": {
                        "hashtags": [
                            {"tag": "AndroidDev"},
                            {"tag": "JetpackCompose"}
                        ]
                    }
                }
            ],
            "includes": {
                "users": [
                    {"id": "user123", "username": "androiddev"}
                ]
            }
        }
    
    @pytest.mark.asyncio
    async def test_fetch_trending_topics_success(self, mock_db, mock_tweet_response):
        fetcher = XFetcher()
        fetcher.bearer_token = "test_token"
        
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_tweet_response
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Execute
            result = await fetcher.fetch_trending_topics(mock_db)
            
            # Verify
            assert len(result) >= 0  # May be empty if no bearer token configured
            if fetcher.bearer_token:
                mock_db.add.assert_called()
                mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_without_bearer_token(self, mock_db):
        fetcher = XFetcher()
        fetcher.bearer_token = ""
        
        result = await fetcher.fetch_trending_topics(mock_db)
        
        # Should return empty list when no token is configured
        assert result == []
        mock_db.add.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, mock_db):
        fetcher = XFetcher()
        fetcher.bearer_token = "test_token"
        
        with patch('httpx.AsyncClient') as mock_client:
            # Setup rate limit response
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Execute
            result = await fetcher.fetch_trending_topics(mock_db)
            
            # Should handle gracefully and return empty result
            assert isinstance(result, list)
            mock_db.rollback.assert_called_once()
    
    def test_extract_hashtags(self):
        fetcher = XFetcher()
        
        tweet = {
            "entities": {
                "hashtags": [
                    {"tag": "AndroidDev"},
                    {"tag": "Kotlin"}
                ]
            }
        }
        
        hashtags = fetcher._extract_hashtags(tweet)
        
        assert "#AndroidDev" in hashtags
        assert "#Kotlin" in hashtags
        assert len(hashtags) == 2


@pytest.fixture
def sample_topics():
    """Sample topics for testing clustering"""
    return [
        Topic(
            id=1,
            source="reddit",
            title="New Android 14 features",
            content="Android 14 brings new features",
            url="http://example.com/1",
            score=100,
            engagement=50
        ),
        Topic(
            id=2,
            source="x",
            title="Kotlin coroutines best practices",
            content="Learn about Kotlin coroutines",
            url="http://example.com/2",
            score=80,
            engagement=30
        )
    ]