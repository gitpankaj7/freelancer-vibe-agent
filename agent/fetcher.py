import requests
import json
import os
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from config import (
    SEEN_JOBS_FILE,
    MAX_JOBS_PER_RUN,
)

# Freelancer RSS Feeds — Only the main feed works reliably
# Freelancer ne category RSS feeds band kar diye hain
RSS_FEEDS = [
    "https://www.freelancer.com/rss.xml",   # Main feed — all latest projects
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def load_seen_jobs() -> set:
    """Previously dekhi hui job IDs load karta hai."""
    if not os.path.exists(SEEN_JOBS_FILE):
        os.makedirs(os.path.dirname(SEEN_JOBS_FILE), exist_ok=True)
        return set()
    try:
        with open(SEEN_JOBS_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("seen_ids", []))
    except Exception:
        return set()


def save_seen_jobs(seen_ids: set):
    """Dekhi hui job IDs save karta hai (max 5000 rakhta hai)."""
    os.makedirs(os.path.dirname(SEEN_JOBS_FILE), exist_ok=True)
    ids_list = list(seen_ids)[-5000:]
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(
            {"seen_ids": ids_list, "last_updated": datetime.now().isoformat()},
            f,
            indent=2,
        )


def parse_rss_feed(feed_url: str) -> list[dict]:
    """Ek RSS feed se projects parse karta hai."""
    try:
        response = requests.get(feed_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"[Fetcher] RSS error {response.status_code} for: {feed_url}")
            return []

        root = ET.fromstring(response.content)
        channel = root.find("channel")
        if channel is None:
            return []

        items = channel.findall("item")
        projects = []

        for item in items:
            title = (item.findtext("title") or "").strip()
            description = (item.findtext("description") or "").strip()
            link = (item.findtext("link") or "").strip()
            guid = (item.findtext("guid") or link).strip()
            pub_date_str = (item.findtext("pubDate") or "").strip()

            if not title or not link:
                continue

            # HTML tags description se remove karo
            import re
            description_clean = re.sub(r"<[^>]+>", "", description)[:800]

            # Category from URL extract karo
            category = feed_url.split("/jobs/")[-1].replace("/rss.xml", "").replace("-", " ").title() if "/jobs/" in feed_url else "General"

            projects.append({
                "id": guid,
                "title": title,
                "description": description_clean,
                "url": link,
                "skills": [category] if category != "General" else [],
                "budget_min": 0,
                "budget_max": 0,
                "currency": "$",
                "submitted_at": pub_date_str or "Recent",
                "source_feed": feed_url,
            })

        return projects

    except ET.ParseError as e:
        print(f"[Fetcher] XML parse error for {feed_url}: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"[Fetcher] Network error for {feed_url}: {e}")
        return []
    except Exception as e:
        print(f"[Fetcher] Unexpected error for {feed_url}: {e}")
        return []


def fetch_new_projects() -> list[dict]:
    """
    Saare RSS feeds se naye projects fetch karta hai.
    Sirf wahi projects return karta hai jo pehle nahi dekhe.
    """
    seen_ids = load_seen_jobs()
    all_projects = []
    seen_in_this_run = set()

    print(f"[Fetcher] {len(RSS_FEEDS)} RSS feeds check kar raha hoon...")

    for feed_url in RSS_FEEDS:
        category = feed_url.split("/jobs/")[-1].replace("/rss.xml", "") if "/jobs/" in feed_url else "general"
        print(f"[Fetcher] >> Checking: {category}")

        projects = parse_rss_feed(feed_url)

        for project in projects:
            pid = project["id"]

            # Skip if already seen (previous runs ya same run mein)
            if pid in seen_ids or pid in seen_in_this_run:
                continue

            seen_in_this_run.add(pid)
            seen_ids.add(pid)
            all_projects.append(project)

            # Max limit check
            if len(all_projects) >= MAX_JOBS_PER_RUN:
                break

        if len(all_projects) >= MAX_JOBS_PER_RUN:
            break

        # Respectful delay between feeds
        time.sleep(0.5)

    # Save updated seen IDs
    save_seen_jobs(seen_ids)
    print(f"[Fetcher] Total {len(all_projects)} naye projects mile!")
    return all_projects
