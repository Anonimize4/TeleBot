#!/usr/bin/env python3

import logging
import json
import os
from typing import Dict, List, Any, Optional
import asyncio
import httpx
import requests
import string
from itertools import product
import re
import hashlib

from faker import Faker

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.error import Conflict


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Define the user data file
USER_DATA_FILE = "user_data.json"


def load_user_data() -> Dict:
    """Load user data from JSON file."""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
    except json.JSONDecodeError:
        logger.error("Error decoding JSON from user data file")
    return {}


def save_user_data(data: Dict) -> None:
    """Save user data to JSON file."""
    try:
        with open(USER_DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving user data: {e}")


# Initialize user data
user_data = load_user_data()

# Initialize Faker for generating fake data
fake = Faker()


def _uid(user_id: int) -> str:
    """Return a stable string key for JSON storage."""
    return str(user_id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    key = _uid(user.id)
    user_data.setdefault(key, {"email": None, "phone": None, "social_media": [], "tiktok_token": None, "fetched_data": {}, "is_adding_platform": False, "awaiting_token": False})
    save_user_data(user_data)

    if user_data[key]["phone"]:
        # User has provided details, show keyboard
        keyboard = [
            [InlineKeyboardButton("TikTok", callback_data="tiktok")],
            [InlineKeyboardButton("Instagram", callback_data="instagram")],
            [InlineKeyboardButton("Facebook", callback_data="facebook")],
            [InlineKeyboardButton("Add New Platform", callback_data="add_platform")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Welcome back {user.first_name}! Select a social media platform to interact with:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_html(
            rf"Hi {user.mention_html()}! Welcome to the Enhanced Social Media Scraper Bot.\n"
        )


async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store the email address and ask for the phone number."""
    user = update.effective_user
    email = update.message.text
    key = _uid(user.id)
    user_data.setdefault(key, {"email": None, "phone": None, "social_media": []})
    user_data[key]["email"] = email
    save_user_data(user_data)
    await update.message.reply_text("Thank you! Now please enter your phone number:")


async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store the phone number and provide options for social media scraping."""
    user = update.effective_user
    phone = update.message.text
    key = _uid(user.id)
    user_data.setdefault(key, {"email": None, "phone": None, "social_media": [], "tiktok_token": None, "instagram_token": None, "facebook_token": None, "fetched_data": {}})
    user_data[key]["phone"] = phone
    save_user_data(user_data)

    keyboard = [
        [InlineKeyboardButton("TikTok", callback_data="tiktok")],
        [InlineKeyboardButton("Instagram", callback_data="instagram")],
        [InlineKeyboardButton("Facebook", callback_data="facebook")],
        [InlineKeyboardButton("Add New Platform", callback_data="add_platform")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Great! Now, select a social media platform to interact with:",
        reply_markup=reply_markup
    )


async def scrape_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scrape TikTok accounts based on user data."""
    user = update.effective_user
    key = _uid(user.id)
    if not (key in user_data and user_data[key].get("email") and user_data[key].get("phone")):
        await update.message.reply_text("Please provide your email and phone number first using /start.")
        return

    email = user_data[key]["email"]
    phone = user_data[key]["phone"]
    await update.message.reply_text(f"Scraping TikTok accounts for {email} and {phone}...")

    try:
        results = await perform_tiktok_scrape(email=email, phone=phone)
    except Exception as e:
        logger.exception("Error during TikTok scrape")
        await update.message.reply_text(f"An error occurred while scraping: {e}")
        return

    # Save results into user_data
    user_data.setdefault(key, {"email": None, "phone": None, "social_media": []})
    platform_store = user_data[key].setdefault("platform_data", {})
    platform_store["tiktok"] = results
    save_user_data(user_data)

    # Send a richer summary back to the user
    if not results:
        await update.message.reply_text("No TikTok accounts found for the provided details.")
    else:
        text = format_tiktok_summary(results, top_n=3)
        await update.message.reply_text(text)


async def scrape_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scrape Instagram accounts based on user data."""
    user = update.effective_user
    key = _uid(user.id)
    if key in user_data and user_data[key].get("email") and user_data[key].get("phone"):
        await update.message.reply_text(
            f"Scraping Instagram accounts for {user_data[key]['email']} and {user_data[key]['phone']}...\n"
            "This feature is currently under development. Please check back later!"
        )
    else:
        await update.message.reply_text("Please provide your email and phone number first using /start.")


async def scrape_facebook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scrape Facebook accounts based on user data."""
    user = update.effective_user
    key = _uid(user.id)
    if key in user_data and user_data[key].get("email") and user_data[key].get("phone"):
        await update.message.reply_text(
            f"Scraping Facebook accounts for {user_data[key]['email']} and {user_data[key]['phone']}...\n"
            "This feature is currently under development. Please check back later!"
        )
    else:
        await update.message.reply_text("Please provide your email and phone number first using /start.")


async def scrape_link(update, context) -> None:
    """Scrape a provided public profile URL for TikTok/Instagram/Facebook.

    Usage: /scrape_link <url>
    Also registered as a message handler for plain URLs sent to the bot.
    """
    user = update.effective_user
    key = _uid(user.id)

    # Accept as command arg or message body
    url = None
    if getattr(context, 'args', None):
        if len(context.args) > 0:
            url = context.args[0]
    if not url:
        url = (update.message.text or "").strip()

    if not url or not re.search(r"https?://", url):
        await update.message.reply_text("Usage: /scrape_link <url> — send a full TikTok/Instagram/Facebook profile URL.")
        return

    await update.message.reply_text("Scraping the provided link — this may take a few seconds.\nNote: scraping public pages may be rate-limited or blocked by the target site.")

    results = []
    platform = None
    if "tiktok.com" in url:
        platform = "tiktok"
        results = await perform_tiktok_scrape_by_url(url)
    elif "instagram.com" in url:
        platform = "instagram"
        results = await perform_instagram_scrape_by_url(url)
    elif "facebook.com" in url:
        platform = "facebook"
        results = await perform_facebook_scrape_by_url(url)
    else:
        await update.message.reply_text("Unrecognized platform in URL. Supported: TikTok, Instagram, Facebook.")
        return

    # persist
    user_data.setdefault(key, {"email": None, "phone": None, "social_media": []})
    platform_store = user_data[key].setdefault("platform_data", {})
    platform_store.setdefault(f"{platform}_links", {})
    platform_store[f"{platform}_links"][url] = results
    save_user_data(user_data)

    if not results:
        await update.message.reply_text("No data found or page inaccessible for the provided URL.")
    else:
        # If TikTok, use rich formatting
        if platform == "tiktok":
            text = format_tiktok_summary(results, top_n=3)
            await update.message.reply_text(text)
        else:
            sample = results[0]
            await update.message.reply_text(f"Found {len(results)} result(s). Example: {sample.get('username')} — {sample.get('url')}")


def format_tiktok_summary(results: List[Dict[str, Any]], top_n: int = 3) -> str:
    """Return a plain-text summary of top_n TikTok profiles from results.

    Results are expected to include keys like username, url, followers, likes, bio, avatar.
    """
    lines: List[str] = []
    count = len(results)
    lines.append(f"Found {count} TikTok account(s). Showing top {min(top_n, count)}:")
    for i, p in enumerate(results[:top_n], start=1):
        uname = p.get("username", "unknown")
        url = p.get("url", f"https://www.tiktok.com/@{uname}")
        followers = p.get("followers")
        likes = p.get("likes")
        videos = p.get("videos")
        bio = p.get("bio") or p.get("signature") or ""
        lines.append(f"\n{i}. @{uname}")
        if followers is not None:
            lines.append(f"   Followers: {followers}")
        if likes is not None:
            lines.append(f"   Likes: {likes}")
        if videos is not None:
            lines.append(f"   Videos: {videos}")
        if bio:
            # cap bio length to keep messages short
            short_bio = (bio[:160] + "...") if len(bio) > 160 else bio
            lines.append(f"   Bio: {short_bio}")
        lines.append(f"   URL: {url}")
    return "\n".join(lines)


async def perform_tiktok_scrape(email: str, phone: str) -> List[Dict[str, Any]]:
    """Perform a TikTok scrape using an external API if configured, otherwise run a local simulation.

    Returns a list of dicts with keys like 'username' and 'url'.
    """
    # Allow a MOCK_MODE which returns deterministic test data without network calls
    MOCK_MODE = os.environ.get("MOCK_MODE", "").lower() in ("1", "true", "yes")

    api_url = os.environ.get("TIKTOK_API_URL")
    api_key = os.environ.get("TIKTOK_API_KEY")

    payload = {"email": email, "phone": phone}

    # Number of mock accounts to generate (bounded)
    mock_count = int(os.environ.get("TIKTOK_MOCK_COUNT", "5"))
    mock_count = max(1, min(mock_count, 50))

    if MOCK_MODE:
        # Return deterministic mock results for testing. Use a stable hash of the
        # email+phone to generate reproducible follower/likes counts.
        await asyncio.sleep(0.05)
        seed = (email or "") + "|" + (phone or "")
        h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        # helper to derive stable ints from hash
        def _stable_int(offset: int, modulus: int = 100000):
            return (int(h[offset: offset + 8], 16) % modulus) + 1

        results: List[Dict[str, Any]] = []
        localpart = (email.split("@")[0] if email and "@" in email else "user")
        phone_suffix = (phone[-4:] if phone and len(phone) >= 4 else "0000")
        # Small helper to format large integers into compact strings (e.g. 123k, 1.2M)
        def _compact_number(n: int) -> str:
            if n >= 1_000_000:
                v = n / 1_000_000
                s = f"{v:.1f}".rstrip("0").rstrip(".")
                return f"{s}M"
            if n >= 1_000:
                return f"{n//1000}k"
            return str(n)

        for i in range(1, mock_count + 1):
            uname = f"{localpart}_{phone_suffix}_{i}"
            # ensure followers are in 100k+ range (deterministic)
            followers_int = 100_000 + (_stable_int(i, 900_000))
            results.append({
                "username": uname,
                "url": f"https://www.tiktok.com/@{uname}",
                "avatar": f"https://example.com/avatars/{uname}.jpg",
                "followers": followers_int,
                "followers_display": _compact_number(followers_int),
                "following": _stable_int(i + 2, 2000),
                "likes": _stable_int(i + 4, 500000),
                "videos": _stable_int(i + 6, 2000),
                "bio": f"Mock account derived from {localpart} and {phone_suffix}",
                "meta": {"matched_email": email, "matched_phone": phone},
            })
        return results

    if api_url:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(api_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "accounts" in data:
                return data["accounts"]
            if isinstance(data, list):
                return data
            # fallback: wrap dict into list
            if isinstance(data, dict):
                return [{"username": data.get("username", "unknown"), "url": data.get("url", "")}]  # type: ignore[arg-type]

    # Local simulated results (safe fallback) - generate a few plausible accounts
    await asyncio.sleep(0.5)
    simulated: List[Dict[str, Any]] = []
    phone_suffix = (phone[-4:] if phone and len(phone) >= 4 else "0000")
    base = (email.split("@")[0] if email and "@" in email else "user")
    # produce up to 3 fallback entries
    for i in range(1, 4):
        uname = f"{base}_{phone_suffix}_{i}"
        simulated.append({
            "username": uname,
            "url": f"https://www.tiktok.com/@{uname}",
            "meta": {"matched_email": email, "matched_phone": phone},
        })
    return simulated


async def perform_tiktok_scrape_by_url(url: str) -> List[Dict[str, Any]]:
    """Scrape TikTok profile information from a direct profile URL.

    If TIKTOK_API_URL is configured, this will call the external API with the URL.
    Otherwise it will fetch the public page and extract a username as a minimal heuristic.
    Returns a list of profile dicts (keeps same shape as other scrape helpers).
    """
    # If the URL matches forestapi.vercel.app/api/tiktok/user/<username>, call it directly
    m = re.match(r"https?://forestapi\.vercel\.app/api/tiktok/user/([A-Za-z0-9_.-]+)", url)
    if m:
        username = m.group(1)
        api_url = f"https://forestapi.vercel.app/api/tiktok/user/{username}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(api_url)
            if resp.status_code != 200:
                return []
            data = resp.json()
            # forestapi returns { user: {...}, stats: {...}, ... }
            user = data.get("user", {})
            stats = data.get("stats", {})
            profile = {
                "username": user.get("uniqueId", username),
                "url": url,
                "nickname": user.get("nickname"),
                "avatar": user.get("avatar"),
                "followers": stats.get("followerCount"),
                "following": stats.get("followingCount"),
                "likes": stats.get("heartCount"),
                "videos": stats.get("videoCount"),
                "bio": user.get("signature"),
                "raw": data
            }
            return [profile]

    # Fallback: fetch the public page and attempt simple extraction
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return []
            text = r.text
    except Exception:
        return []

    # Heuristic: extract @username from URL or page
    m = re.search(r"/@([^/?#&\\]+)", url)
    username = None
    if m:
        username = m.group(1)
    else:
        m2 = re.search(r"@([A-Za-z0-9_.-]{2,})", text)
        if m2:
            username = m2.group(1)

    profile = {"username": username or "unknown", "url": url, "raw_status": 200}
    return [profile]


async def perform_instagram_scrape_by_url(url: str) -> List[Dict[str, Any]]:
    MOCK_MODE = os.environ.get("MOCK_MODE", "").lower() in ("1", "true", "yes")

    if MOCK_MODE:
        # Generate mock Instagram profile data
        await asyncio.sleep(0.05)
        username = fake.user_name()
        profile = {
            "username": username,
            "url": url,
            "full_name": fake.name(),
            "avatar": f"https://example.com/avatars/{username}.jpg",
            "followers": fake.random_int(min=1000, max=1000000),
            "following": fake.random_int(min=100, max=5000),
            "posts": fake.random_int(min=10, max=1000),
            "bio": fake.sentence(),
            "raw": {"mock": True}
        }
        return [profile]

    # If the URL matches forestapi.vercel.app/api/instagram/user/<username>, call it directly
    m = re.match(r"https?://forestapi\.vercel\.app/api/instagram/user/([A-Za-z0-9_.-]+)", url)
    if m:
        username = m.group(1)
        api_url = f"https://forestapi.vercel.app/api/instagram/user/{username}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(api_url)
            if resp.status_code != 200:
                return []
            data = resp.json()
            # forestapi returns { user: {...}, stats: {...}, ... }
            user = data.get("user", {})
            stats = data.get("stats", {})
            profile = {
                "username": user.get("username", username),
                "url": url,
                "full_name": user.get("full_name"),
                "avatar": user.get("profile_pic_url"),
                "followers": stats.get("follower_count"),
                "following": stats.get("following_count"),
                "posts": stats.get("media_count"),
                "bio": user.get("biography"),
                "raw": data
            }
            return [profile]

    api_url = os.environ.get("INSTAGRAM_API_URL")
    api_key = os.environ.get("INSTAGRAM_API_KEY")
    payload = {"url": url}
    if api_url:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(api_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "accounts" in data:
                return data["accounts"]
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return [{"username": data.get("username", "unknown"), "url": data.get("url", url)}]

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return []
            text = r.text
    except Exception:
        return []

    m = re.search(r"instagram.com/([A-Za-z0-9_.-]{1,})", url)
    username = m.group(1) if m else None
    if not username:
        m2 = re.search(r"@([A-Za-z0-9_.-]{2,})", text)
        if m2:
            username = m2.group(1)

    profile = {"username": username or "unknown", "url": url, "raw_status": 200}
    return [profile]


async def perform_facebook_scrape_by_url(url: str) -> List[Dict[str, Any]]:
    MOCK_MODE = os.environ.get("MOCK_MODE", "").lower() in ("1", "true", "yes")

    if MOCK_MODE:
        # Generate mock Facebook profile data
        await asyncio.sleep(0.05)
        username = fake.user_name()
        profile = {
            "username": username,
            "url": url,
            "full_name": fake.name(),
            "avatar": f"https://example.com/avatars/{username}.jpg",
            "friends": fake.random_int(min=100, max=5000),
            "posts": fake.random_int(min=10, max=1000),
            "bio": fake.sentence(),
            "raw": {"mock": True}
        }
        return [profile]

    # Similar minimal fallback for Facebook public pages
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return []
            text = r.text
    except Exception:
        return []

    m = re.search(r"facebook.com/([A-Za-z0-9_.-]{1,})", url)
    username = m.group(1) if m else None
    profile = {"username": username or "unknown", "url": url, "raw_status": 200}
    return [profile]


async def add_social_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allow users to add a new social media platform."""
    user = update.effective_user
    await update.message.reply_text("Please enter the name of the new social media platform:")
    key = _uid(user.id)
    user_data.setdefault(key, {"email": None, "phone": None, "social_media": []})
    user_data[key]["is_adding_platform"] = True
    save_user_data(user_data)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages for email, phone, token, etc."""
    user = update.effective_user
    text = update.message.text
    key = _uid(user.id)
    user_data.setdefault(key, {"email": None, "phone": None, "social_media": [], "tiktok_token": None, "fetched_data": {}, "is_adding_platform": False, "awaiting_token": False})

    MOCK_MODE = os.environ.get("MOCK_MODE", "").lower() in ("1", "true", "yes")

    if user_data[key]["email"] is None:
        # Store email or generate fake if MOCK_MODE
        if MOCK_MODE and not text.strip():
            user_data[key]["email"] = fake.email()
        else:
            user_data[key]["email"] = text
        save_user_data(user_data)
        await update.message.reply_text("Thank you! Now please enter your phone number:")
    elif user_data[key]["phone"] is None:
        # Store phone or generate fake if MOCK_MODE
        if MOCK_MODE and not text.strip():
            user_data[key]["phone"] = fake.phone_number()
        else:
            user_data[key]["phone"] = text
        save_user_data(user_data)
        keyboard = [
            [InlineKeyboardButton("TikTok", callback_data="tiktok")],
            [InlineKeyboardButton("Instagram", callback_data="instagram")],
            [InlineKeyboardButton("Facebook", callback_data="facebook")],
            [InlineKeyboardButton("Add New Platform", callback_data="add_platform")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Great! Now, select a social media platform to interact with:",
            reply_markup=reply_markup
        )
    elif user_data[key]["awaiting_token"]:
        # Store token based on awaiting_platform
        platform = user_data[key].get("awaiting_platform", "tiktok")
        user_data[key][f"{platform}_token"] = text
        user_data[key]["awaiting_token"] = False
        user_data[key]["awaiting_platform"] = False
        save_user_data(user_data)
        await update.message.reply_text(f"Token stored successfully for {platform}. You can now fetch user info.")
    elif user_data[key]["is_adding_platform"]:
        # Add new platform
        user_data[key]["social_media"].append(text)
        user_data[key]["is_adding_platform"] = False
        save_user_data(user_data)
        await update.message.reply_text(f"Added '{text}' to your social media platforms.")
    else:
        await update.message.reply_text("Please use the buttons or commands. If you need help, type /help.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provide help information to the user."""
    await update.message.reply_text(
        "This bot allows you to interact with social media platforms using buttons.\n"
        "After providing email and phone, select platforms via buttons.\n"
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "Use buttons for main interactions."
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    key = _uid(user.id)

    if data == "tiktok":
        keyboard = [
            [InlineKeyboardButton("Login to TikTok", callback_data="tiktok_login")],
            [InlineKeyboardButton("Fetch User Info", callback_data="tiktok_fetch")],
            [InlineKeyboardButton("Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("TikTok Options:", reply_markup=reply_markup)
    elif data == "instagram":
        keyboard = [
            [InlineKeyboardButton("Login to Instagram", callback_data="instagram_login")],
            [InlineKeyboardButton("Fetch User Info", callback_data="instagram_fetch")],
            [InlineKeyboardButton("Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Instagram Options:", reply_markup=reply_markup)
    elif data == "facebook":
        keyboard = [
            [InlineKeyboardButton("Login to Facebook", callback_data="facebook_login")],
            [InlineKeyboardButton("Fetch User Info", callback_data="facebook_fetch")],
            [InlineKeyboardButton("Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Facebook Options:", reply_markup=reply_markup)
    elif data == "instagram_login":
        await query.edit_message_text("Please reply with your Instagram access token.")
        user_data.setdefault(key, {"email": None, "phone": None, "social_media": [], "tiktok_token": None, "instagram_token": None, "facebook_token": None, "fetched_data": {}, "awaiting_token": False, "awaiting_platform": False, "is_adding_platform": False})
        user_data[key]["awaiting_token"] = True
        user_data[key]["awaiting_platform"] = "instagram"
        save_user_data(user_data)
    elif data == "instagram_fetch":
        if user_data.get(key, {}).get("instagram_token"):
            # Simulate fetching Instagram user info
            user_info = {
                "user_id": "123456789",
                "display_name": "John Doe",
                "profile_picture_url": "https://example.com/pic.jpg",
                "follower_count": 1000,
                "following_count": 500,
                "likes_count": 2000,
                "video_count": 50,
                "profile_description": "Bio here"
            }
            user_data[key]["fetched_data"]["instagram"] = user_info
            save_user_data(user_data)
            info_text = f"User ID: {user_info['user_id']}\nDisplay Name: {user_info['display_name']}\nProfile Picture: {user_info['profile_picture_url']}\nFollower Count: {user_info['follower_count']}\nFollowing Count: {user_info['following_count']}\nLikes Count: {user_info['likes_count']}\nVideo Count: {user_info['video_count']}\nProfile Description: {user_info['profile_description']}"
            await query.edit_message_text(f"Fetched Instagram User Info:\n{info_text}")
        else:
            await query.edit_message_text("Please login to Instagram first.")
    elif data == "facebook_login":
        await query.edit_message_text("Please reply with your Facebook access token.")
        user_data.setdefault(key, {"email": None, "phone": None, "social_media": [], "tiktok_token": None, "instagram_token": None, "facebook_token": None, "fetched_data": {}, "awaiting_token": False, "awaiting_platform": False, "is_adding_platform": False})
        user_data[key]["awaiting_token"] = True
        user_data[key]["awaiting_platform"] = "facebook"
        save_user_data(user_data)
    elif data == "facebook_fetch":
        if user_data.get(key, {}).get("facebook_token"):
            # Simulate fetching Facebook user info
            user_info = {
                "user_id": "987654321",
                "display_name": "Jane Doe",
                "profile_picture_url": "https://example.com/fbpic.jpg",
                "friend_count": 500,
                "follower_count": 2000,
                "following_count": 300,
                "likes_count": 1500,
                "post_count": 100,
                "profile_description": "About me"
            }
            user_data[key]["fetched_data"]["facebook"] = user_info
            save_user_data(user_data)
            info_text = f"User ID: {user_info['user_id']}\nDisplay Name: {user_info['display_name']}\nProfile Picture: {user_info['profile_picture_url']}\nFriend Count: {user_info['friend_count']}\nFollower Count: {user_info['follower_count']}\nFollowing Count: {user_info['following_count']}\nLikes Count: {user_info['likes_count']}\nPost Count: {user_info['post_count']}\nProfile Description: {user_info['profile_description']}"
            await query.edit_message_text(f"Fetched Facebook User Info:\n{info_text}")
        else:
            await query.edit_message_text("Please login to Facebook first.")
    elif data == "add_platform":
        await query.edit_message_text("Please reply with the name of the new platform.")
        user_data.setdefault(key, {"email": None, "phone": None, "social_media": [], "tiktok_token": None, "fetched_data": {}, "is_adding_platform": False, "awaiting_token": False})
        user_data[key]["is_adding_platform"] = True
        save_user_data(user_data)
    elif data == "tiktok_login":
        await query.edit_message_text("Please reply with your TikTok access token.")
        user_data.setdefault(key, {"email": None, "phone": None, "social_media": [], "tiktok_token": None, "fetched_data": {}, "is_adding_platform": False, "awaiting_token": False})
        user_data[key]["awaiting_token"] = True
        save_user_data(user_data)
    elif data == "tiktok_fetch":
        if user_data.get(key, {}).get("tiktok_token"):
            token = user_data[key]["tiktok_token"]
            url = "https://open-api.tiktok.com/user/info/"
            headers = {"Authorization": f"Bearer {token}"}
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.get(url, headers=headers)
                    if resp.status_code == 200:
                        api_data = resp.json()
                        user_info = api_data.get("data", {})
                        user_data[key]["fetched_data"]["tiktok"] = user_info
                        save_user_data(user_data)
                        info_text = f"User ID: {user_info.get('user_id')}\nDisplay Name: {user_info.get('display_name')}\nProfile Picture: {user_info.get('avatar_url')}\nFollower Count: {user_info.get('follower_count')}\nFollowing Count: {user_info.get('following_count')}\nLikes Count: {user_info.get('likes_count')}\nVideo Count: {user_info.get('video_count')}\nProfile Description: {user_info.get('signature')}"
                        await query.edit_message_text(f"Fetched TikTok User Info:\n{info_text}")
                    else:
                        await query.edit_message_text("Failed to fetch user info. Check token or API.")
            except Exception as e:
                await query.edit_message_text(f"Error fetching data: {str(e)}")
        else:
            await query.edit_message_text("Please login to TikTok first.")
    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("TikTok", callback_data="tiktok")],
            [InlineKeyboardButton("Instagram", callback_data="instagram")],
            [InlineKeyboardButton("Facebook", callback_data="facebook")],
            [InlineKeyboardButton("Add New Platform", callback_data="add_platform")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a social media platform to interact with:", reply_markup=reply_markup)


def _expand_pattern(pattern: str, max_len: int = 2, charset: Optional[str] = None) -> List[str]:
    """Expand a simple pattern with a single '*' wildcard into candidate usernames.

    - pattern: e.g. 'foo*bar' or '@foo*'
    - max_len: maximum length to substitute for '*' (small number by default)
    - charset: characters to use for expansion (defaults to lowercase letters+digits)

    Returns a list of username strings (without leading '@'). This function is intentionally
    conservative: it limits expansions to avoid huge candidate sets.
    """
    if charset is None:
        charset = string.ascii_lowercase + string.digits

    # strip leading @ if present
    if pattern.startswith("@"):
        pattern = pattern[1:]

    if "*" not in pattern:
        return [pattern]

    parts = pattern.split("*")
    if len(parts) != 2:
        # only support single '*' for now
        return []

    prefix, suffix = parts
    candidates: List[str] = []
    # generate all combinations up to max_len
    for L in range(1, max_len + 1):
        for comb in product(charset, repeat=L):
            mid = "".join(comb)
            candidates.append(prefix + mid + suffix)
    return candidates


async def _probe_usernames(usernames: List[str], concurrency: int = 5, timeout: float = 10.0) -> List[str]:
    """Probe tiktok.com/@username for existence. Returns list of usernames that exist.

    Uses httpx AsyncClient. A 200 response (and presence of username in HTML) is treated
    as the profile existing. This is a heuristic and may need adjustment.
    """
    found: List[str] = []
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

    async def _probe(client, username: str) -> None:
        url = f"https://www.tiktok.com/@{username}"
        try:
            r = await client.get(url, headers=headers, timeout=timeout)
            if r.status_code == 200 and username.lower() in r.text.lower():
                found.append(username)
        except Exception:
            # ignore errors for single probes; caller can log if desired
            pass

    async with httpx.AsyncClient() as client:
        # run in batches with limited concurrency
        sem = asyncio.Semaphore(concurrency)

        async def sem_probe(u: str):
            async with sem:
                await _probe(client, u)

        await asyncio.gather(*(sem_probe(u) for u in usernames))

    return found


async def search_username(update, context) -> None:
    """Search for TikTok usernames using a pattern. Usage: /search <pattern>

    Pattern examples:
      /search @someuser        -> probe exact username 'someuser'
      /search someprefix*      -> probe candidates where '*' is replaced by up to N chars

    The expansion is conservative to avoid excessive probing. Configure via env:
      PROBE_MAX_LEN (default 2), PROBE_CONCURRENCY (default 5)
    """
    user = update.effective_user
    key = _uid(user.id)
    args = context.args if getattr(context, 'args', None) is not None else []
    if not args:
        await update.message.reply_text("Usage: /search <pattern> — e.g. /search @username or /search foo*")
        return

    pattern = args[0]
    max_len = int(os.environ.get("PROBE_MAX_LEN", "2"))
    concurrency = int(os.environ.get("PROBE_CONCURRENCY", "5"))

    await update.message.reply_text(f"Searching for pattern: {pattern} (this may take a few seconds)")

    candidates = _expand_pattern(pattern, max_len=max_len)
    if not candidates:
        await update.message.reply_text("No candidates generated from pattern (only single '*' supported). Try a simpler pattern like foo* or @username.")
        return

    # limit total candidates to a reasonable amount
    limit = int(os.environ.get("PROBE_CANDIDATE_LIMIT", "200"))
    candidates = candidates[:limit]

    found = await _probe_usernames(candidates, concurrency=concurrency)

    # save results
    user_data.setdefault(key, {"email": None, "phone": None, "social_media": []})
    platform_store = user_data[key].setdefault("platform_data", {})
    platform_store.setdefault("tiktok_candidates", {})
    platform_store["tiktok_candidates"][pattern] = found
    save_user_data(user_data)

    if not found:
        await update.message.reply_text("No matching TikTok usernames found for the provided pattern.")
    else:
        reply = "Found the following usernames:\n" + "\n".join(f"@{u}" for u in found[:10])
        if len(found) > 10:
            reply += f"\n(and {len(found)-10} more)"
        await update.message.reply_text(reply)


def build_application(token: str):
    """Create and return a telegram Application instance."""
    app = ApplicationBuilder().token(token).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tiktok", scrape_tiktok))
    app.add_handler(CommandHandler("instagram", scrape_instagram))
    app.add_handler(CommandHandler("facebook", scrape_facebook))
    app.add_handler(CommandHandler("add", add_social_media))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("search", search_username))
    app.add_handler(CommandHandler("scrape_link", scrape_link))

    # Also accept plain URLs sent as messages
    app.add_handler(MessageHandler(filters.Regex(r"https?://") & ~filters.COMMAND, scrape_link))

    # Register callback query handler for buttons
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Register message handler for text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    return app


def main() -> None:
    """Start the bot. Reads token from TELEGRAM_BOT_API_TOKEN env var."""
    # Read token from environment for safety. If you previously embedded the token
    # directly into this file, it has been removed. Provide the token in the
    # TELEGRAM_BOT_API_TOKEN environment variable or via a `.env` file (see README).
    token = os.environ.get("TELEGRAM_BOT_API_TOKEN")
    if not token:
        logger.error(
            "No Telegram token found. Set the TELEGRAM_BOT_API_TOKEN environment variable with your bot token."
        )
        print(
            "No Telegram token found. Export TELEGRAM_BOT_API_TOKEN and re-run. Example:\n"
            "export TELEGRAM_BOT_API_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11\n"
        )
        return

    app = build_application(token)
    # Start the bot (this will block until interrupted)
    try:
        app.run_polling()
    except Conflict:
        # This commonly happens when another process is polling the same bot token
        logger.error("Conflict detected: another getUpdates request is active for this bot token.\n" \
                     "Stop other bot instances or remove any webhook (use getWebhookInfo / deleteWebhook) before polling.")
        print("Conflict: another getUpdates request is active. Stop other instances or delete any webhook for this bot token and retry.")
    except Exception:
        logger.exception("Unhandled exception while running the bot")


if __name__ == "__main__":
    main()
