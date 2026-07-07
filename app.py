from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import joblib
import numpy as np
from datetime import datetime
from assessment_agent import StressAssessmentAgent
from werkzeug.security import generate_password_hash, check_password_hash
import os

# =========================================
# FLASK APPLICATION
# =========================================

app = Flask(__name__)
app.secret_key = "stresssystem"

# =========================================
# LOAD MACHINE LEARNING MODEL
# =========================================

model = joblib.load("model.pkl")

# =========================================
# CHATBOT AGENTS
# =========================================

agents = {}

# =========================================
# DATABASE CONNECTION
# =========================================

def get_db_connection():

    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row

    return conn


# =========================================
# HOME PAGE
# Registration Opens First
# =========================================

@app.route("/")
def home():

    return render_template("register.html")


# =========================================
# REGISTER PAGE
# =========================================

@app.route("/register")
def register():

    return render_template("register.html")


# =========================================
# LOGIN PAGE
# =========================================

@app.route("/login_page")
def login_page():

    return render_template("login.html")


# =========================================
# REGISTER USER
# =========================================

@app.route("/register_user", methods=["POST"])
def register_user():

    username = request.form["username"].strip()
    password = request.form["password"].strip()

    if username == "" or password == "":

        return "Username and Password are required."

    conn = get_db_connection()

    existing = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username=?
        """,
        (username,)
    ).fetchone()

    if existing:

        conn.close()
        return "Username already exists."

    hashed_password = generate_password_hash(password)

    conn.execute(
        """
        INSERT INTO users
        (
            username,
            password
        )
        VALUES (?, ?)
        """,
        (
            username,
            hashed_password
        )
    )

    conn.commit()
    conn.close()

    return redirect("/login_page")


# =========================================
# LOGIN USER
# =========================================

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"].strip()
    password = request.form["password"].strip()

    conn = get_db_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username=?
        """,
        (username,)
    ).fetchone()

    conn.close()

    if user is None:

        return "Invalid Username or Password."

    if not check_password_hash(user["password"], password):

        return "Invalid Username or Password."

    session["username"] = username

    return redirect("/dashboard")


# =========================================
# DASHBOARD
# =========================================

@app.route("/dashboard")
def dashboard():

    if "username" not in session:

        return redirect("/login_page")

    username = session["username"]

    conn = get_db_connection()

    # Total Predictions
    total = conn.execute(
        """
        SELECT COUNT(*)
        FROM predictions
        WHERE username=?
        """,
        (username,)
    ).fetchone()[0]

    # Total Stressed
    stressed = conn.execute(
        """
        SELECT COUNT(*)
        FROM predictions
        WHERE username=?
        AND prediction='STRESSED'
        """,
        (username,)
    ).fetchone()[0]

    # Total Not Stressed
    not_stressed = conn.execute(
        """
        SELECT COUNT(*)
        FROM predictions
        WHERE username=?
        AND prediction='NOT STRESSED'
        """,
        (username,)
    ).fetchone()[0]
        # Recent Activities
    history = conn.execute(
        """
        SELECT *
        FROM predictions
        WHERE username=?
        ORDER BY id DESC
        LIMIT 5
        """,
        (username,)
    ).fetchall()

    # Stress Rate
    if total > 0:
        stress_rate = round((stressed / total) * 100, 1)
    else:
        stress_rate = 0

    conn.close()

    return render_template(
        "dashboard.html",
        username=username,
        total=total,
        stressed=stressed,
        not_stressed=not_stressed,
        stress_rate=stress_rate,
        history=history
    )
# =========================================
# PREDICTION SYSTEM
# =========================================

