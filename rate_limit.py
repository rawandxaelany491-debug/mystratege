# -*- coding: utf-8 -*-
"""
سنووردارکردنی ڕۆژانەی وێنە (Photo Rate Limit).
هەر بەکارهێنەرێک (جگە لە خاوەنی بۆت) تەنها دەتوانێت بڕێکی دیاریکراو
(بنەڕەت ١٠) وێنەی چارت لە ڕۆژێکدا بۆ شیکاریکردن بنێرێت. ژمارەکان
لە فایلێکی JSON پاشەکەوت دەکرێن و بەپێی بەروار (ڕۆژ) نوێ دەبنەوە.
"""

import json
import os
from datetime import datetime, timezone

RATE_LIMIT_FILE = "photo_limits.json"


def _today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load() -> dict:
    if not os.path.exists(RATE_LIMIT_FILE):
        return {}
    try:
        with open(RATE_LIMIT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save(data: dict) -> None:
    with open(RATE_LIMIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_today_count(user_id: int) -> int:
    """ژمارەی وێنەی شیکارکراوی ئەم بەکارهێنەرە بۆ ئەمڕۆ."""
    data = _load()
    entry = data.get(str(user_id))
    if not entry or entry.get("date") != _today_str():
        return 0
    return entry.get("count", 0)


def can_analyze(user_id: int, daily_limit: int, extra: int = 1) -> bool:
    """ئایا ئەم بەکارهێنەرە دەتوانێت ‪extra‬ وێنەی تر شیکاری بۆ بکرێت ئەمڕۆ؟"""
    return get_today_count(user_id) + extra <= daily_limit


def record_usage(user_id: int, count: int = 1) -> int:
    """تۆمارکردنی بەکارهێنانی N وێنە بۆ ئەم بەکارهێنەرە. کۆی نوێ دەگەڕێنێتەوە."""
    data = _load()
    today = _today_str()
    entry = data.get(str(user_id))
    if not entry or entry.get("date") != today:
        entry = {"date": today, "count": 0}
    entry["count"] += count
    data[str(user_id)] = entry
    _save(data)
    return entry["count"]