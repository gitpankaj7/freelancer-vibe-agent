"""
AI Filter Module (Gemini 1.5 Flash via REST API)
-------------------------------------------------
google-generativeai SDK ki jagah direct HTTP requests use karta hai.
Python 3.14 compatible!
"""

import time
import json
import re
import requests
from config import GEMINI_API_KEY

# Gemini REST API endpoint
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

# Rate limiting (free tier: 15 requests per minute)
DELAY_BETWEEN_REQUESTS = 4.5  # seconds

SYSTEM_PROMPT = """You are a smart filter for a "vibe coder" — someone who uses AI tools to build software, apps, and agents, and does video editing, WITHOUT needing traditional programming degrees.

A vibe coder CAN handle:
✅ Building websites, landing pages, portfolios using no-code or AI tools
✅ Creating apps (mobile or web) without needing strict engineering backgrounds
✅ Building AI agents, AI chatbots, and automations
✅ Video editing (all types: YouTube, TikTok, promos, etc.)
✅ WordPress, Shopify, Wix customization
✅ Simple API integrations, CRM setup, email automation
✅ Browser extensions and simple tools
✅ Any project focused on END RESULT (website, app, video, bot)

A vibe coder CANNOT handle:
❌ Data entry, manual copy-pasting, transcription
❌ Web scraping or data crawling tasks (strictly reject these)
❌ Projects requiring 3+ years of specific engineering experience
❌ Low-level programming (C++, Rust, Assembly)
❌ DevOps, Kubernetes, complex infrastructure setup

Respond with ONLY this JSON format (no markdown, no extra text):
{"decision": "APPROVE" or "REJECT", "confidence": 1-10, "reason": "One sentence in simple English"}"""


def ai_filter_job(job: dict) -> tuple[str, str, int]:
    """
    Single job ko Gemini REST API se check karwata hai.
    Returns: (decision, reason, confidence)
    """
    prompt = f"""{SYSTEM_PROMPT}

Project Title: {job.get('title', 'N/A')}
Description: {job.get('description', 'No description.')[:600]}
Skills: {', '.join(job.get('skills', [])) or 'Not specified'}

Should a vibe coder bid on this?"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 150,
        },
    }

    try:
        response = requests.post(
            GEMINI_API_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=20,
        )

        if response.status_code == 429:
            print(f"[AIFilter] Rate limit / quota exceeded. Approving job without AI check.")
            return ("APPROVE", "AI quota exceeded - approved by fallback", 6)

        if response.status_code != 200:
            print(f"[AIFilter] Gemini API error {response.status_code}: {response.text[:200]}")
            return ("APPROVE", f"AI unavailable (error {response.status_code}) - approved by fallback", 5)

        data = response.json()
        raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()

        # JSON parse karo
        json_match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            decision = result.get("decision", "REJECT").upper()
            reason = result.get("reason", "No reason provided")
            confidence = int(result.get("confidence", 5))

            # Low confidence approvals ko reject karo
            if decision == "APPROVE" and confidence < 6:
                return ("REJECT", f"Low confidence ({confidence}/10): {reason}", confidence)

            return (decision, reason, confidence)
        else:
            return ("REJECT", "AI response parse nahi hua", 0)

    except Exception as e:
        print(f"[AIFilter] Error: {e}")
        return ("REJECT", f"AI error: {str(e)[:80]}", 0)


def ai_filter_jobs(jobs: list[dict]) -> list[dict]:
    """
    Multiple jobs ko AI se filter karta hai with rate limiting.
    Sirf APPROVE hue jobs return karta hai.
    """
    if not jobs:
        return []

    print(f"[AIFilter] {len(jobs)} jobs ko Gemini se check kar raha hoon...")
    approved = []

    for i, job in enumerate(jobs):
        decision, reason, confidence = ai_filter_job(job)
        job["ai_decision"] = decision
        job["ai_reason"] = reason
        job["ai_confidence"] = confidence

        status = "[APPROVED]" if decision == "APPROVE" else "[REJECTED]"
        print(f"[AIFilter] [{i+1}/{len(jobs)}] {status} '{job['title'][:50]}' ({confidence}/10)")

        if decision == "APPROVE":
            approved.append(job)

        # Rate limiting (sirf agar aur jobs hain)
        if i < len(jobs) - 1:
            time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"[AIFilter] Done: {len(approved)}/{len(jobs)} approved!")
    return approved
