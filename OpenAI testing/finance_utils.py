import csv

def read_finance_csv(filename="finance.csv"):
    try:
        with open(filename, mode='r', newline='') as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []

def format_finance_data(data):
    lines = ["Date | Time | Description | Type | Amount | Balance | Category"]
    for row in data:
        line = f"{row['Date']} | {row.get('Time', '00:00:00')} | {row['Description']} | {row['Transaction Type']} | {row['Amount']} | {row['Balance']} | {row.get('Category', 'Uncategorized')}"
        lines.append(line)
    return "\n".join(lines)
