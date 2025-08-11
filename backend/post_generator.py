import openai
from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from database import Topic, LinkedInPost
from config import settings
import logging
import json

logger = logging.getLogger(__name__)


class LinkedInPostGenerator:
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    def generate_post(self, db: Session, topic_ids: List[int]) -> Dict:
        # Fetch topics
        topics = db.query(Topic).filter(Topic.id.in_(topic_ids)).all()
        
        if not topics:
            logger.error("No topics found for post generation")
            return None
        
        # Prepare context
        context = self._prepare_context(topics)
        
        # Generate post using OpenAI
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            post_content = response.choices[0].message.content
            
            # Parse the structured response
            post_data = self._parse_post_content(post_content)
            
            # Ensure proper attribution
            sources = [topic.url for topic in topics]
            post_data["sources"] = sources
            
            # Add attribution to content
            attribution = "\n\nSources:\n" + "\n".join([f"• {url}" for url in sources])
            full_content = f"{post_data['hook']}\n\n{post_data['insight']}\n\n{post_data['takeaway']}\n\n{post_data['cta']}{attribution}"
            
            # Validate length
            char_count = len(full_content)
            if char_count < settings.min_post_length or char_count > settings.max_post_length:
                logger.warning(f"Post length {char_count} outside bounds, regenerating...")
                return self._regenerate_with_length_constraint(db, topic_ids, char_count)
            
            # Save to database
            linkedin_post = LinkedInPost(
                topic_ids=topic_ids,
                content=full_content,
                hook=post_data["hook"],
                insight=post_data["insight"],
                takeaway=post_data["takeaway"],
                cta=post_data["cta"],
                sources=sources,
                created_at=datetime.utcnow(),
                status="queued"
            )
            
            db.add(linkedin_post)
            db.commit()
            
            logger.info(f"Generated LinkedIn post with {char_count} characters")
            
            return {
                "id": linkedin_post.id,
                "content": full_content,
                "char_count": char_count,
                "topics": [t.title for t in topics]
            }
            
        except Exception as e:
            logger.error(f"Error generating post: {str(e)}")
            return None
    
    def _get_system_prompt(self) -> str:
        return """You are an expert Android developer and LinkedIn content creator. Generate engaging LinkedIn posts about Android development trends.

CRITICAL RULES:
1. NEVER copy text verbatim from sources
2. ALWAYS write original insights
3. ALWAYS maintain professional tone
4. Focus on value for Android developers

Generate a structured post with these components:
- HOOK: Attention-grabbing opening (1-2 lines)
- INSIGHT: Main technical insight or trend analysis (3-4 lines)
- TAKEAWAY: Practical advice or key learning (2-3 lines)
- CTA: Call to action encouraging discussion (1 line)

Target length: 900-1500 characters total
Include relevant hashtags: #AndroidDev #Kotlin #MobileDev

Format your response as JSON:
{
    "hook": "...",
    "insight": "...",
    "takeaway": "...",
    "cta": "..."
}"""
    
    def _prepare_context(self, topics: List[Topic]) -> str:
        context = "Create a LinkedIn post based on these trending Android development topics:\n\n"
        
        for i, topic in enumerate(topics, 1):
            context += f"{i}. {topic.title}\n"
            if topic.content:
                context += f"   Context: {topic.content[:200]}...\n"
            context += f"   Engagement: {topic.score} points, {topic.engagement} comments\n"
            context += f"   Source: {topic.source}\n\n"
        
        context += "\nCreate an original post that synthesizes these trends. DO NOT copy text directly."
        
        return context
    
    def _parse_post_content(self, content: str) -> Dict:
        try:
            # Try to parse as JSON first
            data = json.loads(content)
            return {
                "hook": data.get("hook", ""),
                "insight": data.get("insight", ""),
                "takeaway": data.get("takeaway", ""),
                "cta": data.get("cta", "")
            }
        except:
            # Fallback to text parsing
            lines = content.split("\n")
            return {
                "hook": lines[0] if lines else "",
                "insight": "\n".join(lines[1:4]) if len(lines) > 1 else "",
                "takeaway": "\n".join(lines[4:6]) if len(lines) > 4 else "",
                "cta": lines[-1] if lines else ""
            }
    
    def _regenerate_with_length_constraint(self, db: Session, topic_ids: List[int], current_length: int) -> Dict:
        # Implement length-constrained regeneration
        logger.info(f"Regenerating post with length constraint (current: {current_length})")
        # For now, return the original attempt
        return self.generate_post(db, topic_ids)