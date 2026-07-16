"""
Notifier Module (Telegram)
---------------------------
Approved jobs ko Telegram par bhejta hai.
"""

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_telegram_message(text: str) -> bool:
    """Telegram par ek message bhejta hai."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Notifier] Telegram credentials missing! Check environment variables.")
        return False
    
    try:
        response = requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        if response.status_code == 200:
            return True
        else:
            print(f"[Notifier] Telegram error: {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[Notifier] Exception: {e}")
        return False


def format_job_message(job: dict) -> str:
    """Job dict se ek sundar Telegram message banata hai."""
    budget_min = job.get('budget_min', 0)
    budget_max = job.get('budget_max', 0)
    currency = job.get('currency', '$')
    
    if budget_max and budget_max > budget_min:
        budget_str = f"{currency}{budget_min:.0f} - {currency}{budget_max:.0f}"
    elif budget_min:
        budget_str = f"{currency}{budget_min:.0f}+"
    else:
        budget_str = "Budget not specified"
    
    skills = job.get('skills', [])
    skills_str = ", ".join(skills[:5]) if skills else "Not specified"
    
    ai_reason = job.get('ai_reason') or job.get('prefilter_reason', '')
    confidence = job.get('ai_confidence', '')
    confidence_str = f" ({confidence}/10)" if confidence else ""
    
    source = "🤖 AI" if job.get('ai_decision') else "⚡ Quick Filter"
    
    message = f"""🚀 <b>New Vibe Coder Project!</b>

📌 <b>{job.get('title', 'No Title')}</b>

💰 <b>Budget:</b> {budget_str}
🏷️ <b>Skills:</b> {skills_str}
📅 <b>Posted:</b> {job.get('submitted_at', 'Unknown')}

{source} <b>Reason{confidence_str}:</b> <i>{ai_reason}</i>

🔗 <a href="{job.get('url', '#')}">Apply Now on Freelancer</a>

—————————————————"""
    
    return message


def notify_jobs(approved_jobs: list[dict]) -> int:
    """
    Approved jobs ki Telegram notifications bhejta hai.
    
    Returns:
        int: Kitni notifications successfully bheji gayi
    """
    if not approved_jobs:
        print("[Notifier] Koi approved jobs nahi hain. Koi notification nahi bhejni.")
        return 0
    
    # Summary message pehle bhejo
    summary = f"✅ <b>Agent Alert!</b> {len(approved_jobs)} naye vibe-coder project(s) mile!\n\n🕐 Check time: just now"
    send_telegram_message(summary)
    
    sent_count = 0
    for job in approved_jobs:
        message = format_job_message(job)
        success = send_telegram_message(message)
        if success:
            sent_count += 1
            print(f"[Notifier] Sent: '{job.get('title', '')[:50]}'")
        else:
            print(f"[Notifier] Failed: '{job.get('title', '')[:50]}'")
    
    return sent_count


def send_startup_message():
    """Agent start hone par ek confirmation message bhejta hai."""
    msg = (
        "<b>Freelancer Vibe Agent Started!</b>\n\n"
        "Agent ab active hai aur projects dhoondhna shuru kar raha hai.\n"
        "Har 15 minute mein check hoga.\n\n"
        "Jab bhi koi achhi project mile, main aapko yahan alert karunga!"
    )
    send_telegram_message(msg)


def send_no_jobs_found_message():
    """Agar koi naya job na mile toh status update bhejta hai."""
    msg = "🔍 Agent ne check kiya — is baar koi naya vibe-coder project nahi mila. Agle check mein dekhte hain!"
    send_telegram_message(msg)
