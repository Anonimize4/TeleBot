#!/usr/bin/env python3
"""Interactive test harness for KrisBot mock mode.

Run with MOCK_MODE=1 to have the internal helpers return deterministic mock data.

Usage:
  MOCK_MODE=1 python3 test_mock.py

Commands available in the REPL:
  tiktok_search <email> <phone>
  tiktok_by_url <url>
  instagram_by_url <url>
  facebook_by_url <url>
  probe <pattern>   # probes username pattern using _expand_pattern/_probe_usernames
  exit
"""

import asyncio
import os
import json
from typing import Any

from KrisBot import (
    perform_tiktok_scrape,
    perform_tiktok_scrape_by_url,
    perform_instagram_scrape_by_url,
    perform_facebook_scrape_by_url,
    _expand_pattern,
    _probe_usernames,
)


async def repl():
    print("KrisBot mock REPL. Commands: tiktok_search, tiktok_by_url, instagram_by_url, facebook_by_url, probe, exit")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            continue
        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "exit":
            break
        elif cmd == "tiktok_search":
            if len(args) < 2:
                print("usage: tiktok_search <email> <phone>")
                continue
            email, phone = args[0], args[1]
            res = await perform_tiktok_scrape(email=email, phone=phone)
            print(json.dumps(res, indent=2))
        elif cmd == "tiktok_by_url":
            if len(args) < 1:
                print("usage: tiktok_by_url <url>")
                continue
            url = args[0]
            res = await perform_tiktok_scrape_by_url(url)
            print(json.dumps(res, indent=2))
        elif cmd == "instagram_by_url":
            if len(args) < 1:
                print("usage: instagram_by_url <url>")
                continue
            url = args[0]
            res = await perform_instagram_scrape_by_url(url)
            print(json.dumps(res, indent=2))
        elif cmd == "facebook_by_url":
            if len(args) < 1:
                print("usage: facebook_by_url <url>")
                continue
            url = args[0]
            res = await perform_facebook_scrape_by_url(url)
            print(json.dumps(res, indent=2))
        elif cmd == "probe":
            if len(args) < 1:
                print("usage: probe <pattern>")
                continue
            pattern = args[0]
            candidates = _expand_pattern(pattern, max_len=2)
            print(f"Generated {len(candidates)} candidates (showing up to 20): {candidates[:20]}")
            found = await _probe_usernames(candidates, concurrency=5)
            print("Found:", found)
        else:
            print("Unknown command:", cmd)


def main():
    # Ensure MOCK_MODE is on for predictable responses
    os.environ.setdefault("MOCK_MODE", "1")
    asyncio.run(repl())


if __name__ == "__main__":
    main()
