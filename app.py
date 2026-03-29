from flask import Flask, render_template, request
import pickle
import numpy as np
import sqlite3
import os

app = Flask(__name__)


model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
model = pickle.load(open(model_path, 'rb'))

db_path = os.path.join(os.path.dirname(__file__), 'database.db')


def init_db():
    try:
        conn = sqlite3.connect(db_path)
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
    except Exception as e:
        print("DB Error:", e)

init_db()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        tenure = float(request.form['tenure'])
        monthly = float(request.form['MonthlyCharges'])
        total = float(request.form['TotalCharges'])
        contract = int(request.form['Contract'])
        internet = int(request.form['InternetService'])

        features = np.array([[tenure, monthly, total, contract, internet]])

        prediction = model.predict(features)[0]
        prob = model.predict_proba(features)[0][1]

        if prediction == 1:
            result = "Customer is likely to CHURN ❌"
        else:
            result = "Customer will STAY ✅"

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute('''
            INSERT INTO predictions 
            (tenure, monthly, total, contract, internet, result, probability)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tenure, monthly, total, contract, internet, result, prob))

        conn.commit()
        conn.close()

        return render_template(
            'result.html',
            prediction_text=result,
            probability=round(prob * 100, 2)
        )

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT * FROM predictions ORDER BY id DESC")
    data = c.fetchall()

    conn.close()

    return render_template('dashboard.html', data=data)

if __name__ == "__main__":
    app.run()
