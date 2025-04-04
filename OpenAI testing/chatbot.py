import os
import re
import csv
from datetime import datetime, timedelta
from openai import OpenAI
from finance_utils import read_finance_csv, format_finance_data
from category_keywords import CATEGORY_KEYWORDS
from dotenv import load_dotenv

load_dotenv()

FINANCE_FILE = "finance.csv"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def initialize_finance_csv(filename=FINANCE_FILE):
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Date", "Description", "Transaction Type", "Amount", "Balance", "Category"])
            writer.writeheader()

def is_exit_command(text):
    return any(keyword in text.lower() for keyword in ["exit", "quit", "bye", "goodbye"])

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

def get_response(user_message):
    print("Received message in chatbot.py:", user_message)
    if is_exit_command(user_message):
        return "Goodbye!"

    # Check if the user is asking about their balance
    if "balance" in user_message.lower():
         balance = get_latest_balance()
         reply = f"Your current balance is: £{balance:.2f}"
         print("Returning reply (balance query):", reply)
         return reply

    # Otherwise, proceed with the normal conversation flow
    conversation_history = [{
        "role": "system",
        "content": "You are Saive, your personal AI financial advisor."
    }, {"role": "user", "content": user_message}]
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            store=True,
            messages=conversation_history
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f"Error communicating with API: {e}"
    
    print("Returning reply:", reply)
    return reply


def auto_categorize(description):
    desc = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in desc for word in keywords):
            return category.capitalize()
    return "Uncategorized"



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


def parse_relative_date(text):
    today = datetime.today()
    if "2 weeks ago" in text:
        return (today - timedelta(weeks=2)).strftime("%Y-%m-%d")
    elif "a week ago" in text or "last week" in text or "1 week ago" in text:
        return (today - timedelta(weeks=1)).strftime("%Y-%m-%d")
    elif "yesterday" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    elif "today" in text:
        return today.strftime("%Y-%m-%d")
    else:
        return today.strftime("%Y-%m-%d")

def extract_natural_entry(user_input):
    # Normalize the input text and determine the date
    text = user_input.lower()
    date = parse_relative_date(text)
    
    # Determine the transaction type based on keywords
    if "cash" in text:
        transaction_type = "cash"
    elif any(word in text for word in ["spent", "paid", "bought", "used", "purchased"]):
        transaction_type = "debit"
    elif any(word in text for word in ["received", "got", "earned", "gift", "given", "found"]):
        transaction_type = "credit"
    else:
        transaction_type = "credit"
    
    # Set defaults for description and amount
    description = "Uncategorized"
    amount = None

    # Define regex patterns along with extraction logic in order of priority.
    patterns = [
        # Gift pattern: e.g., "Alice sent me 50"
        (r"(\b\w+\b)\s+(?:sent|gave|offered|provided|gifted)\s+me\s+(\d+(?:\.\d+)?)",
         lambda m: (f"Gift from {m.group(1).capitalize()}", float(m.group(2)))),
        # Family or friend gift pattern: e.g., "my mum gave me 30"
        (r"(?:my|from)?\s*(grandma|mum|mom|dad|friend|sister|brother|uncle|aunt).*?(?:gave|sent)\s+me\s+(\d+(?:\.\d+)?)",
         lambda m: (f"Gift from {m.group(1).capitalize()}", float(m.group(2)))),
        # Purchase or expense pattern: e.g., "spent lunch for 10" or "bought coffee at 5"
        (r"(?:bought|spent|paid) (.+?) (?:for|at|with) (\d+(?:\.\d+)?)",
         lambda m: (clean_description(m.group(1)), float(m.group(2)))),
        # Received pattern: e.g., "received 100 from employer"
        (r"received (\d+(?:\.\d+)?) from (.+)",
         lambda m: (clean_description(m.group(2)), float(m.group(1)))),
        # Salary pattern: e.g., "got paid 2000"
        (r"got paid (\d+(?:\.\d+)?)",
         lambda m: ("Salary", float(m.group(1)))),
        # Boss raise pattern: e.g., "my boss gave me 150"
        (r"my boss .*?(?:gave|offered|granted) me .*?(\d+(?:\.\d+)?)",
         lambda m: ("Raise from Boss", float(m.group(1)))),
        # Used pattern: e.g., "used 20 for taxi"
        (r"used (\d+(?:\.\d+)?) .*? for (.+)",
         lambda m: (clean_description(m.group(2)), float(m.group(1)))),
    ]

    # Try each pattern and use the first successful match.
    for pattern, extractor in patterns:
        match = re.search(pattern, text)
        if match:
            description, amount = extractor(match)
            break

    # Fallback: if no pattern matched, look for any number if a finance-related keyword is present.
    if amount is None:
        finance_keywords = ["spent", "paid", "bought", "received", "salary", "gift", "used"]
        if any(word in text for word in finance_keywords):
            numbers = [float(n) for n in re.findall(r"\b\d+(?:\.\d+)?\b", text) if float(n) > 1]
            if numbers:
                amount = max(numbers)
        else:
            return None

    if amount:
        description = clean_description(description)
        category = auto_categorize(description)
        return date, description, transaction_type, amount, category

    return None


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

