from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import Topic
import logging

logger = logging.getLogger(__name__)


class TopicClusterer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def cluster_and_rank_topics(self, db: Session) -> List[Dict]:
        # Get unprocessed topics from last 24 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        topics = db.query(Topic).filter(
            Topic.fetched_at >= cutoff_time,
            Topic.processed == False
        ).all()
        
        if len(topics) < 3:
            logger.info("Not enough topics to cluster")
            return []
        
        # Prepare text data
        texts = []
        for topic in topics:
            text = f"{topic.title} {topic.content or ''}"
            texts.append(text)
        
        # Vectorize texts
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
        except Exception as e:
            logger.error(f"Error vectorizing topics: {str(e)}")
            return []
        
        # Determine optimal number of clusters
        n_clusters = min(max(3, len(topics) // 5), 10)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)
        
        # Calculate cluster centers and topic distances
        cluster_centers = kmeans.cluster_centers_
        
        # Assign cluster IDs and calculate rank scores
        clustered_topics = []
        
        for i, topic in enumerate(topics):
            cluster_id = int(cluster_labels[i])
            
            # Calculate distance to cluster center
            topic_vector = tfidf_matrix[i].toarray()
            center_vector = cluster_centers[cluster_id].reshape(1, -1)
            similarity = cosine_similarity(topic_vector, center_vector)[0][0]
            
            # Calculate rank score based on multiple factors
            recency_score = 1.0 / (1.0 + (datetime.utcnow() - topic.fetched_at).total_seconds() / 3600)
            engagement_score = np.log1p(topic.score + topic.engagement)
            
            # Combined rank score
            rank_score = (
                similarity * 0.3 +  # Relevance to cluster
                recency_score * 0.3 +  # Recency
                min(engagement_score / 10, 1.0) * 0.4  # Engagement (capped)
            )
            
            topic.cluster_id = cluster_id
            topic.rank_score = float(rank_score)
            topic.processed = True
            
            clustered_topics.append({
                "id": topic.id,
                "title": topic.title,
                "cluster_id": cluster_id,
                "rank_score": rank_score,
                "source": topic.source,
                "url": topic.url
            })
        
        try:
            db.commit()
            logger.info(f"Successfully clustered {len(topics)} topics into {n_clusters} clusters")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving clustered topics: {str(e)}")
            raise
        
        # Return top topics from each cluster
        top_topics = self._get_top_topics_per_cluster(clustered_topics, top_n=2)
        return top_topics
    
    def _get_top_topics_per_cluster(self, topics: List[Dict], top_n: int = 2) -> List[Dict]:
        # Group by cluster
        clusters = {}
        for topic in topics:
            cluster_id = topic["cluster_id"]
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(topic)
        
        # Get top N from each cluster
        top_topics = []
        for cluster_id, cluster_topics in clusters.items():
            sorted_topics = sorted(cluster_topics, key=lambda x: x["rank_score"], reverse=True)
            top_topics.extend(sorted_topics[:top_n])
        
        # Sort all top topics by rank score
        top_topics.sort(key=lambda x: x["rank_score"], reverse=True)
        
        return top_topics