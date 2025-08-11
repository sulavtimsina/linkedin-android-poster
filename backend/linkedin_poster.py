import httpx
import logging
from datetime import datetime
from typing import Optional, Dict
from sqlalchemy.orm import Session
from database import LinkedInPost
from config import settings

logger = logging.getLogger(__name__)


class LinkedInPoster:
    def __init__(self):
        self.access_token = settings.linkedin_access_token
        self.person_urn = settings.linkedin_person_urn
        self.api_url = "https://api.linkedin.com/v2"
        
    def has_credentials(self) -> bool:
        return bool(self.access_token and self.person_urn)
    
    async def post_to_linkedin(self, db: Session, post_id: int) -> Dict:
        if not self.has_credentials():
            logger.warning("LinkedIn credentials not configured")
            return {
                "success": False,
                "message": "LinkedIn credentials not configured. Use the Copy button instead."
            }
        
        # Get post from database
        post = db.query(LinkedInPost).filter(LinkedInPost.id == post_id).first()
        
        if not post:
            return {"success": False, "message": "Post not found"}
        
        if post.status == "posted":
            return {"success": False, "message": "Post already published"}
        
        try:
            # Prepare LinkedIn API request
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            payload = {
                "author": f"urn:li:person:{self.person_urn}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": post.content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/ugcPosts",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 201:
                    # Successfully posted
                    response_data = response.json()
                    post_urn = response_data.get("id", "")
                    
                    post.status = "posted"
                    post.posted_at = datetime.utcnow()
                    post.linkedin_post_id = post_urn
                    db.commit()
                    
                    logger.info(f"Successfully posted to LinkedIn: {post_urn}")
                    
                    return {
                        "success": True,
                        "message": "Successfully posted to LinkedIn",
                        "post_id": post_urn,
                        "url": self._get_post_url(post_urn)
                    }
                else:
                    error_msg = f"LinkedIn API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    
                    post.status = "failed"
                    post.error_message = error_msg
                    db.commit()
                    
                    return {
                        "success": False,
                        "message": error_msg
                    }
                    
        except Exception as e:
            error_msg = f"Error posting to LinkedIn: {str(e)}"
            logger.error(error_msg)
            
            post.status = "failed"
            post.error_message = error_msg
            db.commit()
            
            return {
                "success": False,
                "message": error_msg
            }
    
    def _get_post_url(self, post_urn: str) -> str:
        # Convert URN to URL (approximate - LinkedIn doesn't provide direct URLs)
        post_id = post_urn.split(":")[-1] if post_urn else ""
        return f"https://www.linkedin.com/feed/update/{post_urn}"
    
    def validate_credentials(self) -> bool:
        if not self.has_credentials():
            return False
        
        try:
            # Test API access
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            with httpx.Client() as client:
                response = client.get(
                    f"{self.api_url}/me",
                    headers=headers,
                    timeout=10
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error validating LinkedIn credentials: {str(e)}")
            return False