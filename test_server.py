#!/usr/bin/env python3
"""Lightweight FastAPI test server exposing KrisBot helpers.

Endpoints:
  POST /tiktok/search    {"email":..., "phone":...}
  POST /tiktok/by_url    {"url":...}
  POST /instagram/by_url {"url":...}
  POST /facebook/by_url  {"url":...}
  POST /probe            {"pattern":...}

By default this server forces MOCK_MODE=1 so responses are deterministic and safe.
"""

import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

# Ensure mock mode for predictable behavior
os.environ.setdefault("MOCK_MODE", "1")

from KrisBot import (
    perform_tiktok_scrape,
    perform_tiktok_scrape_by_url,
    perform_instagram_scrape_by_url,
    perform_facebook_scrape_by_url,
    _expand_pattern,
    _probe_usernames,
)

app = FastAPI(title="KrisBot Test Server")


class TikTokSearchRequest(BaseModel):
    email: str
    phone: str


class URLRequest(BaseModel):
    url: str


class ProbeRequest(BaseModel):
    pattern: str


@app.post("/tiktok/search")
async def tiktok_search(req: TikTokSearchRequest) -> List[Dict[str, Any]]:
    res = await perform_tiktok_scrape(email=req.email, phone=req.phone)
    return res


@app.post("/tiktok/by_url")
async def tiktok_by_url(req: URLRequest) -> List[Dict[str, Any]]:
    res = await perform_tiktok_scrape_by_url(req.url)
    return res


@app.post("/instagram/by_url")
async def instagram_by_url(req: URLRequest) -> List[Dict[str, Any]]:
    res = await perform_instagram_scrape_by_url(req.url)
    return res


@app.post("/facebook/by_url")
async def facebook_by_url(req: URLRequest) -> List[Dict[str, Any]]:
    res = await perform_facebook_scrape_by_url(req.url)
    return res


@app.post("/probe")
async def probe(req: ProbeRequest) -> Dict[str, Any]:
    pattern = req.pattern
    candidates = _expand_pattern(pattern, max_len=int(os.environ.get("PROBE_MAX_LEN", "2")))
    # limit to avoid heavy loads
    limit = int(os.environ.get("PROBE_CANDIDATE_LIMIT", "200"))
    candidates = candidates[:limit]
    found = await _probe_usernames(candidates, concurrency=int(os.environ.get("PROBE_CONCURRENCY", "5")))
    return {"pattern": pattern, "generated": len(candidates), "found": found}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test_server:app", host="127.0.0.1", port=8000, log_level="info")
