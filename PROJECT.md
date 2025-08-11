# LinkedIn Android Poster - Complete Project Guide

A comprehensive macOS application that automatically curates Android development content from Reddit and X/Twitter, generates professional LinkedIn posts using AI, and manages automated posting workflows.

## 📋 Table of Contents
- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Content Sources](#-content-sources)
- [API Setup](#-api-setup)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)

## Overview

### What It Does
1. **Content Curation**: Fetches trending Android development discussions from Reddit and X/Twitter
2. **AI Enhancement**: Uses OpenAI GPT-4 to generate professional LinkedIn posts with proper attribution
3. **Smart Filtering**: Applies quality filters to ensure only LinkedIn-worthy content is processed
4. **Dashboard Control**: React-based interface for monitoring, editing, and managing content
5. **Automated Workflow**: Configurable scheduling for hands-off operation

### Key Features
- **Quality-First Approach**: Advanced filtering removes help requests, basic questions, and low-engagement posts
- **Professional Tone**: AI generates content appropriate for professional LinkedIn audiences
- **Source Attribution**: Always links back to original discussions and authors
- **Flexible Scheduling**: Configurable intervals from 1 minute to 24 hours
- **Manual Override**: Full manual control for immediate operations
- **Copy Fallback**: Works without LinkedIn API - provides copy-to-clipboard functionality

## Quick Start

### Prerequisites
- **macOS** (tested on macOS 14+)
- **Python 3.12+**
- **Node.js 18+**
- **npm or yarn**

### 1. Installation
```bash
# Clone repository
git clone <your-repo>
cd linkedin-android-poster

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies  
cd ../frontend
npm install

# Return to project root
cd ..
```

### 2. Configuration
```bash
# Create environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

### 3. Database Setup
```bash
# Initialize SQLite database
cd backend
python -c "from database import init_db; init_db()"
```

### 4. Start Application
```bash
# Option 1: Use startup script
./start.sh

# Option 2: Manual start
# Terminal 1 - Backend
cd backend && python -m uvicorn main:app --reload

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

### 5. Access Application
- **Dashboard**: http://localhost:5173
- **API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    React Dashboard                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │  Topics     │ │    Posts    │ │  Settings   │      │
│  │  Browser    │ │    Queue    │ │  Control    │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
└─────────────────────────────────────────────────────────┘
                           │ HTTP API
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │   Content   │ │     AI      │ │  LinkedIn   │      │
│  │  Fetchers   │ │ Generator   │ │   Poster    │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │  Clustering │ │  Scheduler  │ │    Logs     │      │
│  │   Engine    │ │   System    │ │  Manager    │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                     Data Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │   Topics    │ │    Posts    │ │    Logs     │      │
│  │  (SQLite)   │ │  (SQLite)   │ │  (SQLite)   │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                  External APIs                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │   Reddit    │ │ X/Twitter   │ │   OpenAI    │      │
│  │     API     │ │     API     │ │     API     │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
│                 ┌─────────────┐                       │
│                 │  LinkedIn   │                       │
│                 │     API     │                       │
│                 └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

### Tech Stack

#### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM with SQLite
- **APScheduler** - Background job scheduling
- **PRAW** - Python Reddit API wrapper
- **OpenAI SDK** - AI content generation
- **Scikit-learn** - Content clustering and ranking

#### Frontend
- **Vite** - Fast build tool and dev server
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Axios** - HTTP client
- **Lucide React** - Icon library

#### Database Schema
- **Topics** - Fetched content with metadata and clustering data
- **LinkedInPosts** - Generated posts with status tracking
- **SystemLogs** - Application logs and error tracking
- **Settings** - Configurable application parameters

## Content Sources

### Reddit Sources
- **r/androiddev** - Primary professional Android development community
- **r/kotlin** - Kotlin language discussions (Android-focused filtering)
- **r/android** - General Android (developer content only)
- **r/mobiledev** - Cross-platform mobile development

### X/Twitter Sources
- **Hashtags**: #AndroidDev, #JetpackCompose, #KotlinAndroid, #AndroidStudio
- **Accounts**: @AndroidDev, @GoogleDevs, @JetBrains, @gradle

### Quality Filtering
- **Technical Focus**: Keywords like "jetpack compose", "kotlin", "architecture", "performance"
- **Engagement Thresholds**: Minimum upvotes (30-100) and comments (5+)
- **Content Exclusions**: Help requests, basic questions, homework, device issues
- **Professional Relevance**: Topics applicable to production Android development

*See [SOURCES.md](SOURCES.md) for complete filtering criteria.*

## API Setup

### Required APIs

#### 1. Reddit API (Free)
```bash
# 1. Go to https://www.reddit.com/prefs/apps
# 2. Create "script" type app
# 3. Get Client ID and Secret
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

#### 2. OpenAI API (Paid - ~$0.03 per post)
```bash
# 1. Sign up at https://platform.openai.com
# 2. Add payment method
# 3. Create API key
OPENAI_API_KEY=sk-your-api-key
```

#### 3. X/Twitter API (Optional - requires approval)
```bash
# 1. Apply at https://developer.twitter.com
# 2. Create app and get Bearer Token
X_BEARER_TOKEN=your_bearer_token
```

#### 4. LinkedIn API (Optional - complex OAuth)
```bash
# 1. Create LinkedIn Developer app
# 2. Implement OAuth2 flow
# 3. Get access token and person URN
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_PERSON_URN=your_person_urn
```

### API Cost Estimates
- **Reddit**: Free (rate limited)
- **X/Twitter**: Free tier available (limited requests)
- **OpenAI**: ~$0.03 per generated post (GPT-4 Turbo)
- **LinkedIn**: Free API access (rate limited)

## Configuration

### Environment Variables (.env)
```bash
# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=AndroidTrendFetcher/1.0

# X (Twitter) API  
X_BEARER_TOKEN=your_x_bearer_token

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# LinkedIn API (optional)
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_PERSON_URN=your_linkedin_person_urn

# Scheduling
FETCH_INTERVAL=21600  # 6 hours
POST_INTERVAL=14400   # 4 hours

# Database
DATABASE_URL=sqlite:///./linkedin_poster.db

# App Settings
DEBUG=False
LOG_LEVEL=INFO
```

### Content Sources (sources_config.py)
Customize subreddits, hashtags, quality filters, and content strategies.

### Dashboard Settings
- **Fetch Interval**: 1 minute to 24 hours
- **Post Interval**: 1 minute to 12 hours  
- **Scheduler Control**: Pause/resume operations
- **Manual Operations**: Immediate fetch/generate/post

## Usage Guide

### Dashboard Navigation

#### 1. Dashboard Tab
- **System Status**: API connection indicators
- **Quick Actions**: Manual fetch, generate, and refresh buttons
- **Recent Activity**: Latest posts with status indicators

#### 2. Topics Tab  
- **Content Browser**: View fetched Reddit and X/Twitter posts
- **Quality Indicators**: Score, engagement, and ranking metrics
- **Source Links**: Direct links to original discussions
- **Selection**: Choose topics for custom post generation

#### 3. Posts Tab
- **Queue Management**: View generated posts waiting to publish
- **Status Tracking**: Posted, queued, failed, and edited states
- **Content Preview**: Full post content with character counts
- **Actions**: Copy to clipboard, publish to LinkedIn, edit, or delete

#### 4. Settings Tab
- **Interval Controls**: Adjust fetch and post timing with sliders
- **System Configuration**: Pause/resume scheduler
- **API Status**: Connection status for all services

### Manual Operations

#### Via Dashboard
- **Fetch Now**: Immediately fetch new trending topics
- **Generate Now**: Create new post from top-ranked topics
- **Publish Post**: Send specific post to LinkedIn (if configured)

#### Via CLI  
```bash
# Manual content fetch
python -m backend.cli fetch-now

# Generate post from current topics
python -m backend.cli generate-now

# Publish specific post
python -m backend.cli post-now 123

# View system status
python -m backend.cli status

# View recent logs
python -m backend.cli logs --limit 50
```

### Content Workflow

1. **Fetching Phase** (Every 6 hours default)
   - Scan configured subreddits for new posts
   - Apply quality filters to identify LinkedIn-worthy content  
   - Query X/Twitter for relevant hashtags and accounts
   - Store topics with engagement metrics

2. **Analysis Phase** (After fetching)
   - Cluster similar topics using TF-IDF and K-means
   - Rank topics by recency, engagement, and relevance
   - Identify top candidates for LinkedIn posts

3. **Generation Phase** (Every 4 hours default)
   - Select highest-ranked topics
   - Generate LinkedIn post with AI (hook, insight, takeaway, CTA)
   - Ensure proper source attribution and character limits
   - Add to posting queue

4. **Publishing Phase** (Manual or automatic)
   - Post to LinkedIn if API configured
   - Otherwise, provide copy-to-clipboard functionality
   - Track posting status and engagement metrics

## Testing

### API Testing Dashboard
Access http://localhost:5173 for interactive testing:
- **Test Reddit API**: Fetch quality Android development posts
- **Test OpenAI API**: Generate summaries of fetched content
- **Test Full Pipeline**: Complete fetch → generate workflow

### Unit Testing
```bash
# Run all tests
cd tests && python -m pytest

# Run specific test files
python -m pytest test_fetchers.py -v
python -m pytest test_clustering.py -v  
python -m pytest test_post_generator.py -v

# Run with coverage
python -m pytest --cov=backend --cov-report=html
```

### Manual Testing
```bash
# Test individual components
python -c "from fetchers.reddit_fetcher import RedditFetcher; f = RedditFetcher(); print('Reddit OK')"
python -c "from post_generator import LinkedInPostGenerator; g = LinkedInPostGenerator(); print('OpenAI OK')"
```

## Deployment

### Production Setup
```bash
# 1. Set production environment
export DEBUG=False
export LOG_LEVEL=WARNING

# 2. Use production WSGI server
pip install gunicorn
gunicorn main:app --workers 2 --bind 127.0.0.1:8000

# 3. Build frontend for production
cd frontend
npm run build

# 4. Enable static file serving in main.py
# Uncomment the StaticFiles mount line
```

### Process Management
```bash
# Use PM2 for production process management
npm install -g pm2

# Start backend
pm2 start "gunicorn main:app --bind 127.0.0.1:8000" --name linkedin-poster-api

# Start scheduler separately if needed
pm2 start "python -m backend.cli start-scheduler" --name linkedin-poster-scheduler
```

### Database Backup
```bash
# Backup SQLite database
cp backend/linkedin_poster.db backup/linkedin_poster_$(date +%Y%m%d).db

# Automated daily backup
echo "0 2 * * * cp /path/to/linkedin_poster.db /path/to/backup/linkedin_poster_\$(date +\%Y\%m\%d).db" | crontab -
```

## 🔧 Development

### Project Structure
```
linkedin-android-poster/
├── backend/                 # FastAPI application
│   ├── fetchers/           # Reddit & X API clients
│   │   ├── reddit_fetcher.py
│   │   └── x_fetcher.py
│   ├── database.py         # SQLAlchemy models
│   ├── clustering.py       # Topic analysis & ranking
│   ├── post_generator.py   # AI content generation
│   ├── linkedin_poster.py  # LinkedIn API client
│   ├── scheduler.py        # Background job system
│   ├── sources_config.py   # Content source configuration
│   ├── config.py          # Application configuration
│   ├── main.py            # FastAPI app entry point
│   └── cli.py             # Command-line interface
├── frontend/               # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── api.ts        # API client
│   │   ├── types.ts      # TypeScript interfaces
│   │   └── App.tsx       # Main application component
│   └── public/           # Static assets
├── tests/                 # Test suite
│   ├── test_fetchers.py  # API client tests
│   ├── test_clustering.py # Analysis tests
│   ├── test_post_generator.py # AI generation tests
│   └── conftest.py       # Test configuration
├── .env.example          # Environment template
├── start.sh             # Quick start script
├── SOURCES.md           # Content source documentation
└── PROJECT.md           # This file
```

### Adding New Features

#### 1. New Content Source
```python
# 1. Add source config to sources_config.py
# 2. Create fetcher in fetchers/ directory
# 3. Add to scheduler.py
# 4. Add tests
```

#### 2. New AI Model
```python
# 1. Update post_generator.py
# 2. Add model configuration to config.py
# 3. Update cost estimates
# 4. Test with new model API
```

#### 3. New Social Platform
```python
# 1. Create new poster module (e.g., twitter_poster.py)
# 2. Add API configuration
# 3. Update dashboard UI
# 4. Add to scheduler workflow
```

### Code Style
```bash
# Format code with Black
pip install black
black backend/ tests/

# Type checking with mypy
pip install mypy
mypy backend/

# Linting with flake8
pip install flake8
flake8 backend/
```

## Troubleshooting

### Common Issues

#### "LinkedIn credentials not configured"
- **Solution**: Either configure LinkedIn API or use copy-to-clipboard functionality
- **Check**: LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN in .env

#### "No quality Android development posts found"
- **Cause**: Quality filters are too strict for current Reddit activity
- **Solution**: Lower thresholds in sources_config.py or try again later
- **Alternative**: Check r/kotlin or r/mobiledev subreddits

#### "OpenAI API error"  
- **Check**: Valid API key and sufficient credit balance
- **Solution**: Verify key at https://platform.openai.com/api-keys
- **Cost**: Ensure billing method is added

#### "Reddit API 401 Unauthorized"
- **Cause**: Invalid Reddit credentials or rate limiting
- **Solution**: Verify REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET
- **Test**: Use API test dashboard to verify connection

#### Frontend shows blank page
- **Check**: Both backend (port 8000) and frontend (port 5173) are running
- **Solution**: Refresh browser, check browser console for errors
- **Alternative**: Try http://127.0.0.1:8000/docs for backend API docs

### Debugging

#### View Logs
```bash
# Application logs
python -m backend.cli logs --limit 100

# Database logs (via dashboard)
curl http://127.0.0.1:8000/api/logs

# System logs
tail -f /var/log/linkedin-poster.log
```

#### Database Inspection
```bash
# SQLite CLI
sqlite3 backend/linkedin_poster.db

# View tables
.tables

# View recent topics
SELECT title, score, source FROM topics ORDER BY fetched_at DESC LIMIT 10;

# View post queue
SELECT id, status, created_at FROM linkedin_posts ORDER BY created_at DESC;
```

#### API Testing
```bash
# Test Reddit connection
curl -X POST http://127.0.0.1:8000/api/test-reddit

# Test OpenAI connection
curl -X POST http://127.0.0.1:8000/api/test-openai -H "Content-Type: application/json" -d '{"text":"Test summarization"}'

# Check system status
curl http://127.0.0.1:8000/api/status
```

### Performance Optimization

#### Database
- Regular cleanup of old topics (>30 days)
- Index optimization for common queries
- Consider PostgreSQL for high-volume usage

#### Memory Usage
- Monitor APScheduler job memory consumption
- Implement topic archiving for large datasets
- Consider Redis for caching frequently accessed data

#### API Rate Limits
- Reddit: 60 requests/minute (automatically handled)
- X/Twitter: 300 requests/15 minutes (automatically handled)  
- OpenAI: Varies by plan (monitor usage dashboard)
- LinkedIn: 100 posts/day (configurable limit)

## Success Metrics & Analytics

### Content Quality Indicators
- **Engagement Rate**: Comments and likes on source posts
- **Topic Relevance**: Keyword matching and technical depth
- **Community Response**: Positive sentiment in discussions
- **Professional Value**: Actionable insights for developers

### LinkedIn Performance
- **Post Engagement**: Target 3%+ engagement rate
- **Click-through Rate**: Target 2%+ on source links
- **Character Optimization**: Sweet spot 900-1500 characters
- **Hashtag Performance**: Track which hashtags drive engagement

### System Health
- **Fetch Success Rate**: >95% successful Reddit API calls
- **Generation Quality**: >90% posts meet LinkedIn standards
- **Uptime**: >99.5% scheduler availability
- **Error Rate**: <1% failed operations

---

## Support & Contributing

### Get Help
1. Check this documentation and [SOURCES.md](SOURCES.md)
2. Review troubleshooting section
3. Check system logs and error messages
4. Test API connections with built-in test dashboard

### Contributing
1. Fork repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request with clear description

### License
MIT License - see LICENSE file for details.

---

**Built for the Android developer community**