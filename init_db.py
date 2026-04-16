import sqlite3
import os
from config import DATABASE

db_folder = os.path.dirname(DATABASE)
os.makedirs(db_folder, exist_ok=True)

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    password TEXT NOT NULL,
    user_id TEXT NOT NULL UNIQUE,
    otp TEXT,
    otp_verified INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS aadhaar_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    aadhaar_number TEXT NOT NULL,
    original_filename TEXT,
    encrypted_filename TEXT,
    sha256_hash TEXT,
    blockchain_txn_hash TEXT,
    uidai_verified INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bank_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bank_name TEXT,
    target_user_id TEXT,
    status TEXT DEFAULT 'Pending',
    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preview_used INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS mock_uidai (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aadhaar_number TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL
)
""")

mock_records = [
    ("123412341234", "Ayaan Khan", "9876543210"),
    ("555566667777", "Sara Ali", "9123456780"),
    ("111122223333", "Rahul Mehta", "9988776655")
]

for record in mock_records:
    try:
        cursor.execute("""
        INSERT INTO mock_uidai (aadhaar_number, full_name, phone)
        VALUES (?, ?, ?)
        """, record)
    except sqlite3.IntegrityError:
        pass

conn.commit()
conn.close()

print("Database and tables created successfully.")
print("Database path:", DATABASE)