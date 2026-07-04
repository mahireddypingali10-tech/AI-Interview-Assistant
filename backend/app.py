from ai import generate_questions, evaluate_answer
from flask import Flask, render_template, request, redirect, url_for, session
from database import get_db_connection
import bcrypt

app = Flask(__name__)

app.secret_key = "interview_ai_secret_key"


@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing = cursor.fetchone()

        if existing:
            conn.close()
            return "Email already exists!"

        cursor.execute(
            """
            INSERT INTO users(fullname,email,password)
            VALUES(%s,%s,%s)
            """,
            (
                fullname,
                email,
                hashed_password.decode("utf-8")
            )
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            if bcrypt.checkpw(
                password.encode("utf-8"),
                user["password"].encode("utf-8")
            ):

                session["user"] = user["fullname"]
                session["user_id"] = user["id"]

                return redirect("/dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM performance
        WHERE user_id=%s
        LIMIT 1
    """, (session["user_id"],))

    performance = cursor.fetchone()

    conn.close()

    return render_template(
        "dashboard.html",
        user=session["user"],
        performance=performance
    )

# ---------------- INTERVIEW ----------------

@app.route("/interview")
def interview():

    if "user" not in session:
        return redirect("/login")

    return render_template("interview.html")

@app.route("/start-interview", methods=["POST"])
def start_interview():

    role = request.form["role"]
    difficulty = request.form["difficulty"]
    count = int(request.form["questions"])

    questions = generate_questions(role, difficulty, count)

    question_list = [
        q.strip()
        for q in questions.split("\n")
        if q.strip()
    ]

    session["questions"] = question_list
    session["role"] = role
    session["difficulty"] = difficulty
    session["current_question"] = 0

    return render_template(
        "answer.html",
        question_no=1,
        total_questions=len(question_list),
        question=question_list[0],
        role=role,
        difficulty=difficulty
    )

@app.route("/evaluate-answer", methods=["POST"])
def evaluate():

    question = request.form["question"]
    answer = request.form["answer"]

    feedback = evaluate_answer(question, answer)

    session["current_question"] += 1

    finished = session["current_question"] >= len(session["questions"])

    return render_template(
        "result.html",
        feedback=feedback,
        finished=finished
    )

@app.route("/next-question")
def next_question():

    index = session["current_question"]

    questions = session["questions"]

    return render_template(
        "answer.html",
        question_no=index + 1,
        total_questions=len(questions),
        question=questions[index],
        role=session["role"],
        difficulty=session["difficulty"]
    )

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)