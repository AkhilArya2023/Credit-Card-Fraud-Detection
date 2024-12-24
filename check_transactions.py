import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('fraud_detection.db')
cursor = conn.cursor()

# Query to count the number of rows in the transactions table
cursor.execute("SELECT COUNT(*) FROM transactions")
row_count = cursor.fetchone()[0]

print(f"Number of rows in the transactions table: {row_count}")

# Close the connection
conn.close()
