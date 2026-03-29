from flask import Flask, render_template, request
import pickle
import numpy as np
import sqlite3

app = Flask(__name__)

# ==============================
# Load ML Model
# ==============================
import os

model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
model = pickle.load(open(model_path, 'rb'))

# ==============================
# Create Database
# ==============================
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenure REAL,
            monthly REAL,
            total REAL,
            contract INTEGER,
            internet INTEGER,
            result TEXT,
            probability REAL
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ==============================
# Home Page
# ==============================
@app.route('/')
def home():
    return render_template('index.html')

# ==============================
# Prediction Route
# ==============================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input values
        tenure = float(request.form['tenure'])
        monthly = float(request.form['MonthlyCharges'])
        total = float(request.form['TotalCharges'])
        contract = int(request.form['Contract'])
        internet = int(request.form['InternetService'])

        # Prepare features
        features = np.array([[tenure, monthly, total, contract, internet]])

        # Prediction
        prediction = model.predict(features)[0]
        prob = model.predict_proba(features)[0][1]

        # Result text
        if prediction == 1:
            result = "Customer is likely to CHURN ❌"
        else:
            result = "Customer will STAY ✅"

        # ==============================
        # Save to Database
        # ==============================
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('''
            INSERT INTO predictions 
            (tenure, monthly, total, contract, internet, result, probability)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tenure, monthly, total, contract, internet, result, prob))

        conn.commit()
        conn.close()

        # Send to result page
        return render_template(
            'result.html',
            prediction_text=result,
            probability=round(prob * 100, 2)
        )

    except Exception as e:
        return f"Error: {str(e)}"

# ==============================
# Dashboard Route
# ==============================
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM predictions ORDER BY id DESC")
    data = c.fetchall()

    conn.close()

    return render_template('dashboard.html', data=data)

# ==============================
# Run App
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
