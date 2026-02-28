from database.db import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON


class Skill(db.Model):
    __tablename__ = "skill"

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Test(db.Model):
    __tablename__ = "test"

    id = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.String(100), nullable=False)
    total_questions = db.Column(db.Integer)
    score = db.Column(db.Integer)
    percentage = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Question(db.Model):
    __tablename__ = "question"

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey("test.id"))
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(JSON)
    correct_answer = db.Column(db.String(255))
    selected_answer = db.Column(db.String(255))
    is_correct = db.Column(db.Boolean)


class Communication(db.Model):
    __tablename__ = "communication"

    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.String(50))  # practice / interview
    topic = db.Column(db.String(200))
    response = db.Column(db.Text)

    score = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    suggestions = db.Column(db.Text)

    session_id = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InterviewSession(db.Model):
    __tablename__ = "interview_session"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))
    average_score = db.Column(db.Float)
    total_questions = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LearningPath(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    career = db.Column(db.String(200))
    roadmap_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())