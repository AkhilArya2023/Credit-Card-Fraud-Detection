import sqlite3
import pandas as pd

def load_data_to_db():
    # Read the Excel file
    excel_file = r"C:\Users\Akhil\Desktop\Froud detechtion\fraud_detection_website\credit_card_fraud_detection_dataset.xlsx"
    df = pd.read_excel(excel_file)

    # Check the first few rows of the dataframe to understand its structure
    print(df.head())

    # Establish database connection
    conn = sqlite3.connect('fraud_detection.db')
    cursor = conn.cursor()

    # Drop the existing transactions table (optional, only do this if you're sure)
    cursor.execute('''DROP TABLE IF EXISTS transactions''')

    # Create users table (if not already exists)
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        name TEXT
    )
    ''')

    # Create transactions table with the correct structure
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        bank_name TEXT,
        transaction_amount REAL,
        transaction_location TEXT,
        transaction_type TEXT,
        frequency INTEGER,
        status TEXT
    )
    ''')

    # Function to detect fraud based on transaction data
    def detect_fraud(transaction_amount, frequency):
        fraud_status = "Safe"  # Default to Safe
        
        # Fraud detection criteria
        if transaction_amount > 10000:
            fraud_status = "Fraud"  # High transaction amount
        elif frequency > 10:
            fraud_status = "Fraud"  # Unusually high frequency
        
        # Additional checks can be added (like transaction location checks)
        
        return fraud_status

    # Add data from the dataset into the transactions table
    for _, row in df.iterrows():
        user_id = row['ID']
        user_name = row['User_Name']
        bank_name = row['Bank_Name']
        transaction_amount = row['Transaction_Amount']
        transaction_location = row['Transaction_Location']
        transaction_type = row['Transaction_Type']
        frequency = row['Frequency']
        
        # Use the fraud detection function to get the status
        status = detect_fraud(transaction_amount, frequency)

        # Insert data into the transactions table
        cursor.execute(''' 
            INSERT INTO transactions 
            (user_id, bank_name, transaction_amount, transaction_location, transaction_type, frequency, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, bank_name, transaction_amount, transaction_location, transaction_type, frequency, status))

    # Commit and close the connection
    conn.commit()
    conn.close()

    print("Data loaded successfully into the database.")

if __name__ == "__main__":
    load_data_to_db()
