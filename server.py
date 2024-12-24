import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import json
import pandas as pd
from urllib.parse import parse_qs

PORT = 8000
BASE_DIR = r"C:\Users\Akhil\Desktop\Froud detechtion\fraud_detection_website"

# Load data from Excel file into the database
def load_data_to_db():
    file_path = os.path.join(BASE_DIR, "credit_card_fraud_detection_dataset.xlsx")

    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} was not found.")
        return
    
    df = pd.read_excel(file_path)

    conn = sqlite3.connect('fraud_detection.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            bank_name TEXT,
            transaction_amount REAL,
            transaction_location TEXT,
            transaction_type TEXT,
            frequency INTEGER,
            status TEXT
        )
    ''')

    for index, row in df.iterrows():
        cursor.execute('''
            INSERT INTO transactions (user_id, bank_name, transaction_amount, transaction_location, transaction_type, frequency, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (row['User_Name'], row['Bank_Name'], row['Transaction_Amount'], row['Transaction_Location'], row['Transaction_Type'], row['Frequency'], 'Safe'))

    conn.commit()
    conn.close()
    print("Dataset loaded successfully.")

# Fraud detection logic based on transaction attributes
def detect_fraud(amount, frequency, location, user_id):
    conn = sqlite3.connect("fraud_detection.db")
    cursor = conn.cursor()

    # Basic fraud detection: if amount > 10000 or frequency > 10
    if amount > 10000 or frequency > 10:
        return "Fraud"

    return "Safe"

class FraudDetectionServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Debugging output to show the requested URL path
        print(f"Received GET request for: {self.path}")

        # Serve appropriate HTML file based on path
        if self.path == "/":
            self.serve_file("index.html")
        elif self.path == "/login.html":
            self.serve_file("login.html")
        elif self.path == "/dashboard.html":
            self.serve_file("dashboard.html")
        elif self.path == "/report.html":
            self.serve_file("report.html")
        elif self.path == "/contact.html":
            self.serve_file("contact.html")  # Fixed indentation here
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        if self.path == "/process_login":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            credentials = parse_qs(post_data.decode("utf-8"))
            username = credentials.get("username", [""])[0]
            password = credentials.get("password", [""])[0]

            # Authenticate user
            if (username == "admin" and password == "admin@123") or (username == "user" and password == "user@123"):
                self.send_response(302)  # Redirect after login
                self.send_header("Location", "/dashboard.html")  # Redirect to dashboard
                self.end_headers()
            else:
                self.send_response(401)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Invalid credentials</h1>")

        elif self.path == "/process_transaction":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            transaction_data = parse_qs(post_data.decode("utf-8"))

            user_id = transaction_data.get("user_id", [""])[0]
            bank_name = transaction_data.get("bank_name", [""])[0]
            amount = float(transaction_data.get("transaction_amount", ["0"])[0])
            location = transaction_data.get("transaction_location", [""])[0]
            transaction_type = transaction_data.get("transaction_type", [""])[0]
            frequency = int(transaction_data.get("frequency", ["0"])[0])

            fraud_status = detect_fraud(amount, frequency, location, user_id)

            conn = sqlite3.connect("fraud_detection.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (user_id, bank_name, transaction_amount, transaction_location, transaction_type, frequency, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, bank_name, amount, location, transaction_type, frequency, fraud_status))
            conn.commit()
            conn.close()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": fraud_status}).encode("utf-8"))

    def serve_file(self, filepath):
        try:
            # Construct the full file path
            full_path = os.path.join(BASE_DIR, filepath)
            print(f"Serving file: {full_path}")  # Debugging output to check file path

            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File {filepath} not found in directory {BASE_DIR}")
            
            # Determine file type based on extension
            if filepath.endswith(".html"):
                content_type = "text/html"
            elif filepath.endswith(".css"):
                content_type = "text/css"
            elif filepath.endswith(".js"):
                content_type = "application/javascript"
            elif filepath.endswith(".png"):
                content_type = "image/png"
            elif filepath.endswith(".jpg") or filepath.endswith(".jpeg"):
                content_type = "image/jpeg"
            else:
                content_type = "application/octet-stream"  # Default for other types

            with open(full_path, "rb") as file:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError as e:
            print(e)  # Debugging output to see the error
       

def run_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, FraudDetectionServer)
    print(f"Server running on port {PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    load_data_to_db()  # Load the data into the database
    run_server()
