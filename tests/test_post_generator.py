import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from backend.post_generator import LinkedInPostGenerator
from backend.database import Topic, LinkedInPost


class TestLinkedInPostGenerator:
    
    @pytest.fixture
    def mock_db(self):
        db = Mock()
        
        # Sample topics
        sample_topics = [
            Topic(
                id=1,
                title="Android 14 Privacy Sandbox",
                content="New privacy features in Android 14",
                url="https://example.com/android14",
                source="reddit",
                score=150,
                engagement=25
            ),
            Topic(
                id=2,
                title="Kotlin Coroutines Best Practices",
                content="How to use coroutines effectively",
                url="https://example.com/kotlin",
                source="x",
                score=120,
                engagement=18
            )
        ]
        
        db.query.return_value.filter.return_value.all.return_value = sample_topics
        db.add = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        
        return db
    
    @pytest.fixture
    def mock_openai_response(self):
        return {
            "choices": [{
                "message": {
                    "content": '{\n  "hook": "🚀 Android 14 just dropped some game-changing privacy features!",\n  "insight": "The new Privacy Sandbox is revolutionizing how apps handle user data. This shift toward privacy-first development isn\'t just a trend—it\'s the future of mobile development. Developers who adapt now will build more trustworthy apps.",\n  "takeaway": "Start integrating Privacy Sandbox APIs into your current projects. Your users (and their data) will thank you for being proactive about privacy.",\n  "cta": "How are you planning to implement these privacy changes in your Android apps? Share your approach below! 👇"\n}'
                }
            }]
        }
    
    @patch('backend.post_generator.openai.OpenAI')
    def test_generate_post_success(self, mock_openai_client, mock_db, mock_openai_response):
        # Setup
        generator = LinkedInPostGenerator()
        
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = Mock()
        mock_client_instance.chat.completions.create.return_value.choices = mock_openai_response["choices"]
        mock_openai_client.return_value = mock_client_instance
        
        # Execute
        result = generator.generate_post(mock_db, [1, 2])
        
        # Verify
        assert result is not None
        assert "id" in result
        assert "content" in result
        assert "char_count" in result
        assert "topics" in result
        
        # Check character count is within bounds (900-1500)
        assert 900 <= result["char_count"] <= 1500
        
        # Verify database interactions
        mock_db.add.assert_called()
        mock_db.commit.assert_called_once()
    
    def test_generate_post_no_topics(self, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        generator = LinkedInPostGenerator()
        result = generator.generate_post(mock_db, [])
        
        assert result is None
    
    @patch('backend.post_generator.openai.OpenAI')
    def test_generate_post_openai_error(self, mock_openai_client, mock_db):
        # Setup OpenAI to raise an exception
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_client.return_value = mock_client_instance
        
        generator = LinkedInPostGenerator()
        result = generator.generate_post(mock_db, [1, 2])
        
        assert result is None
    
    def test_parse_post_content_json(self):
        generator = LinkedInPostGenerator()
        
        json_content = '{\n  "hook": "Test hook",\n  "insight": "Test insight",\n  "takeaway": "Test takeaway",\n  "cta": "Test CTA"\n}'
        
        result = generator._parse_post_content(json_content)
        
        assert result["hook"] == "Test hook"
        assert result["insight"] == "Test insight"
        assert result["takeaway"] == "Test takeaway"
        assert result["cta"] == "Test CTA"
    
    def test_parse_post_content_fallback(self):
        generator = LinkedInPostGenerator()
        
        text_content = "Test hook\nTest insight line 1\nTest insight line 2\nTest takeaway\nTest CTA"
        
        result = generator._parse_post_content(text_content)
        
        # Should fall back to text parsing
        assert "Test hook" in result["hook"]
        assert isinstance(result["insight"], str)
        assert isinstance(result["takeaway"], str)
        assert isinstance(result["cta"], str)
    
    def test_prepare_context(self):
        generator = LinkedInPostGenerator()
        
        topics = [
            Topic(
                id=1,
                title="Android 14 Features",
                content="New privacy features",
                score=150,
                engagement=25,
                source="reddit"
            )
        ]
        
        context = generator._prepare_context(topics)
        
        assert "Android 14 Features" in context
        assert "New privacy features" in context
        assert "150 points" in context
        assert "25 comments" in context
        assert "reddit" in context
        assert "DO NOT copy text directly" in context
    
    def test_get_system_prompt(self):
        generator = LinkedInPostGenerator()
        
        prompt = generator._get_system_prompt()
        
        # Check key requirements are mentioned
        assert "NEVER copy text verbatim" in prompt
        assert "ALWAYS write original insights" in prompt
        assert "900-1500 characters" in prompt
        assert "AndroidDev" in prompt
        assert "JSON" in prompt