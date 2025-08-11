export interface Topic {
  id: number;
  source: string;
  title: string;
  url: string;
  author: string;
  score: number;
  engagement: number;
  fetched_at: string;
  cluster_id?: number;
  rank_score?: number;
}

export interface LinkedInPost {
  id: number;
  content: string;
  status: 'queued' | 'posted' | 'failed' | 'edited';
  created_at: string;
  posted_at?: string;
  sources: string[];
}

export interface SystemLog {
  id: number;
  timestamp: string;
  level: string;
  component: string;
  message: string;
  details?: any;
}

export interface AppSettings {
  fetch_interval: string;
  post_interval: string;
  paused: string;
  max_posts_per_day: string;
  min_topic_score: string;
}

export interface AppStatus {
  scheduler_running: boolean;
  linkedin_configured: boolean;
  reddit_configured: boolean;
  x_configured: boolean;
  openai_configured: boolean;
}