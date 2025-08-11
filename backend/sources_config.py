"""
Content Sources Configuration
Define what content to fetch from Reddit and X/Twitter
"""

# Reddit Configuration
REDDIT_SOURCES = {
    "androiddev": {
        "enabled": True,
        "sort_by": ["hot", "top"],  # Try hot first, then top
        "time_filter": "week",  # For top posts: day, week, month, year, all
        "limit": 15,
        "min_score": 50,  # Minimum upvotes to consider
        "min_comments": 5,  # Minimum engagement
        "keywords_required": [  # At least one of these must be in title/content
            "jetpack compose", "kotlin", "android studio", "gradle", 
            "coroutines", "flow", "mvvm", "architecture", "performance",
            "material design", "api", "testing", "release", "update",
            "best practice", "tutorial", "guide", "tip", "trick",
            "compose ui", "navigation", "dependency injection", "dagger",
            "hilt", "retrofit", "room", "firebase", "play store"
        ],
        "keywords_exclude": [  # Skip posts with these words
            "help", "error", "issue", "problem", "stuck", "why doesn't",
            "not working", "crash", "bug", "how do i", "how to fix",
            "newbie", "beginner question", "eli5", "homework"
        ],
        "flair_exclude": [  # Skip posts with these flairs
            "Question", "Help", "Support", "Debugging"
        ]
    },
    
    "androiddev_weekly": {
        "enabled": True,
        "specific_threads": [  # Look for weekly threads
            "Weekly Questions Thread",
            "Weekly Anything Goes Thread"
        ],
        "extract_top_discussions": True  # Extract top discussions from megathreads
    },
    
    "kotlin": {
        "enabled": True,
        "sort_by": ["hot", "top"],
        "time_filter": "week",
        "limit": 10,
        "min_score": 30,
        "keywords_required": [
            "android", "compose", "coroutines", "flow", "multiplatform",
            "performance", "best practice", "release", "update", "feature"
        ],
        "keywords_exclude": [
            "help", "error", "homework", "assignment"
        ]
    },
    
    "android": {
        "enabled": True,
        "sort_by": ["top"],
        "time_filter": "week",
        "limit": 10,
        "min_score": 100,  # Higher threshold for general Android subreddit
        "keywords_required": [
            "developer", "development", "api", "sdk", "android 14", "android 15",
            "google", "announcement", "release", "beta", "preview"
        ],
        "keywords_exclude": [
            "phone", "device", "samsung", "pixel", "oneplus", "app recommendation",
            "battery", "screen", "camera", "root", "custom rom"
        ]
    },
    
    "mobiledev": {
        "enabled": True,
        "sort_by": ["top"],
        "time_filter": "week",
        "limit": 5,
        "min_score": 50,
        "keywords_required": ["android", "kotlin", "compose"]
    },
    
    "programming": {
        "enabled": False,  # Can enable if we want broader content
        "sort_by": ["top"],
        "time_filter": "week",
        "limit": 5,
        "min_score": 500,  # Very high threshold for general programming
        "keywords_required": ["android", "mobile", "kotlin"]
    }
}

# X/Twitter Configuration
X_TWITTER_SOURCES = {
    "hashtags": [
        "#AndroidDev",
        "#JetpackCompose", 
        "#KotlinAndroid",
        "#AndroidStudio",
        "#MaterialDesign3",
        "#AndroidDevelopment",
        "#ComposeUI",
        "#KotlinDev"
    ],
    
    "accounts_to_monitor": [  # Key Android dev accounts
        "@AndroidDev",
        "@GoogleDevs", 
        "@JetBrains",
        "@gradle",
        "@Firebase"
    ],
    
    "keywords": [
        "android release",
        "jetpack compose update",
        "kotlin new feature",
        "android studio",
        "material design",
        "android api",
        "compose multiplatform"
    ],
    
    "min_engagement": {
        "likes": 10,
        "retweets": 5
    },
    
    "exclude_terms": [
        "hiring", "job", "position available",
        "course", "bootcamp", "learn android in"
    ]
}

# LinkedIn Post Generation Config
LINKEDIN_CONTENT = {
    "post_types": [
        "technical_insight",  # Deep dive into a technical topic
        "trend_analysis",     # Analysis of multiple related posts
        "tool_announcement",  # New tools/libraries/updates
        "best_practices",     # Compilation of best practices
        "weekly_roundup"      # Weekly Android dev highlights
    ],
    
    "tone": "professional_engaging",  # professional, casual, technical, engaging
    
    "hashtags": [
        "#AndroidDev",
        "#MobileDevelopment", 
        "#Kotlin",
        "#JetpackCompose",
        "#AndroidDevelopment",
        "#TechInsights",
        "#MobileApps",
        "#SoftwareEngineering"
    ],
    
    "post_structure": {
        "hook_types": [
            "question",      # "Ever wondered why...?"
            "statistic",     # "90% of Android devs..."
            "announcement",  # "Big news for Android developers!"
            "insight",       # "Here's what I learned..."
            "trend"          # "The Android community is buzzing about..."
        ],
        
        "cta_types": [
            "discussion",    # "What's your experience with...?"
            "share",         # "Share if you found this helpful!"
            "follow",        # "Follow for more Android insights"
            "try",           # "Try this in your next project!"
            "learn"          # "Check the links to learn more"
        ]
    },
    
    "min_quality_score": 7.0,  # 1-10 scale for post quality
    
    "content_themes": [
        "Performance Optimization",
        "UI/UX Best Practices",
        "Architecture Patterns", 
        "Testing Strategies",
        "New Framework Features",
        "Developer Productivity",
        "Code Quality",
        "Security Best Practices"
    ]
}

# Quality Scoring Weights
QUALITY_WEIGHTS = {
    "reddit_score": 0.2,      # Reddit upvotes/score
    "engagement": 0.2,        # Comments and discussions
    "recency": 0.2,          # How recent the post is
    "keyword_relevance": 0.25, # Relevance to Android development
    "content_depth": 0.15     # Length and detail of content
}

# Scheduling Configuration
SCHEDULE_CONFIG = {
    "fetch_interval_seconds": 21600,  # 6 hours
    "post_interval_seconds": 14400,   # 4 hours
    "max_posts_per_day": 3,
    "optimal_post_times": [  # In UTC
        "09:00",  # Morning US East Coast
        "14:00",  # Morning US West Coast  
        "17:00"   # End of day Europe
    ],
    "pause_on_weekends": False
}