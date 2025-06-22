import csv
import os
from werkzeug.security import generate_password_hash, check_password_hash

USERS_CSV = 'users.csv'
TASKS_CSV = 'tasks.csv'

# Ensure CSV files exist with headers
if not os.path.exists(USERS_CSV):
    with open(USERS_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'password'])

if not os.path.exists(TASKS_CSV):
    with open(TASKS_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'task', 'completed'])

def user_exists(username):
    with open(USERS_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] == username:
                return True
    return False

def add_user(username, password):
    hashed = generate_password_hash(password)
    with open(USERS_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([username, hashed])

def verify_user(username, password):
    with open(USERS_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] == username and check_password_hash(row['password'], password):
                return True
    return False

def get_tasks(username):
    tasks = []
    with open(TASKS_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] == username:
                tasks.append({'task': row['task'], 'completed': row['completed'] == 'True'})
    return tasks

def add_task(username, task):
    with open(TASKS_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([username, task, False])

def update_tasks(username, tasks):
    all_tasks = []
    with open(TASKS_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] == username:
                continue
            all_tasks.append(row)
    for t in tasks:
        all_tasks.append({'username': username, 'task': t['task'], 'completed': str(t['completed'])})
    with open(TASKS_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['username', 'task', 'completed'])
        writer.writeheader()
        for row in all_tasks:
            writer.writerow(row)

def signup():
    print("=== Sign Up ===")
    username = input("Username: ")
    if user_exists(username):
        print("Username already exists.")
        return None
    password = input("Password: ")
    add_user(username, password)
    print("Signup successful! Please log in.")
    return None

def login():
    print("=== Login ===")
    username = input("Username: ")
    password = input("Password: ")
    if verify_user(username, password):
        print(f"Welcome, {username}!")
        return username
    print("Invalid username or password.")
    return None

def list_tasks(username):
    tasks = get_tasks(username)
    if not tasks:
        print("No tasks found.")
        return
    print("\nYour tasks:")
    for i, t in enumerate(tasks):
        status = "[x]" if t['completed'] else "[ ]"
        print(f"{i+1}. {status} {t['task']}")

def add_new_task(username):
    task = input("Enter new task: ")
    if task.strip():
        add_task(username, task)
        print("Task added.")
    else:
        print("Task cannot be empty.")

def toggle_task(username):
    tasks = get_tasks(username)
    list_tasks(username)
    idx = int(input("Enter task number to toggle: ")) - 1
    if 0 <= idx < len(tasks):
        tasks[idx]['completed'] = not tasks[idx]['completed']
        update_tasks(username, tasks)
        print("Task status updated.")
    else:
        print("Invalid task number.")

def delete_task(username):
    tasks = get_tasks(username)
    list_tasks(username)
    idx = int(input("Enter task number to delete: ")) - 1
    if 0 <= idx < len(tasks):
        tasks.pop(idx)
        update_tasks(username, tasks)
        print("Task deleted.")
    else:
        print("Invalid task number.")

def main_menu(username):
    while True:
        print("\n=== To-Do List Menu ===")
        print("1. List tasks")
        print("2. Add task")
        print("3. Toggle task completion")
        print("4. Delete task")
        print("5. Logout")
        choice = input("Choose an option: ")
        if choice == "1":
            list_tasks(username)
        elif choice == "2":
            add_new_task(username)
        elif choice == "3":
            toggle_task(username)
        elif choice == "4":
            delete_task(username)
        elif choice == "5":
            print("Logged out.")
            break
        else:
            print("Invalid choice.")

def main():
    print("=== Welcome to Terminal To-Do App ===")
    while True:
        print("\n1. Login\n2. Sign Up\n3. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            user = login()
            if user:
                main_menu(user)
        elif choice == "2":
            signup()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
