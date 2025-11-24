<<<<<<< HEAD
# KrisBot (Telegram)

Small local Telegram bot. This repo contains the bot code in `KrisBot.py` and a helper
`run.sh` to start it using a `.env` file or environment variable.

Quick start

1. Create and activate a Python venv (if you haven't yet):

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt  # if you have one; otherwise install python-telegram-bot
```

2. Create `.env` from the example and add your token:

```bash
cp .env.example .env
# Edit .env and set TELEGRAM_BOT_API_TOKEN to your bot token
```

Optional scraping API

If you run or have access to a scraping backend, you can configure the bot to call it by setting:

- `TIKTOK_API_URL` — the endpoint that accepts JSON {"email","phone"} and returns either {"accounts": [...] } or a list of account objects.
- `TIKTOK_API_KEY` — optional bearer token to include as Authorization header.

If these are not set the bot will run a safe local simulation for testing.

3. Run the bot:

```bash
./run.sh
```

Security note

- Do NOT commit your real bot token into source control. Use `.env` or environment variables.
- If you accidentally committed a token to a public repo, rotate it immediately via BotFather.

Connectivity

The bot requires outbound HTTPS access to api.telegram.org (port 443). If your host
is on a restrictive network or behind a firewall/proxy, configure the network or
provide a proxy for HTTP(S) requests.
=======
- 👋 Hi, I’m @smigo21
- 👀 I’m interested in colaborating with the cyber security team 
- 🌱 I’m currently learning cyber security
- 💞️ I’m looking to collaborate on the strong and dedicated team
- 📫 How to reach me at samuelbelay81@gmail.com
- 😄 Pronouns: ...
- ⚡ Fun fact: the cyber shield
- 

<!---
smigo21/smigo21 is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->
>>>>>>> 8745559a1977651dbb52cb173da249942fc292ab
