"""
trends.py — PULSE Content Intelligence
Trend detection + animation content idea generator
Completely separate from market/signal engine
"""

import random
import requests
from datetime import datetime

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False

from config import (
    CRYPTO_KEYWORDS, LIFESTYLE_KEYWORDS,
    ANIMATION_KEYWORDS, GENERAL_TRENDING, PLATFORMS
)


# ─── Trend Detection ─────────────────────────────────────────

def get_google_trends(keywords: list[str]) -> list[dict]:
    """Fetch rising trends from Google Trends for given keywords."""
    if not PYTRENDS_AVAILABLE:
        return []
    try:
        pt = TrendReq(hl="en-US", tz=0, timeout=(10, 25))
        pt.build_payload(keywords[:5], timeframe="now 1-d", geo="")
        related = pt.related_queries()

        rising = []
        for kw in keywords[:5]:
            df = related.get(kw, {}).get("rising")
            if df is not None and not df.empty:
                for _, row in df.head(3).iterrows():
                    rising.append({
                        "keyword": row["query"],
                        "value":   int(row["value"]),
                        "source":  "Google Trends",
                        "seed":    kw,
                    })
        return rising

    except Exception as e:
        print(f"[trends] Google Trends error: {e}")
        return []


def get_dexscreener_trending_names() -> list[str]:
    """
    Pull trending Solana token names to use as content seeds.
    This feeds the CONTENT engine (not trading signals).
    """
    try:
        url = "https://api.dexscreener.com/token-boosts/top/v1"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        names = []
        for item in data:
            if item.get("chainId", "").lower() == "solana":
                desc = item.get("description", "")
                if desc:
                    names.append(desc.split()[0])  # first word / token name
        return names[:5]
    except Exception as e:
        print(f"[trends] DexScreener name fetch error: {e}")
        return []


# ─── Content Idea Generator ──────────────────────────────────

# Animation-specific idea templates per category
TEMPLATES = {
    "crypto": {
        "YouTube": [
            "The {topic} story — fully animated breakdown",
            "What actually happens when {topic} pumps (animated)",
            "I animated the {topic} crash and it's hilarious",
            "Explaining {topic} to your grandma — animation",
        ],
        "TikTok": [
            "POV: you bought {topic} before Twitter found it (animated)",
            "Animated {topic} in 30 seconds",
            "{topic} right now — animated reaction",
            "When {topic} does a 10x (stick figure edition)",
        ],
        "X (Twitter)": [
            "Animated thread: everything you need to know about {topic}",
            "I made a {topic} animation and now I can't stop",
            "{topic} explained in one animated loop",
        ],
    },
    "lifestyle": {
        "YouTube": [
            "Animated day in my life as a creator (no talking)",
            "My morning routine but make it animated",
            "What my week actually looks like — animated vlog",
            "Animator vs procrastination — day in the life",
        ],
        "TikTok": [
            "POV: animator morning routine (animated obviously)",
            "Silent animated vlog — {topic} edition",
            "Day in my life but every scene is animated",
            "What {topic} looks like when you animate it",
        ],
        "X (Twitter)": [
            "Animated my daily routine and it exposed me",
            "Nobody talks about the {topic} side of being a creator",
            "Made a 10 second animated vlog — drop yours below",
        ],
    },
    "meme": {
        "YouTube": [
            "I animated the {topic} meme and it slaps",
            "Every {topic} meme but animated — compilation",
            "Animating viral tweets about {topic}",
        ],
        "TikTok": [
            "Animated {topic} meme — tell me you've seen this",
            "I turned the {topic} meme into an animation",
            "POV: {topic} but make it animated",
            "{topic} meme animated in 60 seconds",
        ],
        "X (Twitter)": [
            "Animated the {topic} meme nobody asked for",
            "What if {topic} was an animated series",
            "I animated this so you don't have to — {topic}",
        ],
    },
    "general": {
        "YouTube": [
            "Animated explainer: why everyone is talking about {topic}",
            "{topic} in 2024 — animated summary",
            "The {topic} iceberg — animated deep dive",
        ],
        "TikTok": [
            "Wait — {topic}? Animated reaction",
            "Explaining {topic} with animations in 30 sec",
            "Nobody animated {topic} yet so I did",
        ],
        "X (Twitter)": [
            "Animated take on {topic} — thoughts?",
            "Made a quick animation about {topic}",
            "{topic} but I animated it",
        ],
    },
}

