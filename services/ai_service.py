import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# ================= HELPER: CLEAN JSON =================
def extract_json(text):
    """
    Safely extract JSON from Gemini response.
    Handles markdown, extra text, etc.
    """
    text = text.strip()

    # Remove markdown code blocks
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    # Try to extract JSON object using regex
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    return json.loads(text)


# ================= QUIZ QUESTION GENERATION =================
def generate_questions(skill, count):

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Generate {count} multiple choice questions for skill: {skill}.
    Return STRICT valid JSON only:
    [
      {{
        "question": "",
        "options": ["", "", "", ""],
        "correct_answer": ""
      }}
    ]
    """

    response = model.generate_content(prompt)
    text = response.text

    # Remove markdown
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    return json.loads(text)


# ================= COMMUNICATION EVALUATION =================
def evaluate_response(topic, response_text):

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    You are a professional interview evaluator.

    Question: {topic}
    Candidate Answer: {response_text}

    Evaluate and return STRICT JSON only:

    {{
        "score": integer between 0 and 10,
        "feedback": "detailed constructive feedback",
        "suggestions": "clear actionable improvement suggestions"
    }}
    """

    result = model.generate_content(prompt)
    text = result.text

    try:
        return extract_json(text)

    except Exception as e:
        print("Evaluation JSON Error:", e)
        print("Raw Gemini Response:", text)

        # Fallback safe response
        return {
            "score": 5,
            "feedback": "Evaluation could not be parsed correctly.",
            "suggestions": "Please try answering again more clearly."
        }


# ================= INTERVIEW QUESTION GENERATION =================
def generate_interview_question():

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = """
    Generate one realistic interview question.
    It can be HR, behavioral, or technical.
    Only return the question text.
    """

    result = model.generate_content(prompt)

    return result.text.strip()


# ================== CAREER VALIDATION =================


# services/ai_service.py

def validate_career(career):
    career_lower = career.lower()

    harmful = ["thief", "crime", "snatcher"]
    self_harm = ["die", "suicide", "kill myself"]

    if any(word in career_lower for word in harmful):
        return {
            "status": "blocked",
            "message": "We cannot assist with harmful or illegal career goals."
        }

    if any(word in career_lower for word in self_harm):
        return {
            "status": "blocked",
            "message": "If you're feeling overwhelmed, please consider speaking to someone you trust or a professional. You matter."
        }

    return {"status": "ok"}


# ================== ROADMAP GENERATION =================

def generate_roadmap(career):

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Generate a structured 6-step roadmap to become a {career}.

    Return STRICT valid JSON only in this exact format:

    {{
        "steps": [
            {{
                "title": "Step title",
                "details": [
                    "Actionable point 1",
                    "Actionable point 2",
                    "Actionable point 3"
                ]
            }}
        ]
    }}

    Rules:
    - Each step must contain 3-4 actionable and practical bullet points.
    - Avoid generic advice like "work hard" or "stay motivated".
    - Make guidance realistic and beginner-friendly.
    - Do NOT include harmful or illegal suggestions.
    """

    response = model.generate_content(prompt)
    text = response.text

    try:
        data = extract_json(text)
        return data.get("steps", [])

    except Exception as e:
        print("Roadmap JSON Error:", e)
        print("Raw Gemini Response:", text)

        # Safe fallback roadmap
        return [
            {
                "title": "Research the Career Path",
                "details": [
                    "Understand required qualifications",
                    "Identify core skills needed",
                    "Study job descriptions online"
                ]
            },
            {
                "title": "Build Core Skills",
                "details": [
                    "Take structured online courses",
                    "Practice consistently",
                    "Work on small real-world projects"
                ]
            }
        ]