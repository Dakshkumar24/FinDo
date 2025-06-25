## All the main logic (functions for users and tasks)
import csv
import hashlib
import os

USERS_FILE = "users.csv"  # File to store all usernames and password hashes

# --- USER MANAGEMENT ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    # # Registers a new user if username is not taken
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == username:
                    return False  # Username taken
    #Save new user and password hash
    with open(USERS_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([username, hash_password(password)])
    return True

def authenticate_user(username, password):
    # Checks if username and password match what's stored
    if not os.path.exists(USERS_FILE):
        return False
    with open(USERS_FILE, "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] == username and row[1] == hash_password(password):
                return True
    return False

# --- TASK MANAGEMENT ---

def get_tasks_filename(username):
    # Each user gets their own file for tasks
    return f"{username}_tasks.txt"

def load_tasks(username):
    # Loads all tasks for this user
    filename = get_tasks_filename(username)
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return [line.strip() for line in f.readlines()]

def save_tasks(username, tasks):
    # Saves all tasks for this user
    filename = get_tasks_filename(username)
    with open(filename, "w") as f:
        for task in tasks:
            f.write(task + "\n")

def add_task(tasks, task):
    # Adds a new task to the list
    tasks.append(task)

def view_tasks(tasks):
    # Shows all tasks with numbers
    if not tasks:
        print("No tasks yet.")
    else:
        for i, task in enumerate(tasks, start=1):
            print(f"{i}. {task}")

def remove_task(tasks, index):
    # Removes a task by its numbers
    if 0 <= index < len(tasks):
        removed = tasks.pop(index)
        print(f"Removed: {removed}")
    else:
        print("Invalid task number.")

def mark_task_done(tasks, index):
    # Marks a task as done (removes it)
    if 0 <= index < len(tasks):
        done_task = tasks.pop(index)
        print(f"Task '{done_task}' marked as done and removed.")
    else:
        print("Invalid task number.")
