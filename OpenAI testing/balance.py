import csv
import os
from datetime import datetime

# Define the CSV file name and expected header fields
CSV_FILE = "finance.csv"
FIELDNAMES = ["Date", "Description", "Category", "Amount"]

def initialize_csv():
    """Ensure the CSV file exists with the proper header."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()

def add_transaction(date, description, category, amount):
    """Append a new transaction record to the CSV file."""
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow({
            "Date": date,
            "Description": description,
            "Category": category,
            "Amount": amount
        })

def calculate_balance():
    """Calculate the running balance by summing the 'Amount' field from each record."""
    balance = 0.0
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                balance += float(row["Amount"])
            except ValueError:
                print(f"Warning: Skipping invalid amount '{row['Amount']}' in row: {row}")
    return balance

def main():
    # Initialize the CSV file if necessary
    initialize_csv()
    
    # Calculate and display the current balance
    current_balance = calculate_balance()
    print(f"Current balance: ${current_balance:.2f}")
    
    # Ask the user if they want to add a new transaction
    choice = input("Do you want to add a new transaction? (y/n): ").strip().lower()
    if choice == 'y':
        # Get date input; default to today's date if left blank
        date_input = input("Enter the date (YYYY-MM-DD) or leave blank for today: ").strip()
        if not date_input:
            date_input = datetime.today().strftime("%Y-%m-%d")
        
        description = input("Enter the description: ").strip()
        category = input("Enter the category: ").strip()
        
        amount_input = input("Enter the amount (use negative for expenses, positive for income): ").strip()
        try:
            amount = float(amount_input)
        except ValueError:
            print("Invalid amount entered. Transaction aborted.")
            return
        
        # Add the new transaction to the CSV file
        add_transaction(date_input, description, category, amount)
        print("Transaction added successfully!")
        
        # Display the updated balance
        updated_balance = calculate_balance()
        print(f"Updated balance: ${updated_balance:.2f}")
    else:
        print("No transaction added. Exiting.")

if __name__ == "__main__":
    main()
