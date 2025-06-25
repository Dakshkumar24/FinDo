import csv
import hashlib
import os
import random
import smtplib
from email.message import EmailMessage
from email_validator import validate_email, EmailNotValidError

DATABASE_FOLDER = "database"
USERS_FILE = os.path.join(DATABASE_FOLDER, "users.csv")

# --- Ensure database folder exists ---
if not os.path.exists(DATABASE_FOLDER):
    os.makedirs(DATABASE_FOLDER)

# --- Email sending setup ---
SENDER_EMAIL = "dakshkumar19860@gmail.com"      # <-- Replace with your Gmail address
SENDER_PASSWORD = "jpud hbik syny jsnn"      # <-- Replace with your Gmail App Password
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
    if password:
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

def validate_email_address(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

# --- TASK MANAGEMENT ---

def get_tasks_filename(email):
    return os.path.join(DATABASE_FOLDER, f"{email}_tasks.txt")

def load_tasks(email):
    filename = get_tasks_filename(email)
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return [line.strip() for line in f.readlines()]

def save_tasks(email, tasks):
    filename = get_tasks_filename(email)
    with open(filename, "w") as f:
        for task in tasks:
            f.write(task + "\n")

def add_task(tasks, task):
    tasks.append(task)

def view_tasks(tasks):
    if not tasks:
        print("No tasks yet.")
    else:
        for i, task in enumerate(tasks, start=1):
            print(f"{i}. {task}")

def remove_task(tasks, index):
    if 0 <= index < len(tasks):
        removed = tasks.pop(index)
        print(f"Removed: {removed}")
    else:
        print("Invalid task number.")

def mark_task_done(tasks, index):
    if 0 <= index < len(tasks):
        done_task = tasks.pop(index)
        print(f"Task '{done_task}' marked as done and removed.")
    else:
        print("Invalid task number.")
