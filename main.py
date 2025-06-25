#main.py - User Interface (menus, input/output)
from app import (
    register_user, authenticate_user,
    load_tasks, save_tasks, add_task, view_tasks,
    remove_task, mark_task_done
)

def main():
    print("=== Welcome to the Secure To-Do List App ===")
    username = None

    # --- LOGIN OR REGISTER ---
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            username = input("Enter new username: ").strip()
            password = input("Enter new password: ").strip()
            if register_user(username, password):
                print("Registration successful! Please login.")
            else:
                print("Username already exists. Try another.")
        elif choice == "2":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            if authenticate_user(username, password):
                print(f"Login successful! Welcome, {username}.")
                break
            else:
                print("Invalid credentials. Please try again.")
        elif choice == "3":
            print("Goodbye!")
            return
        else:
            print("Invalid choice. Please try again.")

    #   # --- TASK MENU --- To-Do list operations
    tasks = load_tasks(username)
    while True:
        print("\n===== To-Do Menu =====")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Mark Task as Done")
        print("4. Remove Task")
        print("5. Save and Logout")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            task = input("Enter task: ").strip()
            add_task(tasks, task)
            print("Task added.")
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            view_tasks(tasks)
            try:
                idx = int(input("Enter task number to mark as done: ")) - 1
                mark_task_done(tasks, idx)
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "4":
            view_tasks(tasks)
            try:
                idx = int(input("Enter task number to remove: ")) - 1
                remove_task(tasks, idx)
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "5":
            save_tasks(username, tasks)
            print("Tasks saved. Logging out.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
