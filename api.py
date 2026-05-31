# api.py
import requests
from storage import save_token, load_token, clear_token

SERVER_URL = "http://127.0.0.1:5000"  # ← 나중에 배포 후 변경

_token    = None
_nickname = None

def set_token(token, nickname, persist=True):
    """토큰 설정 + 로컬 저장"""
    global _token, _nickname
    _token    = token
    _nickname = nickname
    if persist and token != "offline":
        save_token(token, nickname)

def get_nickname():
    return _nickname

def is_logged_in():
    return _token is not None

def try_auto_login():
    """앱 시작 시 저장된 토큰으로 자동 로그인 시도"""
    token, nickname = load_token()
    if not token:
        return False
    # 서버에 토큰 유효성 확인
    try:
        res = requests.get(
            f"{SERVER_URL}/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type" : "application/json"
            },
            timeout=3
        )
        if res.status_code == 200:
            set_token(token, nickname, persist=False)
            return True
    except Exception:
        # 서버 연결 실패해도 토큰은 유지 (오프라인 상태)
        set_token(token, nickname, persist=False)
        return True
    return False

def logout():
    """로그아웃 — 토큰 삭제"""
    global _token, _nickname
    _token    = None
    _nickname = None
    clear_token()

def _headers():
    return {
        "Authorization": f"Bearer {_token}",
        "Content-Type" : "application/json"
    }

def register(username, password, nickname):
    try:
        res  = requests.post(
            f"{SERVER_URL}/register",
            json={"username": username,
                  "password": password,
                  "nickname": nickname},
            timeout=5
        )
        data = res.json()
        if res.status_code == 201:
            set_token(data["token"], data["nickname"])
            return True, "회원가입 성공!"
        return False, data.get("error", "오류 발생")
    except Exception as e:
        return False, f"서버 연결 실패: {e}"

def login(username, password):
    try:
        res  = requests.post(
            f"{SERVER_URL}/login",
            json={"username": username, "password": password},
            timeout=5
        )
        data = res.json()
        if res.status_code == 200:
            set_token(data["token"], data["nickname"])
            return True, "로그인 성공!"
        return False, data.get("error", "오류 발생")
    except Exception as e:
        return False, f"서버 연결 실패: {e}"

def save_record(words, total_quiz, correct):
    from datetime import date
    try:
        requests.post(
            f"{SERVER_URL}/record",
            headers=_headers(),
            json={
                "date"      : str(date.today()),
                "words"     : [w["japanese"] for w in words],
                "total_quiz": total_quiz,
                "correct"   : correct
            },
            timeout=5
        )
    except Exception:
        pass

def get_records():
    try:
        res = requests.get(
            f"{SERVER_URL}/records",
            headers=_headers(), timeout=5)
        if res.status_code == 200:
            return res.json().get("records", [])
    except Exception:
        pass
    return []

def get_stats():
    try:
        res = requests.get(
            f"{SERVER_URL}/stats",
            headers=_headers(), timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {"total_days": 0, "avg_percent": 0, "weekly": []}