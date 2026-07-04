import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Absolute path to .env
env_path = Path(__file__).resolve().parent.parent / ".env"

print("ENV Path:", env_path)
print("ENV Exists:", env_path.exists())

loaded = load_dotenv(dotenv_path=env_path)

print("Loaded:", loaded)
for k, v in os.environ.items():
    if "GROQ" in k.upper():
        print(k, "=", v)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_questions(role, difficulty, count):

    prompt = f"""
You are an expert technical interviewer.

Generate exactly {count} interview questions.

Role: {role}
Difficulty: {difficulty}

Rules:
- Return only numbered interview questions.
- Do NOT provide answers.
- Make the questions suitable for the selected difficulty.
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1024
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI Error: {str(e)}"

def evaluate_answer(question, answer):

    prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer.

Question:
{question}

Candidate Answer:
{answer}

Respond in exactly this format:

Score: <0-100>

Strengths:
- ...

Weaknesses:
- ...

Suggestions:
- ...
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI Error: {e}"    