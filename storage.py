# storage.py
import json
import os
from datetime import date

SAVE_FILE  = "progress.json"
TOKEN_FILE = "token.json"      # ← 로그인 토큰 저장 파일

# ══════════════════════════════════════════
# 토큰 저장/불러오기
# ══════════════════════════════════════════

def save_token(token, nickname):
    """로그인 토큰을 로컬에 저장"""
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump({"token": token, "nickname": nickname}, f)

def load_token():
    """저장된 토큰 불러오기 → (token, nickname) 또는 (None, None)"""
    if not os.path.exists(TOKEN_FILE):
        return None, None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("token"), data.get("nickname")
    except Exception:
        return None, None

def clear_token():
    """로그아웃 시 토큰 삭제"""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

# ══════════════════════════════════════════
# 학습 데이터
# ══════════════════════════════════════════

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    raise ValueError
                return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            pass
    return {"history": []}

def save_data(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_daily_record(words, total_quiz, correct):
    data  = load_data()
    today = str(date.today())
    record = {
        "date"      : today,
        "words"     : [w["japanese"] for w in words],
        "total_quiz": total_quiz,
        "correct"   : correct
    }
    for i, h in enumerate(data["history"]):
        if h["date"] == today:
            data["history"][i] = record
            save_data(data)
            return
    data["history"].append(record)
    save_data(data)

def get_history():
    return load_data().get("history", [])

def is_studied_today():
    today = str(date.today())
    return any(h["date"] == today for h in get_history())