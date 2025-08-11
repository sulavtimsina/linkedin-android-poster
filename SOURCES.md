# Content Sources & Configuration

This document details the content sources, filtering criteria, and quality controls used by the LinkedIn Android Poster.

## Reddit Sources

### Primary Subreddits

| Subreddit | Status | Focus | Min Score | Min Comments |
|-----------|---------|-------|-----------|--------------|
| **r/androiddev** | Active | Professional Android development | 50 | 5 |
| **r/kotlin** | Active | Kotlin language (Android-focused) | 30 | 5 |
| **r/android** | Selective | General Android (dev content only) | 100 | 5 |
| **r/mobiledev** | Active | Mobile development | 50 | 5 |

### Quality Filters

#### **Include Posts With:**
- **Technical Keywords**: jetpack compose, kotlin, android studio, gradle, coroutines, flow, mvvm, architecture, performance
- **Educational Content**: tutorial, guide, best practice, tip, trick, testing, release, update
- **Professional Topics**: material design, api, dependency injection, dagger, hilt, retrofit, room, firebase
- **Sufficient Engagement**: Minimum upvotes and comments (see table above)
- **Recent Activity**: Posts from hot/trending or top of the week

#### **Exclude Posts With:**
- **Help/Support**: "help", "error", "issue", "problem", "stuck", "not working", "crash", "bug"
- **Beginner Questions**: "how do i", "how to fix", "newbie", "beginner question", "eli5"
- **Academic**: "homework", "assignment"
- **Low Engagement**: Below minimum score/comment thresholds
- **Sticky Posts**: Pinned moderator posts

### Content Prioritization

1. **Hot Posts** from r/androiddev (checks 20 posts)
2. **Top Weekly Posts** from r/androiddev (checks 20 posts)
3. **Hot Posts** from r/kotlin (checks 15 posts, Android-related only)
4. **Fallback**: Other configured subreddits

## X (Twitter) Sources

### Hashtags Monitored
- `#AndroidDev` - Primary Android development hashtag
- `#JetpackCompose` - Modern UI toolkit discussions
- `#KotlinAndroid` - Kotlin for Android development
- `#AndroidStudio` - IDE updates and tips
- `#MaterialDesign3` - Design system updates
- `#ComposeUI` - Compose-specific UI discussions
- `#KotlinDev` - General Kotlin development

### Key Accounts Monitored
- `@AndroidDev` - Official Android Developer account
- `@GoogleDevs` - Google Developer relations
- `@JetBrains` - Kotlin and IDE updates
- `@gradle` - Build system updates
- `@Firebase` - Backend services for mobile

### Quality Thresholds
- **Minimum Likes**: 10
- **Minimum Retweets**: 5
- **Exclude**: Hiring posts, courses, bootcamp promotions

## LinkedIn Content Strategy

### Post Types Generated
1. **Technical Insights** - Deep dives into development topics
2. **Trend Analysis** - Analysis of multiple related discussions
3. **Tool Announcements** - New libraries, updates, releases
4. **Best Practices** - Curated advice and techniques
5. **Weekly Roundups** - Compilation of top discussions

### Content Quality Score (1-10 scale)

| Factor | Weight | Description |
|--------|--------|-------------|
| Reddit Score | 20% | Upvotes and community approval |
| Engagement | 20% | Comments and discussions |
| Recency | 20% | How recent the content is |
| Keyword Relevance | 25% | Relevance to Android development |
| Content Depth | 15% | Length and technical detail |

**Minimum Quality Score**: 7.0/10 for LinkedIn posting

### LinkedIn Post Structure

#### Hook Types
- **Question**: "Ever wondered why Jetpack Compose...?"
- **Statistic**: "90% of Android developers are now using..."
- **Announcement**: "Big news for the Android community!"
- **Insight**: "Here's what I learned building..."
- **Trend**: "The Android dev community is buzzing about..."

#### Call-to-Action Types
- **Discussion**: "What's your experience with...?"
- **Educational**: "Check the links to learn more"
- **Engagement**: "Share if you found this helpful!"
- **Professional**: "Try this in your next project"

### Content Themes Targeted
- **Performance Optimization** - Memory, battery, speed improvements
- **UI/UX Best Practices** - Design patterns, accessibility, user experience
- **Architecture Patterns** - MVVM, Clean Architecture, modularization
- **Testing Strategies** - Unit testing, UI testing, TDD practices
- **New Framework Features** - Latest Android/Kotlin updates
- **Developer Productivity** - Tools, workflows, automation
- **Code Quality** - Static analysis, code review, refactoring
- **Security Best Practices** - Data protection, secure coding

## Scheduling Configuration

### Default Intervals
- **Content Fetching**: Every 6 hours (21,600 seconds)
- **Post Generation**: Every 4 hours (14,400 seconds)
- **Maximum Posts**: 3 per day

### Optimal Posting Times (UTC)
- **09:00 UTC** - Morning US East Coast
- **14:00 UTC** - Morning US West Coast
- **17:00 UTC** - End of day Europe

## Configuration Files

### `sources_config.py`
Contains all source definitions, quality filters, and content strategies.

### `.env`
Contains API credentials and basic settings:
- Reddit API credentials
- X/Twitter API tokens
- OpenAI API key
- LinkedIn API tokens (optional)
- Scheduling intervals

### `config.py`  
Application configuration and settings management.

## Customization

### Adding New Subreddits
1. Edit `REDDIT_SOURCES` in `sources_config.py`
2. Define quality criteria (min_score, keywords, etc.)
3. Test with the Reddit API test endpoint

### Adjusting Quality Filters
- Modify `keywords_required` for different technical focus
- Adjust `min_score` and `min_comments` thresholds
- Update `keywords_exclude` to filter out unwanted content

### Changing Post Themes
- Edit `content_themes` in `LINKEDIN_CONTENT`
- Modify `post_types` for different content styles
- Adjust `hashtags` for different reach strategies

## Success Metrics

### Source Quality Indicators
- **High Engagement**: Comments/upvotes ratio > 0.1
- **Technical Depth**: Posts with code snippets, architecture diagrams
- **Community Response**: Positive comment sentiment
- **Professional Relevance**: Topics applicable to production apps

### LinkedIn Performance Targets
- **Character Count**: 900-1500 characters (optimal engagement)
- **Engagement Rate**: Target 3%+ (likes, comments, shares)
- **Click-through Rate**: Target 2%+ on source links
- **Professional Value**: Educational or actionable insights

## Future Enhancements

### Planned Improvements
1. **AI-Powered Filtering**: Use ML to better identify high-quality posts
2. **Sentiment Analysis**: Filter for positive, constructive discussions
3. **Code Analysis**: Prioritize posts with actual code examples
4. **Community Signals**: Weight posts by author reputation
5. **Trend Detection**: Identify emerging topics in Android development

### Additional Sources Being Considered
- **GitHub Trending**: Popular Android repositories
- **Medium/Dev.to**: Technical blog posts
- **YouTube**: Conference talks and tutorials
- **Podcast Transcripts**: Android developer podcasts
- **Stack Overflow**: Highly-upvoted Android questions/answers