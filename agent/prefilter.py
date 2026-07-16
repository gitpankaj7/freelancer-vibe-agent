"""
Pre-Filter Module
-----------------
Ye module AI call karne SE PEHLE jobs ko fast reject/accept karta hai.
Sirf "survive" ki hui jobs Gemini ko bheji jayengi — isse cost 80%+ bachti hai.
"""

import re

# ============================================================
# REJECT Keywords — agar description mein ye hon toh seedha reject
# ============================================================
REJECT_PATTERNS = [
    # Experience requirements
    r"\b\d+\+?\s*years?\s*(of\s+)?(experience|exp)\b",
    r"\bsenior\s+(developer|engineer|programmer|dev)\b",
    r"\bjunior\s+(developer|engineer|programmer|dev)\b",
    r"\blead\s+(developer|engineer|architect)\b",
    r"\bfull[-\s]?stack\s+engineer\b",
    r"\bstaff\s+engineer\b",
    r"\bprincipal\s+engineer\b",
    r"\b(must|should|need)\s+(have|know|be)\s+proficient\b",
    r"\bproven\s+(track\s+record|experience)\b",

    # Strict Tech Stack (low-level / specialized)
    r"\bc\+\+\b",
    r"\brust\s+(programming|developer|lang)\b",
    r"\bassembly\s+language\b",
    r"\bembedded\s+systems?\b",
    r"\bfpga\b",
    r"\bverilog\b",
    r"\bsolidity\s+(expert|developer|engineer)\b",

    # DevOps / Infrastructure
    r"\bkubernetes\b",
    r"\bterraform\b",
    r"\bansible\b",
    r"\bci[\s/]?cd\s+pipeline\b",
    r"\bdevops\s+(engineer|expert)\b",

    # Certifications / Degrees
    r"\baws\s+certified\b",
    r"\bcertified\s+(professional|developer|engineer)\b",
    r"\bcomputer\s+science\s+(degree|graduate)\b",
    r"\bbs\s*\/\s*ms\s+in\b",
    r"\bphd\b",

    # Physical / Manufacturing products (vibe coder nahi kar sakta)
    r"\b(rubber|rubberized|silicone)\s+(product|item|pin|band|grip)\b",
    r"\bcardboard\b",
    r"\bpackaging\s+(design|box|material)\b",
    r"\bmanufactur(ing|er|ed)\b",
    r"\b3d\s+(print(ing|ed)?|model(ing|ling)?)\b",
    r"\bcad\s+(drawing|design|model)\b",
    r"\bprototype\s+(physical|hardware)\b",
    r"\bsupplier\b",
    r"\bwholesale\b",
    r"\baliexpress\b",

    # Data Entry & Web Scraping (Not vibe coder scope)
    r"\bdata\s+entry\b",
    r"\b(web\s+)?scrap(e|ing|er)\b",
    r"\bdata\s+scraping\b",
    r"\bcrawler\b",

    # Very large / corporate projects
    r"\blong[-\s]?term\s+(contract|commitment)\b",
    r"\bonsite\b",
    r"\bequity\s+(stake|offer)\b",
]

# ============================================================
# BOOST Keywords — agar ye hon toh ye SURE approve karega (pre-filter level pe)
# ============================================================
STRONG_APPROVE_PATTERNS = [
    r"\bbuild\s+(me\s+)?(a|an)\b",           # "build me a website"
    r"\bcreate\s+(a|an)\b",                    # "create an app"
    r"\bi\s+need\s+(a|an)\b",                 # "I need a landing page"
    r"\bsimple\s+(website|app|tool|bot|script)\b",
    r"\bone[-\s]page\b",
    r"\blanding\s+page\b",
    r"\bwordpress\b",
    r"\bshopify\b",
    r"\bwix\b",
    r"\bno[-\s]?code\b",
    r"\bautom[ae]t\w+\b",                     # automate, automation
    r"\bdashboard\b",
    r"\bchatbot\b",
    r"\btelegram\s+bot\b",
    r"\bdiscord\s+bot\b",
    r"\bwhatsapp\s+bot\b",
    r"\bai\s+(agent|bot|chatbot)\b",          # AI Agents
    r"\bvideo\s+edit(ing|or)?\b",             # Video editing
    r"\byoutube\s+video\b",
    r"\bapp\s+(development|developer|creation)\b", # App Dev
]

# Budget se bhi filter (bahut kam budget wali jobs skip)
MIN_BUDGET_USD = 30  # $30 se kam ki jobs skip


def prefilter(job: dict) -> tuple[str, str]:
    """
    Job ko pre-filter karta hai.
    
    Returns:
        ("REJECT", reason) — AI ko mat bhejo
        ("APPROVE", reason) — Strong positive signal, approve karo
        ("PASS", reason) — Neutral, AI decide karega
    """
    title = (job.get("title") or "").lower()
    description = (job.get("description") or "").lower()
    full_text = f"{title} {description}"
    budget_min = float(job.get("budget_min") or 0)

    # 1. Budget check
    if budget_min > 0 and budget_min < MIN_BUDGET_USD:
        return ("REJECT", f"Budget bahut kam hai: ${budget_min:.0f} (min ${MIN_BUDGET_USD})")

    # 2. Reject patterns check
    for pattern in REJECT_PATTERNS:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            return ("REJECT", f"Reject keyword mila: '{match.group()}'")

    # 3. Strong approve patterns check
    for pattern in STRONG_APPROVE_PATTERNS:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            return ("APPROVE", f"Strong vibe-coder signal: '{match.group()}'")

    # 4. Neutral — AI decide karega
    return ("PASS", "Neutral job, AI se final check karein")


def prefilter_jobs(jobs: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """
    Jobs list ko pre-filter karta hai.
    
    Returns:
        (approved_jobs, pass_jobs, rejected_jobs)
    """
    approved, passed, rejected = [], [], []

    for job in jobs:
        decision, reason = prefilter(job)
        job["prefilter_decision"] = decision
        job["prefilter_reason"] = reason

        if decision == "APPROVE":
            approved.append(job)
        elif decision == "PASS":
            passed.append(job)
        else:
            rejected.append(job)

    print(f"[PreFilter] Approved: {len(approved)} | AI ko bhejenge: {len(passed)} | Rejected: {len(rejected)}")
    return approved, passed, rejected
