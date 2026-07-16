import os

# ============================================================
# CONFIG — Saari keys environment variables se aayengi
# GitHub Actions mein ye "Secrets" ke roop mein store honge
# ============================================================

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Google Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# NOTE: Freelancer API key nahi chahiye!
# Hum public RSS feeds use karte hain — completely FREE & no login needed.

# Agent Settings
CHECK_INTERVAL_MINUTES = 15       # Har kitne minute mein check ho
MAX_JOBS_PER_RUN = 50             # Ek run mein max kitni jobs fetch karein
SEEN_JOBS_FILE = "data/seen_jobs.json"  # Already dekhi hui jobs ka record
