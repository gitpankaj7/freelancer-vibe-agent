"""
Main Entry Point
-----------------
Ye file agent ka poora flow run karta hai:
1. Fetch → 2. PreFilter → 3. AI Filter → 4. Notify
"""

import sys
import os

# Agent module path
sys.path.insert(0, os.path.dirname(__file__))

# Local .env file load karo (GitHub Actions mein ye skip ho jaayega)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from agent.fetcher import fetch_new_projects
from agent.prefilter import prefilter_jobs
from agent.ai_filter import ai_filter_jobs
from agent.notifier import notify_jobs, send_startup_message
from config import GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def validate_config():
    """Check karo ki saari required keys set hain."""
    missing = []
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_CHAT_ID:
        missing.append("TELEGRAM_CHAT_ID")

    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please set these in your .env file or GitHub Secrets.")
        sys.exit(1)

    print("[OK] All credentials found! (Freelancer RSS - no key needed)")


def run_agent():
    """Main agent pipeline run karta hai."""
    print("=" * 60)
    print("[AGENT] Freelancer Vibe Coder Agent - Starting...")
    print("=" * 60)
    
    # Step 0: Config validate karo
    validate_config()
    
    # Step 1: Fetch new projects
    print("\n[STEP 1] Freelancer se projects fetch kar raha hoon...")
    new_jobs = fetch_new_projects()
    
    if not new_jobs:
        print("[INFO] Koi naye projects nahi mile. Agent ka kaam khatam.")
        return
    
    print(f"[OK] {len(new_jobs)} naye projects mile!\n")
    
    # Step 2: Pre-filter (fast, free)
    print("[STEP 2] Code-based pre-filter laga raha hoon...")
    approved_by_code, needs_ai_check, rejected = prefilter_jobs(new_jobs)
    
    # Step 3: AI Filter (sirf "PASS" wale jobs ke liye)
    ai_approved = []
    if needs_ai_check:
        print(f"\n[STEP 3] {len(needs_ai_check)} jobs ko Gemini AI se check karwa raha hoon...")
        ai_approved = ai_filter_jobs(needs_ai_check)
    else:
        print("\n[STEP 3] AI check skip - sab pre-filter se hi handle ho gaya!")
    
    # Combine all approved jobs
    all_approved = approved_by_code + ai_approved
    
    print(f"\n[RESULTS]")
    print(f"   Approved (code): {len(approved_by_code)}")
    print(f"   Approved (AI):   {len(ai_approved)}")
    print(f"   Rejected:        {len(rejected)}")
    print(f"   Total to send:   {len(all_approved)}")

    # Step 4: Telegram notifications
    print(f"\n[STEP 4] Telegram par {len(all_approved)} alerts bhej raha hoon...")
    sent = notify_jobs(all_approved)
    
    print(f"\n[DONE] {sent}/{len(all_approved)} notifications bheji gayi.")
    print("=" * 60)


if __name__ == "__main__":
    # Special command: --setup (pehli baar test ke liye)
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        print("[SETUP] Setup test mode...")
        validate_config()
        send_startup_message()
        print("[OK] Telegram test message bheja! Apna Telegram check karo.")
    else:
        run_agent()
