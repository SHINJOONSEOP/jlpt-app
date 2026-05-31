# server/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(20), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    nickname   = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    records    = db.relationship("StudyRecord", backref="user", lazy=True)

class StudyRecord(db.Model):
    __tablename__ = "study_records"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    study_date = db.Column(db.String(20), nullable=False)
    words      = db.Column(db.Text, nullable=False)
    total_quiz = db.Column(db.Integer, default=0)
    correct    = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)