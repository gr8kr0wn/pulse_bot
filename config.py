import os
from dotenv import load_dotenv

load_dotenv()

# ─── Telegram ────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ─── Scheduler intervals ─────────────────────────────────────
SIGNAL_CHECK_INTERVAL = int(os.getenv("SIGNAL_CHECK_INTERVAL", 15))  # minutes
TREND_CHECK_INTERVAL  = int(os.getenv("TREND_CHECK_INTERVAL",  30))  # minutes

# ─── DexScreener ─────────────────────────────────────────────
DEXSCREENER_BASE_URL   = "https://api.dexscreener.com/latest/dex"
SOLANA_CHAIN           = "solana"

# Thresholds for signal detection
VOLUME_SPIKE_MULTIPLIER = 3.0    # 3x normal volume = spike
PRICE_CHANGE_THRESHOLD  = 20.0   # 20%+ change in 1h = signal
MIN_LIQUIDITY_USD       = 10_000 # ignore tokens under $10k liquidity
NEW_TOKEN_HOURS         = 24     # tokens launched within last 24h

# ─── Trend Keywords ──────────────────────────────────────────
# These seed the trend engine — edit freely
CRYPTO_KEYWORDS = [
    "solana", "memecoin", "SOL", "pump fun",
    "BONK", "WIF", "POPCAT", "crypto meme"
]

LIFESTYLE_KEYWORDS = [
    "day in my life", "morning routine", "vlog",
    "aesthetic", "grwm", "silent vlog"
]

ANIMATION_KEYWORDS = [
    "animation meme", "animated video", "2d animation",
    "motion graphics", "animator life", "cartoon meme"
]

GENERAL_TRENDING = [
    "trending", "viral", "tiktok trend"
]

# ─── Content Templates ───────────────────────────────────────
PLATFORMS = ["YouTube", "TikTok", "X (Twitter)"]

# ─── Website-ready API flag ───────────────────────────────────
# When True, bot also exposes a local REST API for the website
ENABLE_API = False
API_PORT   = 8000
