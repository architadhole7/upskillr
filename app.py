from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from database.db import db
from database.models import Skill, Test, Question, Communication
from services.ai_service import generate_questions, evaluate_response
import json
import uuid
from services.ai_service import generate_questions, evaluate_response, generate_interview_question
import re
from database.models import InterviewSession
from services.ai_service import generate_roadmap, validate_career
import os




app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.context_processor
def inject_request():
    return dict(request=request)


# ================= HOME =================
@app.route("/")
def index():
    skills = Skill.query.all()
    return render_template("index.html", skills=skills)


# ================= DASHBOARD =================
from database.models import InterviewSession
from database.models import InterviewSession, LearningPath

@app.route("/dashboard")
def dashboard():

    total_skills = Skill.query.count()
    latest_test = Test.query.order_by(Test.created_at.desc()).first()
    total_comm = Communication.query.count()
    

    # ================= QUIZ ANALYTICS =================
    tests = Test.query.order_by(Test.created_at).all()
    labels = [t.created_at.strftime("%d %b") for t in tests]
    scores = [t.percentage for t in tests]

    # ================= PRACTICE COMMUNICATION ANALYTICS =================
    comm_entries = Communication.query.order_by(Communication.created_at).all()
    comm_labels = [c.created_at.strftime("%d %b") for c in comm_entries]
    comm_scores = [c.score for c in comm_entries if c.score is not None]

    # ================= INTERVIEW SESSION ANALYTICS =================
    interviews = InterviewSession.query.order_by(
        InterviewSession.created_at
    ).all()

    interview_labels = [i.created_at.strftime("%d %b") for i in interviews]
    interview_scores = [i.average_score for i in interviews]

    latest_interview_score = interviews[-1].average_score if interviews else 0

    # Optional improvement calculation
    improvement = 0
    if len(interview_scores) >= 2:
        improvement = round(
            interview_scores[-1] - interview_scores[0], 2
        )
    learning_paths = LearningPath.query.order_by(LearningPath.created_at.desc()).all()
    return render_template(
        "dashboard.html",
        total_skills=total_skills,
        latest_score=latest_test.score if latest_test else 0,
        total_comm=total_comm,
        labels=labels,
        scores=scores,
        comm_labels=comm_labels,
        comm_scores=comm_scores,
        interview_labels=interview_labels,
        interview_scores=interview_scores,
        latest_interview_score=latest_interview_score,
        improvement=improvement,
        learning_paths=learning_paths 
    )
# ================= ADD SKILL =================
@app.route("/add-skill", methods=["POST"])
def add_skill():
    skill_name = request.form.get("skill")

    if not skill_name:
        flash("Skill name cannot be empty")
        return redirect(url_for("index"))

    new_skill = Skill(skill_name=skill_name)
    db.session.add(new_skill)
    db.session.commit()

    return redirect(url_for("skills_page"))


# ================= DELETE SKILL (AJAX) =================
@app.route("/delete-skill/<int:skill_id>", methods=["DELETE"])
def delete_skill(skill_id):
    skill = Skill.query.get(skill_id)

    if skill:
        db.session.delete(skill)
        db.session.commit()
        return {"success": True}

    return {"success": False}, 404


# ================= START TEST =================
@app.route("/start-test", methods=["POST"])
def start_test():

    skill = request.form.get("skill")
    count = request.form.get("count")

    if not skill or not count:
        flash("Please select skill and question count.")
        return redirect(url_for("quiz_page"))

    count = int(count)

    try:
        questions = generate_questions(skill, count)
    except Exception as e:
        flash("AI failed to generate questions. Try again.")
        print("Gemini Error:", e)
        return redirect(url_for("quiz_page"))

    if not isinstance(questions, list):
        flash("Invalid AI response. Try again.")
        return redirect(url_for("quiz_page"))

    return render_template("quiz.html", questions=questions, skill=skill)


# ================= SUBMIT TEST =================
@app.route("/submit-test", methods=["POST"])
def submit_test():

    total = int(request.form.get("total"))
    skill = request.form.get("skill")

    score = 0

    new_test = Test(skill=skill, total_questions=total)
    db.session.add(new_test)
    db.session.commit()

    for i in range(total):

        selected = request.form.get(f"q{i}")
        correct = request.form.get(f"correct{i}")
        question_text = request.form.get(f"question{i}")
        options_raw = request.form.get(f"options{i}")

        try:
            options = json.loads(options_raw) if options_raw else None
        except:
            options = None

        is_correct = selected == correct
        if is_correct:
            score += 1

        new_question = Question(
            test_id=new_test.id,
            question_text=question_text,
            options=options,
            correct_answer=correct,
            selected_answer=selected,
            is_correct=is_correct
        )

        db.session.add(new_question)

    percentage = (score / total) * 100
    new_test.score = score
    new_test.percentage = percentage

    db.session.commit()

    return redirect(url_for("dashboard"))


