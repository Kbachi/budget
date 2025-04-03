from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import os
from datetime import datetime
import category_keywords

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
CSV_FILE = 'finance.csv'
FIELDNAMES = ['Date', 'Description', 'Category', 'Amount']

def initialize_csv():
    """Create the CSV file with headers if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def get_category(description):
    """
    Determine the category for a given description based on keywords.
    Searches each category's list of keywords from category_keywords.py.
    Returns the first matching category or 'Uncategorized' if none match.
    """
    for category, keywords in category_keywords.CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in description.lower():
                return category
    return "Uncategorized"

def add_transaction(date, description, amount):
    """
    Add a new transaction to the CSV file.
    The category is automatically determined from the description.
    """
    category = get_category(description)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow({
            'Date': date,
            'Description': description,
            'Category': category,
            'Amount': amount
        })

def calculate_balance():
    """Read the CSV and sum up the amounts to calculate the current balance."""
    balance = 0.0
    if not os.path.exists(CSV_FILE):
        return balance
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                balance += float(row['Amount'])
            except ValueError:
                pass  # Ignore invalid amounts
    return balance

def get_transactions():
    """Retrieve all transactions from the CSV file."""
    transactions = []
    if not os.path.exists(CSV_FILE):
        return transactions
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions.append(row)
    return transactions

@app.route('/', methods=['GET', 'POST'])
def index():
    initialize_csv()
    if request.method == 'POST':
        # Use provided date or default to today if not given
        date_input = request.form.get('date')
        if not date_input:
            date_input = datetime.today().strftime("%Y-%m-%d")
        description = request.form.get('description')
        amount_input = request.form.get('amount')
        try:
            amount = float(amount_input)
        except (ValueError, TypeError):
            flash("Invalid amount entered. Please try again.")
            return redirect(url_for('index'))
        
        add_transaction(date_input, description, amount)
        flash("Transaction added successfully!")
        return redirect(url_for('index'))
    
    # For GET requests, calculate balance and load transactions
    balance = calculate_balance()
    transactions = get_transactions()
    return render_template('balance.html', balance=balance, transactions=transactions)

if __name__ == "__main__":
    app.run(debug=True)
