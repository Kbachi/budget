from flask import Flask, render_template, jsonify
import os
import csv
from datetime import datetime

app = Flask(__name__)

FINANCE_FILE = "finance.csv"

def get_latest_balance(filename=FINANCE_FILE):
    try:
        with open(filename, mode='r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                return 0.0
            return float(rows[-1]["Balance"])
    except Exception as e:
        print("Error reading balance:", e)
        return 0.0

@app.route('/')
def index():
    return render_template('finance.html')

@app.route('/get_balance')
def get_balance():
    balance = get_latest_balance()
    return jsonify({"balance": balance})

if __name__ == "__main__":
    app.run(debug=True)