# ================= COMMUNICATION (AI EVALUATED) =================
@app.route("/communication", methods=["GET", "POST"])
def communication():

    if request.method == "POST":
        topic = request.form.get("topic")
        response_text = request.form.get("response")

        if topic and response_text:
            try:
                evaluation = evaluate_response(topic, response_text)

                new_entry = Communication(
                    topic=topic,
                    response=response_text,
                    score=evaluation.get("score"),
                    feedback=evaluation.get("feedback"),
                    suggestions=evaluation.get("suggestions")
                )

                db.session.add(new_entry)
                db.session.commit()

            except Exception as e:
                print("Communication Evaluation Error:", e)
                flash("AI evaluation failed. Try again.")

        return redirect(url_for("communication"))

    entries = Communication.query.order_by(
        Communication.created_at.desc()
    ).all()

    return render_template("communication.html", entries=entries)


# ================= SKILLS PAGE =================
@app.route("/skills")
def skills_page():
    skills = Skill.query.all()
    return render_template("skills.html", skills=skills)


# ================= QUIZ START PAGE =================
@app.route("/quiz")
def quiz_page():
    skills = Skill.query.all()
    return render_template("quiz_start.html", skills=skills)

@app.route("/communication/practice", methods=["GET", "POST"])
def communication_practice():

    if request.method == "POST":
        topic = request.form.get("topic")
        response_text = request.form.get("response")

        evaluation = evaluate_response(topic, response_text)

        new_entry = Communication(
            mode="practice",
            topic=topic,
            response=response_text,
            score=evaluation["score"],
            feedback=evaluation["feedback"],
            suggestions=evaluation["suggestions"]
        )

        db.session.add(new_entry)
        db.session.commit()

        return redirect(url_for("communication_practice"))

    entries = Communication.query.filter_by(mode="practice")\
        .order_by(Communication.created_at.desc()).all()

    return render_template("communication_practice.html", entries=entries)



@app.route("/communication/interview", methods=["GET", "POST"])
def communication_interview():

    MAX_QUESTIONS = 5

    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
        session["question_count"] = 0

    evaluation = None
    question = None

    if request.method == "POST":

        topic = request.form.get("question")
        answer = request.form.get("answer")

        evaluation = evaluate_response(topic, answer)

        new_entry = Communication(
            mode="interview",
            topic=topic,
            response=answer,
            score=evaluation["score"],
            feedback=evaluation["feedback"],
            suggestions=evaluation["suggestions"],
            session_id=session["session_id"]
        )

        db.session.add(new_entry)
        db.session.commit()

        session["question_count"] += 1

        # Stop after MAX_QUESTIONS
        if session["question_count"] >= MAX_QUESTIONS:
            return redirect(url_for("interview_summary"))

        # Show evaluation first
        question = generate_interview_question()

        return render_template(
            "communication_interview.html",
            question=question,
            evaluation=evaluation,
            question_number=session["question_count"]
        )

    # First GET request
    question = generate_interview_question()

    return render_template(
        "communication_interview.html",
        question=question,
        evaluation=None,
        question_number=session["question_count"]
    )

@app.route("/communication/interview-summary")
def interview_summary():

    session_id = session.get("session_id")

    entries = Communication.query.filter_by(
        session_id=session_id,
        mode="interview"
    ).all()

    if not entries:
        return redirect(url_for("communication"))

    avg_score = sum(e.score for e in entries) / len(entries)

    # 🔥 Save interview session
    new_session = InterviewSession(
        session_id=session_id,
        average_score=avg_score,
        total_questions=len(entries)
    )

    db.session.add(new_session)
    db.session.commit()

    session.clear()

    return render_template(
        "interview_summary.html",
        entries=entries,
        avg_score=round(avg_score, 2)
    )


# ================== ROADMAP GENERATION =================


@app.route("/roadmap", methods=["POST"])
def roadmap():
    career = request.form.get("career")

    validation = validate_career(career)

    if validation["status"] == "blocked":
        flash(validation["message"])
        return redirect(url_for("career_roadmap_page"))

    steps = generate_roadmap(career)

    return render_template("roadmap.html", career=career, steps=steps)

@app.route("/save-roadmap", methods=["POST"])
def save_roadmap():

    career = request.form.get("career")
    roadmap_json = request.form.get("roadmap_json")

    from database.models import LearningPath

    new_path = LearningPath(
        career=career,
        roadmap_json=roadmap_json
    )

    db.session.add(new_path)
    db.session.commit()

    flash("Roadmap saved successfully!")
    return redirect(url_for("dashboard"))

@app.route("/delete-learning/<int:id>", methods=["POST"])
def delete_learning_path(id):

    from database.models import LearningPath

    path = LearningPath.query.get(id)

    if path:
        db.session.delete(path)
        db.session.commit()

    return redirect(url_for("dashboard"))

@app.route("/career-roadmap")
def career_roadmap_page():
    return render_template("career_roadmap.html")

# ================= RUN =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