def handle_summary_query(user_input):
    import pandas as pd

    if not os.path.exists(FINANCE_FILE):
        return "No finance data found."

    df = pd.read_csv(FINANCE_FILE)

    # Try to extract time range
    match = re.search(r"between (\d{1,2}:\d{2}) ?(am|pm)? to (\d{1,2}:\d{2}) ?(am|pm)?", user_input, re.IGNORECASE)
    if match:
        t1 = match.group(1)
        ampm1 = match.group(2) or ""
        t2 = match.group(3)
        ampm2 = match.group(4) or ""
        
        # Convert to 24-hour time strings
        fmt = "%I:%M %p" if ampm1 or ampm2 else "%H:%M"
        try:
            t1_24 = datetime.strptime(f"{t1} {ampm1}".strip(), fmt).time()
            t2_24 = datetime.strptime(f"{t2} {ampm2}".strip(), fmt).time()
        except:
            return "Sorry, I couldn't understand the time format."

        today = datetime.today().strftime("%Y-%m-%d")
        df_today = df[df["Date"] == today]

        # Filter by time range
        df_today["Time"] = pd.to_datetime(df_today["Time"]).dt.time
        df_filtered = df_today[(df_today["Time"] >= t1_24) & (df_today["Time"] <= t2_24)]

        # Get credits only
        received = df_filtered[df_filtered["Transaction Type"] == "credit"]
        total_received = received["Amount"].astype(float).sum()

        return f"📥 You received £{total_received:.2f} between {t1} {ampm1} and {t2} {ampm2} today."

    return None


def chat_with_saive():
    conversation_history = []
    initialize_finance_csv()
    finance_data = read_finance_csv()
    finance_output = format_finance_data(finance_data)

    conversation_history.append({
        "role": "system",
        "content": f"You are Saive, Your personal AI financial advisor. Use the following finance data as reference:\n{finance_output}"
    })

    print("Welcome to Saive 🧠💰 — your personal finance assistant!")
    print("Type something like 'I spent 10 on lunch today' or 'Got paid 500 yesterday'.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if is_exit_command(user_input):
            print("Saive: Goodbye! Stay financially sharp. 🤑")
            break
        
        new_entry = extract_natural_entry(user_input)
        if new_entry and all(new_entry):
            date, desc, txn_type, amt, category = new_entry
            result = add_finance_entry(date, desc, txn_type, amt, category)
            if result:
                print(f"✅ Entry added: {desc} ({txn_type}) of {amt} on {date} in {category}")
                finance_data = read_finance_csv()
                finance_output = format_finance_data(finance_data)
                conversation_history[0]["content"] = (
                    f"You are Saive, your personal AI financial advisor. "
                    f"Use the following finance data as reference:\n{finance_output}"
                )
            else:
                print("❌ Failed to add the entry.")
            continue

        conversation_history.append({"role": "user", "content": user_input})
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            store=True,
            messages=conversation_history
        )
        reply = completion.choices[0].message.content
        print("Saive:", reply)
        conversation_history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    chat_with_saive()