@app.route("/predict", methods=["POST"])
def predict():

    if "username" not in session:
        return redirect("/login_page")

    username = session["username"]

    # ==========================
    # ACADEMIC INFORMATION
    # ==========================

    study_hours = float(request.form["study_hours"])
    sleep_hours = float(request.form["sleep_hours"])
    break_frequency = float(request.form["break_frequency"])

    courses = int(request.form["courses"])
    workload = int(request.form["workload"])
    exam = int(request.form["exam"])
    attendance = request.form["attendance"]

    # ==========================
    # HEALTH & LIFESTYLE
    # ==========================

    exercise = int(request.form["exercise"])
    meals = int(request.form["meals"])
    screen_time = int(request.form["screen_time"])

    # ==========================
    # MENTAL WELLBEING
    # ==========================

    anxiety = int(request.form["anxiety"])
    motivation = int(request.form["motivation"])
    concentration = int(request.form["concentration"])
    mood = int(request.form["mood"])
    energy = int(request.form["energy"])

    # ==========================
    # FINANCIAL
    # ==========================

    financial_stress = int(request.form["financial_stress"])
    allowance = int(request.form["allowance"])

    # ==========================
    # SOCIAL
    # ==========================

    family_support = int(request.form["family_support"])
    friend_support = int(request.form["friend_support"])
    social_activity = int(request.form["social_activity"])

    # ==========================
    # MACHINE LEARNING PREDICTION
    # ==========================

    features = np.array([
        [study_hours, sleep_hours, break_frequency]
    ])

    prediction = model.predict(features)

    if prediction[0] == 1:
        result = "STRESSED"
    else:
        result = "NOT STRESSED"

    # ==========================
    # CALCULATE SCORES
    # ==========================

    academic_score = study_hours + courses + workload + exam

    health_score = (
        sleep_hours +
        break_frequency +
        exercise +
        meals
    )

    mental_score = (
        anxiety +
        motivation +
        concentration +
        mood +
        energy
    )

    financial_score = (
        financial_stress +
        allowance
    )

    social_score = (
        family_support +
        friend_support +
        social_activity
    )

    # ==========================
    # STRESS LEVEL FUNCTION
    # ==========================

    def level(score, low, medium):

        if score <= low:
            return "LOW"

        elif score <= medium:
            return "MODERATE"

        else:
            return "HIGH"

    academic_level = level(academic_score, 10, 16)
    health_level = level(health_score, 8, 13)
    mental_level = level(mental_score, 10, 18)
    financial_level = level(financial_score, 3, 6)
    social_level = level(social_score, 5, 9)

    # ==========================
    # RECOMMENDATIONS
    # ==========================

    recommendations = []

    if academic_level == "HIGH":
        recommendations.append(
            "📚 Reduce academic workload and create a realistic study timetable."
        )

    if health_level == "HIGH":
        recommendations.append(
            "😴 Improve your sleep schedule, eat balanced meals and exercise regularly."
        )

    if mental_level == "HIGH":
        recommendations.append(
            "🧠 Practice relaxation techniques and consider speaking with a counsellor."
        )

    if financial_level == "HIGH":
        recommendations.append(
            "💰 Seek financial assistance or improve budgeting to reduce financial stress."
        )

    if social_level == "HIGH":
        recommendations.append(
            "👨‍👩‍👧 Spend more time with supportive friends and family."
        )

    if result == "STRESSED":
        recommendations.append(
            "🎯 Your assessment indicates elevated stress. Consider visiting your university counselling centre if symptoms persist."
        )

    if len(recommendations) == 0:
        recommendations.append(
            "✅ Great job! Continue maintaining your healthy lifestyle and study habits."
        )

    if health_level == "HIGH":
        recommendations.append(
            "😴 Improve your sleep schedule, eat balanced meals and exercise regularly."
        )

    if mental_level == "HIGH":
        recommendations.append(
            "🧠 Practice relaxation techniques and consider speaking with a counsellor."
        )

    if financial_level == "HIGH":
        recommendations.append(
            "💰 Seek financial assistance or improve budgeting to reduce financial stress."
        )

    if social_level == "HIGH":
        recommendations.append(
            "👨‍👩‍👧 Spend more time with supportive friends and family members."
        )

    if result == "STRESSED":
        recommendations.append(
            "🎯 Overall assessment indicates elevated stress. Consider visiting your university counselling centre if symptoms persist."
        )

    if len(recommendations) == 0:

        recommendations.append(
            "✅ Great job! Your responses suggest healthy stress management habits. Continue maintaining a balanced lifestyle."
        )
    # ==========================
    # SAVE PREDICTION
    # ==========================

    conn = get_db_connection()

    conn.execute(
        '''
        INSERT INTO predictions
        (
            username,
            study_hours,
            sleep_hours,
            break_frequency,
            prediction,
            date
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (
            username,
            study_hours,
            sleep_hours,
            break_frequency,
            result,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )
    )

    conn.commit()
    conn.close()

    # ==========================
    # DISPLAY RESULT
    # ==========================

    return render_template(

        'result.html',

        prediction=result,

        academic_level=academic_level,
        health_level=health_level,
        mental_level=mental_level,
        financial_level=financial_level,
        social_level=social_level,

        study_hours=study_hours,
        sleep_hours=sleep_hours,
        break_frequency=break_frequency,

        recommendations=recommendations
    )


# =========================================
# PREDICTION HISTORY
# =========================================

@app.route("/history")
def history():

    if "username" not in session:
        return redirect("/login_page")

    username = session["username"]

    conn = get_db_connection()

    predictions = conn.execute(

        """
        SELECT *
        FROM predictions
        WHERE username=?
        ORDER BY id DESC
        """,

        (username,)

    ).fetchall()

    conn.close()

    return render_template(

        "history.html",

        predictions=predictions

    )


# =========================================
# INPUT PAGE
# =========================================

@app.route("/input")
def input_page():

    if "username" not in session:
        return redirect("/login_page")

    return render_template("input.html")


# =========================================
# ADVICE CENTER
# =========================================

@app.route("/advice")
def advice():

    if "username" not in session:
        return redirect("/login_page")

    return render_template("advice.html")


# =========================================
# CHATBOT PAGE
# =========================================

@app.route("/chatbot")
def chatbot():

    if "username" not in session:
        return redirect("/login_page")

    return render_template("chatbot.html")


# =========================================
# CHATBOT API
# =========================================

@app.route("/chat", methods=["POST"])
def chat():

    if "username" not in session:

        return jsonify({

            "reply": "Please login first."

        })

    username = session["username"]

    message = request.json.get("message", "").strip()

    if username not in agents:

        agents[username] = StressAssessmentAgent()

    response = agents[username].reply(message)

    return jsonify(response)


# =========================================
# RESET CHATBOT
# =========================================

@app.route("/reset_chat")
def reset_chat():

    if "username" not in session:
        return redirect("/login_page")

    username = session["username"]

    if username in agents:

        agents[username].reset()

    return redirect("/chatbot")


# =========================================
# LOGOUT
# =========================================

@app.route("/logout")
def logout():

    username = session.get("username")

    if username in agents:

        del agents[username]

    session.clear()

    return redirect("/")


# =========================================
# RUN APPLICATION
# =========================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 3000))

    app.run(

        host="0.0.0.0",

        port=port,

        debug=False

    )