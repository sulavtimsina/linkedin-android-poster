import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.linkedin_poster import LinkedInPoster
from backend.database import LinkedInPost


class TestLinkedInPoster:
    
    @pytest.fixture
    def mock_db(self):
        db = Mock()
        
        # Sample LinkedIn post
        sample_post = LinkedInPost(
            id=1,
            content="Test LinkedIn post content with sources and hashtags #AndroidDev",
            status="queued",
            topic_ids=[1, 2],
            sources=["https://example.com/1", "https://example.com/2"]
        )
        
        db.query.return_value.filter.return_value.first.return_value = sample_post
        db.commit = Mock()
        db.rollback = Mock()
        
        return db
    
    def test_has_credentials_true(self):
        poster = LinkedInPoster()
        poster.access_token = "test_token"
        poster.person_urn = "test_urn"
        
        assert poster.has_credentials() is True
    
    def test_has_credentials_false(self):
        poster = LinkedInPoster()
        poster.access_token = None
        poster.person_urn = None
        
        assert poster.has_credentials() is False
    
    @pytest.mark.asyncio
    async def test_post_to_linkedin_success(self, mock_db):
        poster = LinkedInPoster()
        poster.access_token = "test_token"
        poster.person_urn = "test_person_id"
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "urn:li:share:1234567890"}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await poster.post_to_linkedin(mock_db, 1)
            
            # Verify success
            assert result["success"] is True
            assert "Successfully posted to LinkedIn" in result["message"]
            assert "post_id" in result
            
            # Verify database was updated
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_post_to_linkedin_no_credentials(self, mock_db):
        poster = LinkedInPoster()
        poster.access_token = None
        poster.person_urn = None
        
        result = await poster.post_to_linkedin(mock_db, 1)
        
        assert result["success"] is False
        assert "LinkedIn credentials not configured" in result["message"]
    
    @pytest.mark.asyncio
    async def test_post_to_linkedin_post_not_found(self):
        poster = LinkedInPoster()
        poster.access_token = "test_token"
        poster.person_urn = "test_person_id"
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = await poster.post_to_linkedin(mock_db, 999)
        
        assert result["success"] is False
        assert "Post not found" in result["message"]
    
    @pytest.mark.asyncio
    async def test_post_to_linkedin_already_posted(self, mock_db):
        poster = LinkedInPoster()
        poster.access_token = "test_token"
        poster.person_urn = "test_person_id"
        
        # Mock already posted post
        posted_post = LinkedInPost(id=1, status="posted", content="Test content")
        mock_db.query.return_value.filter.return_value.first.return_value = posted_post
        
        result = await poster.post_to_linkedin(mock_db, 1)
        
        assert result["success"] is False
        assert "Post already published" in result["message"]
    
    @pytest.mark.asyncio
    async def test_post_to_linkedin_api_error(self, mock_db):
        poster = LinkedInPoster()
        poster.access_token = "test_token"
        poster.person_urn = "test_person_id"
        
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await poster.post_to_linkedin(mock_db, 1)
            
            # Verify error handling
            assert result["success"] is False
            assert "LinkedIn API error" in result["message"]
            
            # Verify post status was updated to failed
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_post_to_linkedin_network_exception(self, mock_db):
        poster = LinkedInPoster()
        poster.access_token = "test_token"
        poster.person_urn = "test_person_id"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post.side_effect = Exception("Network error")
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await poster.post_to_linkedin(mock_db, 1)
            
            # Verify error handling
            assert result["success"] is False
            assert "Error posting to LinkedIn" in result["message"]
            
            # Verify post status was updated to failed
            mock_db.commit.assert_called_once()
    
    def test_get_post_url(self):
        poster = LinkedInPoster()
        
        post_urn = "urn:li:share:1234567890"
        url = poster._get_post_url(post_urn)
        
        assert "linkedin.com/feed/update" in url
        assert post_urn in url
    
    @patch('httpx.Client')
    def test_validate_credentials_success(self, mock_client):
        poster = LinkedInPoster()
        poster.access_token = "test_token"
        poster.person_urn = "test_person_id"
        
        # Mock successful validation
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = poster.validate_credentials()
        
        assert result is True
    
    @patch('httpx.Client')
    def test_validate_credentials_failure(self, mock_client):
        poster = LinkedInPoster()
        poster.access_token = "test_token"
        poster.person_urn = "test_person_id"
        
        # Mock failed validation
        mock_response = Mock()
        mock_response.status_code = 401
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = poster.validate_credentials()
        
        assert result is False
    
    def test_validate_credentials_no_credentials(self):
        poster = LinkedInPoster()
        poster.access_token = None
        poster.person_urn = None
        
        result = poster.validate_credentials()
        
        assert result is False