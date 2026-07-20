# -*- coding: utf-8 -*-
"""
بەڕێوەبردنی ڕێگەپێدان (Access Control).
تەنها خاوەنی بۆت (OWNER_TELEGRAM_ID) و ئەو کەسانەی خاوەنەکە ڕێگەی
پێداون (بە فەرمانی /allow) دەتوانن بۆتەکە بەکاربهێنن.
لیستی ڕێگەپێدراوان لە فایلێکی JSON پاشەکەوت دەکرێت تاکو دوای
ڕیستارتکردنی بۆتیش نەفەوتێت.
"""

import json
import os

ALLOWED_USERS_FILE = "allowed_users.json"


def _load_allowed_users() -> set:
    if not os.path.exists(ALLOWED_USERS_FILE):
        return set()
    try:
        with open(ALLOWED_USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("allowed", []))
    except (json.JSONDecodeError, IOError):
        return set()


def _save_allowed_users(users: set) -> None:
    with open(ALLOWED_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"allowed": sorted(users)}, f, ensure_ascii=False, indent=2)


def is_allowed(user_id: int, owner_id: int) -> bool:
    """پشکنینی ئەوەی ئایا ئەم بەکارهێنەرە ڕێگەی پێدراوە."""
    if user_id == owner_id:
        return True
    return user_id in _load_allowed_users()


def allow_user(user_id: int) -> bool:
    """زیادکردنی بەکارهێنەرێک بۆ لیستی ڕێگەپێدراوان. True دەگەڕێنێتەوە ئەگەر نوێ بوو."""
    users = _load_allowed_users()
    if user_id in users:
        return False
    users.add(user_id)
    _save_allowed_users(users)
    return True


def deny_user(user_id: int) -> bool:
    """لابردنی بەکارهێنەرێک لە لیستی ڕێگەپێدراوان. True دەگەڕێنێتەوە ئەگەر لابرا."""
    users = _load_allowed_users()
    if user_id not in users:
        return False
    users.discard(user_id)
    _save_allowed_users(users)
    return True


def list_allowed() -> list:
    """گەڕاندنەوەی لیستی ئایدیەکانی ڕێگەپێدراو."""
    return sorted(_load_allowed_users())