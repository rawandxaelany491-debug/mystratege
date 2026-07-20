# -*- coding: utf-8 -*-
"""
سیستەمی Streak — شوێنکەوتنی چەند ڕۆژی دوایدوا کە بەکارهێنەرێک
بۆتەکەی بەکارهێناوە (پرسیار یان وێنە).
"""

import json
import os
from datetime import datetime, timedelta, timezone

STREAKS_FILE = "streaks.json"


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _yesterday() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")


def _load() -> dict:
    if not os.path.exists(STREAKS_FILE):
        return {}
    try:
        with open(STREAKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save(data: dict) -> None:
    with open(STREAKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record_activity(user_id: int) -> int:
    """تۆمارکردنی چالاکی ئەمڕۆ بۆ بەکارهێنەر. کۆی streak ی نوێ دەگەڕێنێتەوە."""
    data = _load()
    today = _today()
    key = str(user_id)
    entry = data.get(key)

    if not entry:
        streak = 1
    elif entry.get("last_date") == today:
        streak = entry.get("streak", 1)  # ئەمڕۆ پێشتر تۆمارکراوە، گۆڕان نییە
    elif entry.get("last_date") == _yesterday():
        streak = entry.get("streak", 0) + 1
    else:
        streak = 1  # streak شکاوە، لەسەرەتاوە دەستپێدەکاتەوە

    data[key] = {"last_date": today, "streak": streak}
    _save(data)
    return streak


def get_streak(user_id: int) -> int:
    """گەڕاندنەوەی streak ی ئێستا بەبێ تۆمارکردنی چالاکی. ٠ ئەگەر شکابێت."""
    data = _load()
    entry = data.get(str(user_id))
    if not entry:
        return 0
    if entry.get("last_date") in (_today(), _yesterday()):
        return entry.get("streak", 0)
    return 0  # streak شکاوە (دوو ڕۆژ یان زیاتر بەبێ چالاکی)