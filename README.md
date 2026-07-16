# 🤖 Freelancer Vibe Coder Agent

Ek free, automated agent jo Freelancer.com se **vibe coder-friendly projects** dhoondhta hai aur aapko **Telegram par alert** karta hai — har 15 minute mein. Cost: ₹0/month.

---

## Setup Guide (10 minute mein ready!)

### Step 1: Telegram Chat ID lena

1. Apne Telegram mein **@Ahabdhshhsh_bot** ko `/start` message bhejo
2. Phir browser mein ye URL kholo:
   ```
   https://api.telegram.org/bot8804453284:AAEjiPyk6TgKFcfLja5OmbD9wRrcLa3qoOg/getUpdates
   ```
3. Response mein `"chat":{"id":XXXXXXX}` dhundho — yahi aapka Chat ID hai
4. Is Chat ID ko note karo

### Step 2: Gemini API Key lena (Free)

1. [Google AI Studio](https://aistudio.google.com) par jao
2. "Get API Key" par click karo
3. Ek free API key banao aur copy karo

### Step 3: GitHub Secrets Set Karo

Apni GitHub repository mein jao → **Settings → Secrets and variables → Actions → New repository secret**

Ye 4 secrets add karo:

| Secret Name | Value |
|---|---|
| `GEMINI_API_KEY` | (Aapki Gemini API Key) |
| `TELEGRAM_BOT_TOKEN` | (Aapka Telegram Bot Token) |
| `TELEGRAM_CHAT_ID` | (Aapka Telegram Chat ID) |

### Step 4: Code GitHub par Push Karo

```bash
git init
git add .
git commit -m "Initial: Freelancer Vibe Coder Agent"
git remote add origin https://github.com/YOUR_USERNAME/freelancer-vibe-agent.git
git push -u origin main
```

### Step 5: GitHub Actions Enable Karo

1. GitHub repo mein **Actions** tab par jao
2. Agar disabled ho toh **"I understand my workflows, go ahead and enable them"** click karo
3. **Done!** Agent automatically har 15 minute mein run karega

---

## Manual Test Karna

```bash
pip install -r requirements.txt
python main.py --setup   # Telegram test message bhejega
python main.py           # Full agent run karega
```

---

## Architecture

```
Freelancer API → Pre-Filter (Code) → Gemini AI → Telegram Bot
      ↑                                               ↓
 GitHub Actions                               Aapka Phone
  (har 15 min)
```

## Cost Breakdown

| Component | Tool | Cost |
|---|---|---|
| Hosting | GitHub Actions | FREE |
| Data | Freelancer API | FREE |
| AI | Gemini 1.5 Flash | FREE (15 req/min) |
| Alerts | Telegram | FREE |
| **Total** | | **₹0/month** |
