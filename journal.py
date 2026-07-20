# -*- coding: utf-8 -*-
"""
مێژووی سیگناڵەکان (Journal).
هەر جارێک بۆت سیگناڵێکی BUY/SELL/WAIT بدات لەسەر وێنەیەکی چارت، تۆمار
دەکرێت لێرە بۆ ئەوەی دواتر بەکارهێنەر بتوانێت مێژووی سیگناڵەکانی خۆی
یان (ئەگەر خاوەن بێت) هەموو بەکارهێنەران ببینێت.
"""

import json
import os
from datetime import datetime, timedelta, timezone

JOURNAL_FILE = "journal.json"
MAX_ENTRIES = 2000  # سنووری سەرەوەی تۆمار بۆ ئەوەی فایلەکە زۆر گەورە نەبێت


def _load_journal() -> list:
    if not os.path.exists(JOURNAL_FILE):
        return []
    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_journal(entries: list) -> None:
    with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
        json.dump(entries[-MAX_ENTRIES:], f, ensure_ascii=False, indent=2)


def log_signal(user_id: int, signal: str) -> None:
    """تۆمارکردنی سیگناڵێکی نوێ. signal دەبێت یەکێک بێت لە BUY/SELL/WAIT."""
    entries = _load_journal()
    entries.append(
        {
            "user_id": user_id,
            "signal": signal,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    _save_journal(entries)


def extract_signal(reply_text: str) -> str | None:
    """دەرهێنانی سیگناڵ (BUY/SELL/WAIT) لە دەقی وەڵامی مۆدێلەکە."""
    text_upper = reply_text.upper()
    if "سیگناڵ" in reply_text or "SIGNAL" in text_upper:
        for signal in ("BUY", "SELL", "WAIT"):
            if signal in text_upper:
                return signal
    return None


def get_user_stats(user_id: int) -> dict:
    """ژمارەی هەر سیگناڵێک بۆ بەکارهێنەرێکی دیاریکراو."""
    entries = _load_journal()
    stats = {"BUY": 0, "SELL": 0, "WAIT": 0}
    for entry in entries:
        if entry.get("user_id") == user_id and entry.get("signal") in stats:
            stats[entry["signal"]] += 1
    return stats


def get_all_stats() -> dict:
    """ژمارەی هەر سیگناڵێک بۆ هەموو بەکارهێنەران (تەنها بۆ خاوەن)."""
    entries = _load_journal()
    stats = {"BUY": 0, "SELL": 0, "WAIT": 0}
    for entry in entries:
        if entry.get("signal") in stats:
            stats[entry["signal"]] += 1
    return stats


def get_user_stats_since(user_id: int, days: int = 7) -> dict:
    """ژمارەی هەر سیگناڵێک بۆ بەکارهێنەرێک لە دوایین N ڕۆژدا (بۆ ڕاپۆرتی هەفتانە)."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    entries = _load_journal()
    stats = {"BUY": 0, "SELL": 0, "WAIT": 0}
    for entry in entries:
        if entry.get("user_id") != user_id or entry.get("signal") not in stats:
            continue
        try:
            ts = datetime.fromisoformat(entry["timestamp"])
        except (ValueError, KeyError):
            continue
        if ts >= since:
            stats[entry["signal"]] += 1
    return stats


def get_recent(user_id: int | None = None, limit: int = 10) -> list:
    """دوایین N سیگناڵ، ئەگەر user_id دراوە تەنها بۆ ئەو کەسە."""
    entries = _load_journal()
    if user_id is not None:
        entries = [e for e in entries if e.get("user_id") == user_id]
    return entries[-limit:]