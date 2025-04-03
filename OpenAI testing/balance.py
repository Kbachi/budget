import os
import csv
from datetime import datetime, timedelta
import re
from finance_utils import read_finance_csv, format_finance_data
from category_keywords import CATEGORY_KEYWORDS

FINANCE_FILE = "finance.csv"

def initialize_finance_csv(filename=FINANCE_FILE):
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Date", "Time", "Description", "Transaction Type", "Amount", "Balance", "Category"])
            writer.writeheader()

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

def clean_description(desc):
    filler_words = [
        "today", "yesterday", "last week", "2 weeks ago",
        "with cash", "cash", "using", "via", "at", "for", "in", "on",
        "a", "an", "the", "just", "only", "my", "me"
    ]
    pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in filler_words) + r')\b', flags=re.IGNORECASE)

    desc = pattern.sub('', desc)

    desc = desc.strip(" ,.-")
    desc = re.sub(r'\\s+', ' ', desc)
    return " ".join(word.capitalize() if word.lower() not in ["and", "or", "the", "of"] else word for word in desc.split())

def auto_categorize(description):
    desc = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in desc for word in keywords):
            return category.capitalize()
    return "Uncategorized"

def add_finance_entry(date, description, txn_type, amount, category, filename=FINANCE_FILE):
    balance = get_latest_balance(filename)
    new_balance = balance + amount if txn_type == "credit" else balance - amount
    time_now = datetime.now().strftime("%H:%M:%S")

    new_row = {
        "Date": date,
        "Time": time_now,
        "Description": description,
        "Transaction Type": txn_type,
        "Amount": amount,
        "Balance": new_balance,
        "Category": category
    }

    try:
        with open(filename, mode='a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=new_row.keys())
            writer.writerow(new_row)
        return new_row
    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return None

def input_finance_entry():
    print("Please enter the following details for your expenditure or income:")

    date = input("Enter the date (YYYY-MM-DD): ")
    description = input("Enter the description of the transaction: ")
    txn_type = input("Enter the transaction type (credit/debit): ").lower()
    amount = float(input("Enter the amount: "))
    category = input("Enter the category (e.g., groceries, entertainment, etc.): ")

    category = auto_categorize(category)  # Automatically categorize if needed

    return date, description, txn_type, amount, category

def main():
    initialize_finance_csv()

    while True:
        print("\nPlease enter a new finance entry.")
        date, description, txn_type, amount, category = input_finance_entry()

        result = add_finance_entry(date, description, txn_type, amount, category)
        if result:
            print(f"✅ Entry added: {description} ({txn_type}) of £{amount:.2f} on {date} in {category}.")
        else:
            print("❌ Failed to add the entry.")

        more_entries = input("\nWould you like to add another entry? (yes/no): ").lower()
        if more_entries != 'yes':
            print("Goodbye! Stay financially sharp.")
            break

if __name__ == "__main__":
    main()