HASHTAG_SETS = {
    "crypto":    ["#memecoin", "#Solana", "#crypto", "#SOL", "#animation", "#cryptoanimation"],
    "lifestyle": ["#animatorlife", "#dayinmylife", "#contentcreator", "#animation", "#vlog"],
    "meme":      ["#meme", "#animation", "#viral", "#animatedmeme", "#funny"],
    "general":   ["#animation", "#trending", "#viral", "#contentcreator", "#animated"],
}

STATUS_LABELS = ["Rising 📈", "Hot 🔥", "Viral Early Stage ⚡", "Trending Now 🌊"]


def generate_content_ideas(topic: str, category: str = "general") -> dict:
    """
    Generate animation content ideas for a given topic and category.
    Returns structured ideas per platform.
    """
    category = category if category in TEMPLATES else "general"
    templates = TEMPLATES[category]
    hashtags  = HASHTAG_SETS.get(category, HASHTAG_SETS["general"])
    status    = random.choice(STATUS_LABELS)

    ideas = {}
    for platform in PLATFORMS:
        platform_templates = templates.get(platform, templates["TikTok"])
        selected = random.sample(platform_templates, min(2, len(platform_templates)))
        ideas[platform] = [t.format(topic=topic) for t in selected]

    return {
        "topic":    topic,
        "category": category,
        "status":   status,
        "ideas":    ideas,
        "hashtags": hashtags,
        "timestamp": datetime.utcnow().strftime("%H:%M UTC"),
    }


def get_trending_content_ideas() -> list[dict]:
    """
    Master function — pulls trends and returns content ideas.
    Called by the scheduler and /trending command.
    """
    results = []

    # 1. Google Trends — crypto keywords
    crypto_trends = get_google_trends(CRYPTO_KEYWORDS)
    for trend in crypto_trends[:2]:
        idea = generate_content_ideas(trend["keyword"], category="crypto")
        idea["trend_score"] = trend["value"]
        results.append(idea)

    # 2. Google Trends — lifestyle keywords
    lifestyle_trends = get_google_trends(LIFESTYLE_KEYWORDS)
    for trend in lifestyle_trends[:1]:
        idea = generate_content_ideas(trend["keyword"], category="lifestyle")
        idea["trend_score"] = trend["value"]
        results.append(idea)

    # 3. Google Trends — animation keywords
    anim_trends = get_google_trends(ANIMATION_KEYWORDS)
    for trend in anim_trends[:1]:
        idea = generate_content_ideas(trend["keyword"], category="meme")
        idea["trend_score"] = trend["value"]
        results.append(idea)

    # 4. Fallback — use preset keywords if Google Trends fails
    if not results:
        fallback_topics = [
            ("AI replacing jobs",   "general"),
            ("animator life",       "lifestyle"),
            ("memecoin season",     "crypto"),
            ("viral meme format",   "meme"),
        ]
        for topic, cat in fallback_topics[:2]:
            results.append(generate_content_ideas(topic, category=cat))

    return results


def get_ideas_for_topic(topic: str) -> dict:
    """Generate ideas for a specific user-requested topic."""
    # Auto-detect category
    topic_lower = topic.lower()
    if any(k in topic_lower for k in ["coin", "token", "crypto", "sol", "pump", "degen"]):
        category = "crypto"
    elif any(k in topic_lower for k in ["life", "routine", "vlog", "day", "morning"]):
        category = "lifestyle"
    elif any(k in topic_lower for k in ["meme", "funny", "viral", "trend"]):
        category = "meme"
    else:
        category = "general"

    return generate_content_ideas(topic, category=category)
