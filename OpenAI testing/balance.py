import csv
import datetime

def load_keywords():
    return {
        "Food": ["grocery", "restaurant", "coffee", "snack"],
        "Entertainment": ["movie", "concert", "game", "netflix", "spotify"],
        "Transport": ["train", "bus", "uber", "taxi", "fuel"],
        "Housing": ["rent", "mortgage", "electric", "water", "bill"],
        "Health": ["medicine", "doctor", "hospital"],
        "Gift": ["gift", "present"],
        "Misc": ["uncategorized", "misc"],
    }

def categorize_transaction(description, keywords):
    desc_lower = description.lower()
    for category, words in keywords.items():
        if any(word in desc_lower for word in words):
            return category
    return "Misc"

def add_expenditure():
    transactions = []
    keywords = load_keywords()
    print("Enter your expenditures. Type 'DONE' to confirm and save, or 'REMOVE' to delete the last entry.")

    while True:
        description = input("Enter transaction description: ")
        if description.lower() == "done":
            break
        elif description.lower() == "remove":
            if transactions:
                removed = transactions.pop()
                print(f"Removed: {removed}")
            else:
                print("No transactions to remove.")
            continue
        
        transaction_type = input("Enter transaction type (debit/credit/cash): ").lower()
        amount = float(input("Enter amount: "))
        balance = transactions[-1][5] - amount if transaction_type == "debit" else transactions[-1][5] + amount if transactions else amount
        category = categorize_transaction(description, keywords)
        confirm_category = input(f"Suggested category: {category}. Accept? (yes/no): ")
        if confirm_category.lower() == "no":
            category = input("Enter custom category: ")
        
        transaction = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description, transaction_type, amount, balance, category]
        transactions.append(transaction)
        print(f"Added: {transaction}")

    save_transactions(transactions)

def save_transactions(transactions):
    filename = "transactions.csv"
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        for transaction in transactions:
            writer.writerow(transaction)
    print(f"Transactions saved to {filename}")

if __name__ == "__main__":
    add_expenditure()
