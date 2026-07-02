from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import joblib
import numpy as np
from datetime import datetime
from assessment_agent import StressAssessmentAgent

app = Flask(__name__)

app.secret_key = "stresssystem"

# LOAD MACHINE LEARNING MODEL
model = joblib.load('model.pkl')

# CREATE CHATBOT AGENT
agents = {}

def get_db_connection():

    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row

    return conn


# =========================================
# LOGIN PAGE
# =========================================

@app.route('/')
def home():

    return render_template('login.html')


# =========================================
# REGISTER PAGE
# =========================================

@app.route('/register')
def register():

    return render_template('register.html')


# =========================================
# REGISTER USER
# =========================================

@app.route('/register_user', methods=['POST'])
def register_user():

    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()

    conn.execute(
        '''
        INSERT INTO users (username, password)
        VALUES (?, ?)
        ''',
        (username, password)
    )

    conn.commit()
    conn.close()

    return redirect('/')


# =========================================
# LOGIN USER
# =========================================

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()

    user = conn.execute(
        '''
        SELECT * FROM users
        WHERE username=? AND password=?
        ''',
        (username, password)
    ).fetchone()

    conn.close()

    if user:

        session['username'] = username

        return redirect('/dashboard')

    return "Invalid Login Details"

# =========================================
# DASHBOARD
# =========================================

@app.route('/dashboard')
def dashboard():

    if 'username' not in session:
        return redirect('/')

    username = session['username']

    conn = get_db_connection()

    # TOTAL PREDICTIONS
    total = conn.execute(
        '''
        SELECT COUNT(*) FROM predictions
        WHERE username=?
        ''',
        (username,)
    ).fetchone()[0]

    # TOTAL STRESSED
    stressed = conn.execute(
        '''
        SELECT COUNT(*) FROM predictions
        WHERE username=? AND prediction='STRESSED'
        ''',
        (username,)
    ).fetchone()[0]

    # TOTAL NOT STRESSED
    not_stressed = conn.execute(
        '''
        SELECT COUNT(*) FROM predictions
        WHERE username=? AND prediction='NOT STRESSED'
        ''',
        (username,)
    ).fetchone()[0]

    # RECENT ACTIVITIES
    history = conn.execute(
        '''
        SELECT * FROM predictions
        WHERE username=?
        ORDER BY id DESC
        LIMIT 5
        ''',
        (username,)
    ).fetchall()

    # STRESS RATE
    if total > 0:

        stress_rate = round(
            (stressed / total) * 100,
            1
        )

    else:

        stress_rate = 0

    conn.close()

    return render_template(

        'dashboard.html',

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

@app.route('/predict', methods=['POST'])
def predict():

    if 'username' not in session:
        return redirect('/')

    username = session['username']

    study_hours = float(request.form['study_hours'])
    sleep_hours = float(request.form['sleep_hours'])
    break_frequency = float(request.form['break_frequency'])

    features = np.array([
        [study_hours, sleep_hours, break_frequency]
    ])

    prediction = model.predict(features)

    # STRESS RESULT
    if prediction[0] == 1:

        result = "STRESSED"

        recommendations = [

            "Take short study breaks regularly.",

            "Improve your sleeping pattern.",

            "Avoid academic overload.",

            "Practice relaxation techniques.",

            "Stay hydrated and eat healthy meals."
        ]

    else:

        result = "NOT STRESSED"

        recommendations = [

            "Maintain your healthy routine.",

            "Continue balancing study and rest.",

            "Keep practicing proper time management.",

            "Stay physically active."
        ]

    # SAVE PREDICTION
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

    return render_template(
        'result.html',

        prediction=result,

        recommendations=recommendations
    )


# =========================================
# PREDICTION HISTORY
# =========================================

@app.route('/history')
def history():

    if 'username' not in session:
        return redirect('/')

    username = session['username']

    conn = get_db_connection()

    predictions = conn.execute(
        '''
        SELECT * FROM predictions
        WHERE username=?
        ORDER BY id DESC
        ''',
        (username,)
    ).fetchall()

    conn.close()

    return render_template(
        'history.html',

        predictions=predictions
    )


# =========================================
# ADVICE CENTER
# =========================================

@app.route('/advice')
def advice():

    if 'username' not in session:
        return redirect('/')

    username = session['username']


    return render_template('advice.html')


# =========================================
# CHATBOT PAGE
# =========================================

@app.route('/chatbot')
def chatbot():

    if 'username' not in session:
        return redirect('/')

    return render_template('chatbot.html')

# =========================================
# CHATBOT API
# =========================================

@app.route('/chat', methods=['POST'])
def chat():

    if 'username' not in session:
        return jsonify({"reply": "Please login first."})

    message = request.json.get("message")

    username = session['username']

    if username not in agents:
        agents[username] = StressAssessmentAgent()

    response = agents[username].reply(message)

    return jsonify(response)


# =========================================
# RESET CHAT
# =========================================

@app.route('/reset_chat')
def reset_chat():

    if 'username' not in session:
        return redirect('/')

    username = session['username']

    if username in agents:
        agents[username].reset()

    return redirect('/chatbot')


# =========================================
# LOGOUT
# =========================================

@app.route('/logout')
def logout():

    session.pop('username', None)

    return redirect('/')


# =========================================
# INPUT PAGE
# =========================================

@app.route('/input')
def input_page():

    if 'username' not in session:
        return redirect('/')

    return render_template('input.html')

# =========================================
# RUN APPLICATION
# =========================================

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=False)