# LinkedIn Android Poster

**Automatically curate trending Android development content and generate professional LinkedIn posts using AI.**

A comprehensive macOS application that fetches quality Android development discussions from Reddit and X/Twitter, uses OpenAI to generate engaging LinkedIn posts, and manages automated posting workflows.

![LinkedIn Android Poster Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python)
![React](https://img.shields.io/badge/React-19+-61DAFB?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=flat-square&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## What It Does

1. **Smart Content Curation**: Fetches high-quality Android development discussions from r/androiddev, r/kotlin, and other professional communities
2. **AI-Powered Generation**: Uses OpenAI GPT-4 to create engaging LinkedIn posts with professional tone and proper attribution
3. **Quality Filtering**: Advanced filtering removes help requests, basic questions, and low-engagement content
4. **Interactive Dashboard**: React-based interface for monitoring, editing, and managing your content pipeline
5. **Automated Workflow**: Configurable scheduling from 1 minute to 24 hours for hands-off operation

## Key Features

- **LinkedIn-Ready Content**: Only processes content suitable for professional audiences
- **Perfect Attribution**: Always links back to original sources and authors
- **Flexible Scheduling**: Run every few minutes for active monitoring or hours for passive curation
- **Copy Fallback**: Works without LinkedIn API - provides copy-to-clipboard functionality
- **Smart Filtering**: Focuses on technical insights, tutorials, announcements, and best practices
- **Quality Scoring**: Uses engagement, recency, and relevance to rank content

## Quick Start

### Prerequisites
- macOS (tested on 14+)
- Python 3.12+
- Node.js 18+
- Git

### 1-Minute Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/linkedin-android-poster.git
cd linkedin-android-poster

# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Configure environment
cd ..
cp .env.example .env
# Edit .env with your API keys (see API Setup section)

# Initialize database
cd backend
python -c "from database import init_db; init_db()"

# Start the application
cd ..
./start.sh
```

## API Setup (Required)

### 1. Reddit API (Free - 2 minutes)
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" → Select "script"
3. Fill in:
   - **Name**: `LinkedIn Android Poster`
   - **Redirect URI**: `http://localhost:8000`
4. Copy your **Client ID** and **Client Secret**

### 2. OpenAI API (Paid - ~$0.03 per post)
1. Sign up at https://platform.openai.com
2. Add billing method
3. Create API key at https://platform.openai.com/api-keys
4. Copy your **API key** (starts with `sk-`)

### 3. X/Twitter API (Optional)
1. Apply at https://developer.twitter.com/en/apply-for-access
2. Create app and get **Bearer Token**

### 4. LinkedIn API (Optional - for auto-posting)
1. Create app at https://www.linkedin.com/developers/apps
2. Implement OAuth2 flow for access token
3. *Note: Complex setup - app provides copy functionality as alternative*

### Configure `.env` File
```bash
# Required
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
OPENAI_API_KEY=sk-your_openai_api_key

# Optional
X_BEARER_TOKEN=your_x_bearer_token
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_PERSON_URN=your_linkedin_person_urn

# Scheduling (in seconds)
FETCH_INTERVAL=21600  # 6 hours
POST_INTERVAL=14400   # 4 hours
```

## Dashboard Usage

Once running, access your dashboard at **http://localhost:5173**

### Tabs Overview
- **Dashboard**: System status, API connections, quick actions, recent activity
- **Topics**: Browse fetched content, view quality scores, select for custom posts
- **Posts**: Manage generated posts, copy to clipboard, publish to LinkedIn
- **Settings**: Configure intervals, pause/resume scheduler, view API status

### Quick Actions
- **Test Reddit API**: Fetch a quality Android development post
- **Test OpenAI**: Generate summary of fetched content  
- **Test Both**: Run complete pipeline test
- **Fetch Now**: Immediate content fetch
- **Generate Now**: Create new LinkedIn post

## Content Quality

### What Gets Fetched
- **Technical Discussions**: Jetpack Compose, Kotlin coroutines, architecture patterns
- **Tool Updates**: Android Studio, Gradle, new library releases
- **Best Practices**: Performance optimization, testing strategies, code quality
- **Professional Insights**: Industry trends, development workflows
- **Educational Content**: Tutorials, guides, deep dives

### What Gets Filtered Out
- Help requests ("How do I fix...")
- Basic questions ("Beginner needs help")
- Device-specific issues ("My phone won't...")
- Low engagement content (< 30-50 upvotes)
- Homework/assignment requests

### Quality Thresholds
| Source | Min Score | Min Comments | Focus |
|--------|-----------|--------------|-------|
| r/androiddev | 50+ | 5+ | Professional Android development |
| r/kotlin | 30+ | 5+ | Kotlin language (Android-focused) |
| r/android | 100+ | 5+ | General Android (dev content only) |
| X/Twitter | 10+ likes | 5+ retweets | Official announcements, trends |

## CLI Commands

```bash
# Manual operations
python -m backend.cli fetch-now      # Fetch new content
python -m backend.cli generate-now   # Generate LinkedIn post
python -m backend.cli post-now 123   # Publish specific post
python -m backend.cli status         # System health check
python -m backend.cli logs --limit 50 # View recent logs

# Start scheduler daemon
python -m backend.cli start-scheduler
```

## Project Structure

```
linkedin-android-poster/
├── backend/                 # FastAPI application
│   ├── fetchers/           # Reddit & X API clients
│   ├── database.py         # SQLAlchemy models
│   ├── clustering.py       # Topic analysis & ranking  
│   ├── post_generator.py   # AI content generation
│   ├── linkedin_poster.py  # LinkedIn API client
│   ├── scheduler.py        # Background job system
│   ├── sources_config.py   # Content source configuration
│   └── main.py            # FastAPI app entry point
├── frontend/               # React dashboard
│   ├── src/               # React components & logic
│   └── public/            # Static assets
├── tests/                  # Comprehensive test suite
├── .env.example           # Environment template
├── setup.sh              # One-command setup script
├── start.sh              # Application launcher
├── SOURCES.md            # Content source documentation
└── PROJECT.md            # Detailed technical docs
```

## Testing

### Interactive Testing
Visit http://localhost:5173 for the test dashboard with:
- **Reddit API Test**: Fetch real Android development posts
- **OpenAI Test**: Generate summaries and LinkedIn content
- **Full Pipeline Test**: Complete workflow validation

### Unit Tests
```bash
# Run all tests
cd tests && python -m pytest -v

# Test with coverage
python -m pytest --cov=backend --cov-report=html

# Test specific components
python -m pytest test_fetchers.py test_clustering.py
```

## Deployment

### Local Production
```bash
# Build frontend
cd frontend && npm run build

# Start with Gunicorn
cd backend
pip install gunicorn
gunicorn main:app --workers 2 --bind 127.0.0.1:8000
```

### Cloud Deployment
- **Heroku**: See `Procfile` for easy deployment
- **Docker**: `Dockerfile` included for containerization
- **VPS**: Use provided systemd service files

## Customization

### Adding Content Sources
Edit `backend/sources_config.py`:
```python
REDDIT_SOURCES = {
    "your_subreddit": {
        "enabled": True,
        "min_score": 50,
        "keywords_required": ["android", "development"],
        "keywords_exclude": ["help", "question"]
    }
}
```

### Adjusting AI Generation
Modify `backend/post_generator.py`:
- Change GPT model (`gpt-4-turbo-preview` → `gpt-3.5-turbo`)
- Adjust tone and style prompts
- Customize post structure and length

### LinkedIn Post Templates
Configure in `sources_config.py`:
- Hook types (question, statistic, insight)
- Call-to-action styles
- Hashtag strategies
- Professional themes

## Cost Estimates

| Service | Cost | Usage |
|---------|------|-------|
| Reddit API | **Free** | Unlimited (rate limited) |
| OpenAI GPT-4 | **~$0.03/post** | ~$2-3/month at 3 posts/day |
| X/Twitter API | **Free tier** | Limited requests |
| LinkedIn API | **Free** | Rate limited |
| **Total Monthly** | **~$2-5** | For automated operation |

## Troubleshooting

### Common Issues

**"No quality posts found"**
- Quality filters may be too strict during slow periods
- Try lowering thresholds in `sources_config.py`
- Check r/kotlin or r/mobiledev as alternatives

**"OpenAI API error"**
- Verify API key is valid and has billing enabled
- Check quota limits at https://platform.openai.com/usage

**"Frontend shows blank page"**
- Ensure both backend (8000) and frontend (5173) are running
- Check browser console for errors
- Try http://127.0.0.1:8000/docs to verify backend

**"Reddit 401 Unauthorized"**
- Verify `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`
- Ensure app type is "script" not "web app"

### Getting Help
1. Check the [troubleshooting guide](PROJECT.md#troubleshooting)
2. Use the test dashboard to diagnose API issues
3. Review logs: `python -m backend.cli logs`
4. Check [detailed documentation](PROJECT.md)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Reddit API** for providing access to community discussions
- **OpenAI** for powerful AI content generation
- **Android Developer Community** for creating amazing content to curate
- **FastAPI & React** for excellent development frameworks

## Support

- **Documentation**: [PROJECT.md](PROJECT.md) | [SOURCES.md](SOURCES.md)
- **Issues**: GitHub Issues tab
- **Discussions**: GitHub Discussions for questions

---

**Built for the Android developer community**

*Transform trending Android discussions into professional LinkedIn content automatically.*