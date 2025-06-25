import csv
import hashlib
import os
import random
import smtplib
import subprocess
import re
from email.message import EmailMessage
from email_validator import validate_email, EmailNotValidError

# --- Folder and file structure setup ---
DATABASE_FOLDER = "database"
USERS_FOLDER = os.path.join(DATABASE_FOLDER, "users")
USERS_FILE = os.path.join(USERS_FOLDER, "users.csv")
TASKS_FOLDER = os.path.join(DATABASE_FOLDER, "tasks")

# Ensure folders exist
for folder in [DATABASE_FOLDER, USERS_FOLDER, TASKS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- Email sending setup ---
SENDER_EMAIL = "dakshkumar19860@gmail.com"      # <-- Replace with your Gmail address
SENDER_PASSWORD = "jpud hbik syny jsnn"         # <-- Replace with your Gmail App Password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email_verification_code(recipient_email, code):
    msg = EmailMessage()
    msg['Subject'] = 'Your Verification Code'
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg.set_content(f"Your verification code is: {code}")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Verification code sent to {recipient_email}.")
    except Exception as e:
        print(f"Could not send email: {e}")
        print(f"Your verification code is: {code} (shown for testing)")

# --- USER MANAGEMENT ---

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def user_exists(email):
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == email:
                    return True
    return False

def register_user(email, password):
    if user_exists(email):
        return False
    return True

def save_verified_user(email, password):
    with open(USERS_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([email, hash_password(password), "True"])

def authenticate_user(email, password):
    if not os.path.exists(USERS_FILE):
        return False
    with open(USERS_FILE, "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] == email and row[1] == hash_password(password):
                return True
    return False

def is_user_verified(email):
    if not os.path.exists(USERS_FILE):
        return False
    with open(USERS_FILE, "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] == email:
                return row[2] == "True"
    return False

VERIFICATION_CODES = {}
TEMP_PASSWORDS = {}

def generate_verification_code():
    return str(random.randint(100000, 999999))

def set_verification_code(email, password=None):
    code = generate_verification_code()
    VERIFICATION_CODES[email] = code
    if password is not None:  # Only store password if it's provided (not None)
        TEMP_PASSWORDS[email] = password
    return code

def verify_user(email, code):
    if VERIFICATION_CODES.get(email) == code:
        if not user_exists(email):
            password = TEMP_PASSWORDS.get(email, "")
            save_verified_user(email, password)
            TEMP_PASSWORDS.pop(email, None)
        VERIFICATION_CODES.pop(email)
        return True
    return False

def reset_password(email, new_password):
    """Update the password for an existing user"""
    if not user_exists(email):
        return False
        
    # Read all users
    users = []
    with open(USERS_FILE, "r", newline="") as file:
        reader = csv.reader(file)
        users = list(reader)
    
    # Update the password for the matching user
    updated = False
    for user in users:
        if user and user[0] == email:
            user[1] = hash_password(new_password)
            updated = True
            break
    
    # Write the updated users back to the file
    if updated:
        with open(USERS_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(users)
    
    return updated

def initiate_password_reset(email):
    """Initiate password reset by sending verification code to email"""
    if not user_exists(email):
        return False
    code = set_verification_code(email)
    send_email_verification_code(email, code)
    return True

def validate_email_address(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

# --- TASK MANAGEMENT WITH NOTEPAD INTEGRATION ---

def get_tasks_filename(email):
    # Only replace / and \ (which are not allowed in filenames)
    safe_email = re.sub(r"[\\/]", "_", email)
    return os.path.join(TASKS_FOLDER, f"{safe_email}.csv")

def load_tasks(email):
    filename = get_tasks_filename(email)
    tasks = []
    if os.path.exists(filename):
        with open(filename, "r", newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:  # skip empty rows
                    tasks.append(row[0])
    return tasks

def save_tasks(email, tasks):
    filename = get_tasks_filename(email)
    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for task in tasks:
            writer.writerow([task])

def edit_tasks_in_notepad(email):
    """
    Opens the user's tasks file in Notepad++ for direct editing.
    Returns the updated list of tasks (one per line, stripped).
    """
    # Use .txt extension for better link handling in Notepad++
    txt_filename = get_tasks_filename(email).replace('.csv', '.txt')
    csv_filename = get_tasks_filename(email)
    
    # If CSV exists, convert it to a simple text file for Notepad++
    if os.path.exists(csv_filename):
        with open(csv_filename, 'r', encoding='utf-8') as f:
            tasks = [row[0].strip() for row in csv.reader(f) if row]
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(tasks))
    else:
        with open(txt_filename, 'w', encoding='utf-8') as f:
            pass  # create empty file

    # Open in Notepad++ if available, fallback to default text editor
    try:
        subprocess.run(['C:\\Program Files\\Notepad++\\notepad++.exe', '-multiInst', txt_filename])
    except Exception as e:
        print(f"Could not open Notepad++: {e}. Using default text editor instead.")
        subprocess.run(['notepad.exe', txt_filename])

    # After editing, read tasks from the text file
    tasks = []
    if os.path.exists(txt_filename):
        with open(txt_filename, 'r', encoding='utf-8') as f:
            tasks = [line.strip() for line in f if line.strip()]
    
    # Save back to CSV format
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for task in tasks:
            writer.writerow([task])
    
    # Remove the temporary text file
    try:
        os.remove(txt_filename)
    except Exception as e:
        print(f"Warning: Could not remove temporary file: {e}")
    
    return tasks



