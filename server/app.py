# server/app.py
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from models import db, User, StudyRecord
import bcrypt
import json
import re

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jlpt.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "jlpt-secret-key-2026"

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

# ── 유효성 검사 ───────────────────────────
def validate_username(username):
    if not username:
        return False, "아이디를 입력하세요"
    if len(username) < 4:
        return False, "아이디는 4자리 이상이어야 해요"
    if len(username) > 20:
        return False, "아이디는 20자리 이하여야 해요"
    if not re.match(r'^[a-zA-Z0-9]+$', username):
        return False, "아이디는 영어와 숫자만 사용할 수 있어요"
    return True, ""

def validate_password(password):
    if not password:
        return False, "비밀번호를 입력하세요"
    if len(password) < 6:
        return False, "비밀번호는 6자리 이상이어야 해요"
    return True, ""

# ── 회원가입 ──────────────────────────────
@app.route("/register", methods=["POST"])
def register():
    data     = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    nickname = data.get("nickname", "").strip()

    ok, msg = validate_username(username)
    if not ok:
        return jsonify({"error": msg}), 400

    ok, msg = validate_password(password)
    if not ok:
        return jsonify({"error": msg}), 400

    if not nickname:
        return jsonify({"error": "닉네임을 입력하세요"}), 400
    if len(nickname) > 20:
        return jsonify({"error": "닉네임은 20자 이하여야 해요"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "이미 사용 중인 아이디예요"}), 409

    hashed = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    user = User(username=username, password=hashed, nickname=nickname)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message" : "회원가입 성공!",
        "token"   : token,
        "nickname": nickname
    }), 201

# ── 로그인 ────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    data     = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "아이디와 비밀번호를 입력하세요"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "아이디 또는 비밀번호가 틀렸어요"}), 401

    if not bcrypt.checkpw(
        password.encode("utf-8"), user.password.encode("utf-8")
    ):
        return jsonify({"error": "아이디 또는 비밀번호가 틀렸어요"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message" : "로그인 성공!",
        "token"   : token,
        "nickname": user.nickname
    }), 200

# ── 학습 기록 저장 ────────────────────────
@app.route("/record", methods=["POST"])
@jwt_required()
def save_record():
    user_id    = int(get_jwt_identity())
    data       = request.get_json()
    study_date = data.get("date")
    words      = json.dumps(data.get("words", []))
    total_quiz = data.get("total_quiz", 0)
    correct    = data.get("correct", 0)

    existing = StudyRecord.query.filter_by(
        user_id=user_id, study_date=study_date).first()
    if existing:
        existing.words      = words
        existing.total_quiz = total_quiz
        existing.correct    = correct
    else:
        db.session.add(StudyRecord(
            user_id=user_id, study_date=study_date,
            words=words, total_quiz=total_quiz, correct=correct
        ))
    db.session.commit()
    return jsonify({"message": "저장 완료!"}), 200

# ── 학습 기록 불러오기 ────────────────────
@app.route("/records", methods=["GET"])
@jwt_required()
def get_records():
    user_id = int(get_jwt_identity())
    records = StudyRecord.query.filter_by(
        user_id=user_id
    ).order_by(StudyRecord.study_date.desc()).all()
    result = [{
        "date"      : r.study_date,
        "words"     : json.loads(r.words),
        "total_quiz": r.total_quiz,
        "correct"   : r.correct,
        "percent"   : int(r.correct / r.total_quiz * 100)
                      if r.total_quiz else 0
    } for r in records]
    return jsonify({"records": result}), 200

# ── 통계 ──────────────────────────────────
@app.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    from datetime import date, timedelta
    user_id       = int(get_jwt_identity())
    records       = StudyRecord.query.filter_by(user_id=user_id).all()
    total_correct = sum(r.correct for r in records)
    total_quiz    = sum(r.total_quiz for r in records)
    weekly        = []
    today         = date.today()
    for i in range(6, -1, -1):
        d   = today - timedelta(days=i)
        rec = StudyRecord.query.filter_by(
            user_id=user_id, study_date=str(d)).first()
        weekly.append({
            "date"   : str(d),
            "percent": int(rec.correct / rec.total_quiz * 100)
                       if rec and rec.total_quiz else 0
        })
    return jsonify({
        "total_days" : len(records),
        "avg_percent": int(total_correct / total_quiz * 100)
                       if total_quiz else 0,
        "weekly"     : weekly
    }), 200

# ── 내 정보 ───────────────────────────────
@app.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    user    = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "유저 없음"}), 404
    return jsonify({
        "username": user.username,
        "nickname": user.nickname
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)