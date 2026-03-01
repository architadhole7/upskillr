# UpSkillr 
AI-Powered Skill Measurement & Growth Platform

# Overview

UpSkillr is a skill-measurement platform designed to help learners assess their abilities, receive AI-based evaluation, and follow a structured improvement roadmap.
It moves beyond marks and focuses on measurable skill growth.

# Problem Statement

Students often prepare without understanding their real strengths and weaknesses.
Most platforms provide scores but lack structured feedback and improvement guidance.

# Solution

UpSkillr enables users to:

-Add and manage skills
-Take AI-generated assessments
-Practice interview-style questions
-Submit custom Q&A for AI evaluation
-Track skill performance through analytics
-Generate personalized career roadmaps

# System Architecture

Frontend: HTML, CSS
Backend: Python (Flask)
Database: PostgreSQL (Neon DB)
AI Integration: Google Gemini API
Deployment: Render

# Process Flow

1. User adds skill
2. Takes assessment or interview practice
3. AI evaluates responses
4. Performance analytics generated
5. Personalized roadmap provided

# Installation & Setup

1️⃣ Clone the repository
git clone <your-repo-link>
cd upskillr

2️⃣ Create virtual environment

python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3️⃣ Install dependencies

pip install -r requirements.txt

4️⃣ Set environment variables

Create a .env file and add:
  GEMINI_API_KEY=your_api_key
  DATABASE_URL=your_neon_db_url

5️⃣ Run the application

python app.py

# Deployment

The application is deployed on Render.

Prototype Link: https://upskillr-v218.onrender.com

# ⚠️ Deployment Note

This prototype is deployed using Render’s free-tier infrastructure.
Due to free-tier limitations, the service may experience cold-start delays after periods of inactivity.

The application functions fully under standard deployment conditions and performs optimally when hosted on a paid production plan.

The system is compute-efficient and compatible with modern multi-core processor architectures, ensuring scalable performance under production environments.

# Future Enhancements

->Advanced analytics
->Multi-user performance comparison
->AI-driven adaptive difficulty
->Mobile-responsive optimization

# Demo Video Link:

https://drive.google.com/file/d/1Xx1KNMcn7imA76mSb-XTO2iW6XXhBW8p/view?usp=drivesdk




