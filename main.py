# from app import (
#     register_user, authenticate_user, is_user_verified,
#     set_verification_code, verify_user, send_email_verification_code,
#     load_tasks, save_tasks, add_task, view_tasks,
#     remove_task, mark_task_done, validate_email_address
# )
# import pwinput
#
# def get_password(prompt="Enter password: "):
#     """
#     Prompts the user if they want to show or hide their password while typing,
#     then returns the entered password accordingly.
#     """
#     while True:
#         show = input("Show password while typing? (y/n): ").strip().lower()
#         if show == 'y':
#             password = input(prompt).strip()
#             return password
#         elif show == 'n':
#             password = pwinput.pwinput(prompt, mask='*').strip()
#             return password
#         else:
#             print("Please enter 'y' or 'n'.")
#
# def main():
#     print("=== Welcome to the Secure To-Do List App ===")
#     email = None
#
#     while True:
#         print("\n1. Register\n2. Login\n3. Exit")
#         choice = input("Choose an option: ").strip()
#         if choice == "1":
#             email = input("Enter your email: ").strip()
#             if not validate_email_address(email):
#                 print("Invalid email format. Please try again.")
#                 continue
#             password = get_password("Enter new password: ")
#             if register_user(email, password):
#                 print("A verification code has been sent to your email.")
#                 code = set_verification_code(email, password)
#                 send_email_verification_code(email, code)
#                 user_code = input("Enter the verification code: ").strip()
#                 if verify_user(email, user_code):
#                     print("Registration and verification successful! Please login.")
#                 else:
#                     print("Incorrect code. Registration failed.")
#                     continue
#             else:
#                 print("User already exists. Try another email.")
#         elif choice == "2":
#             email = input("Enter your email: ").strip()
#             password = get_password("Enter your password: ")
#             if authenticate_user(email, password):
#                 if not is_user_verified(email):
#                     print("You need to verify your account.")
#                     code = set_verification_code(email)
#                     send_email_verification_code(email, code)
#                     user_code = input("Enter the verification code: ").strip()
#                     if verify_user(email, user_code):
#                         print("Verification successful! Welcome.")
#                         break
#                     else:
#                         print("Incorrect code. Please try logging in again.")
#                         continue
#                 else:
#                     print("Login successful! Welcome.")
#                     break
#             else:
#                 print("Invalid credentials. Please try again.")
#         elif choice == "3":
#             print("Goodbye!")
#             return
#         else:
#             print("Invalid choice. Please try again.")
#
#     # --- TASK MENU ---
#     tasks = load_tasks(email)
#     while True:
#         print("\n===== To-Do Menu =====")
#         print("1. Add Task")
#         print("2. View Tasks")
#         print("3. Mark Task as Done")
#         print("4. Remove Task")
#         print("5. Save and Logout")
#         choice = input("Choose an option: ").strip()
#         if choice == "1":
#             task = input("Enter task: ").strip()
#             add_task(tasks, task)
#             print("Task added.")
#         elif choice == "2":
#             view_tasks(tasks)
#         elif choice == "3":
#             view_tasks(tasks)
#             try:
#                 idx = int(input("Enter task number to mark as done: ")) - 1
#                 mark_task_done(tasks, idx)
#             except ValueError:
#                 print("Please enter a valid number.")
#         elif choice == "4":
#             view_tasks(tasks)
#             try:
#                 idx = int(input("Enter task number to remove: ")) - 1
#                 remove_task(tasks, idx)
#             except ValueError:
#                 print("Please enter a valid number.")
#         elif choice == "5":
#             save_tasks(email, tasks)
#             print("Tasks saved. Logging out.")
#             break
#         else:
#             print("Invalid choice. Please try again.")
#
# if __name__ == "__main__":
#     main()



from app import (
    register_user, authenticate_user, is_user_verified,
    set_verification_code, verify_user, send_email_verification_code,
    load_tasks, save_tasks, add_task, view_tasks,
    remove_task, mark_task_done, validate_email_address,
    open_notepad_and_get_content  # Make sure this is in app.py!
)
import pwinput

def get_password(prompt="Enter password: "):
    """
    Prompts the user if they want to show or hide their password while typing,
    then returns the entered password accordingly.
    """
    while True:
        show = input("Show password while typing? (y/n): ").strip().lower()
        if show == 'y':
            password = input(prompt).strip()
            return password
        elif show == 'n':
            password = pwinput.pwinput(prompt, mask='*').strip()
            return password
        else:
            print("Please enter 'y' or 'n'.")

def main():
    print("=== Welcome to the Secure To-Do List App ===")
    email = None

    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            email = input("Enter your email: ").strip()
            if not validate_email_address(email):
                print("Invalid email format. Please try again.")
                continue
            password = get_password("Enter new password: ")
            if register_user(email, password):
                print("A verification code has been sent to your email.")
                code = set_verification_code(email, password)
                send_email_verification_code(email, code)
                user_code = input("Enter the verification code: ").strip()
                if verify_user(email, user_code):
                    print("Registration and verification successful! Please login.")
                else:
                    print("Incorrect code. Registration failed.")
                    continue
            else:
                print("User already exists. Try another email.")
        elif choice == "2":
            email = input("Enter your email: ").strip()
            password = get_password("Enter your password: ")
            if authenticate_user(email, password):
                if not is_user_verified(email):
                    print("You need to verify your account.")
                    code = set_verification_code(email)
                    send_email_verification_code(email, code)
                    user_code = input("Enter the verification code: ").strip()
                    if verify_user(email, user_code):
                        print("Verification successful! Welcome.")
                        break
                    else:
                        print("Incorrect code. Please try logging in again.")
                        continue
                else:
                    print("Login successful! Welcome.")
                    break
            else:
                print("Invalid credentials. Please try again.")
        elif choice == "3":
            print("Goodbye!")
            return
        else:
            print("Invalid choice. Please try again.")

    # --- TASK MENU ---
    tasks = load_tasks(email)
    while True:
        print("\n===== To-Do Menu =====")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Mark Task as Done")
        print("4. Remove Task")
        print("5. Save and Logout")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            print("A Notepad window will open. Type your task, save, and close Notepad.")
            task = open_notepad_and_get_content()
            if task:
                add_task(tasks, task)
                print("Task added.")
            else:
                print("No task entered.")
        elif choice == "2":
            if not tasks:
                print("No tasks yet.")
            else:
                print("Your tasks will open in Notepad.")
                tasks_text = "\n".join(f"{i+1}. {task}" for i, task in enumerate(tasks))
                open_notepad_and_get_content(tasks_text)
        elif choice == "3":
            if not tasks:
                print("No tasks yet.")
            else:
                print("Your tasks will open in Notepad.")
                tasks_text = "\n".join(f"{i+1}. {task}" for i, task in enumerate(tasks))
                open_notepad_and_get_content(tasks_text)
                try:
                    idx = int(input("Enter task number to mark as done: ")) - 1
                    mark_task_done(tasks, idx)
                except ValueError:
                    print("Please enter a valid number.")
        elif choice == "4":
            if not tasks:
                print("No tasks yet.")
            else:
                print("Your tasks will open in Notepad.")
                tasks_text = "\n".join(f"{i+1}. {task}" for i, task in enumerate(tasks))
                open_notepad_and_get_content(tasks_text)
                try:
                    idx = int(input("Enter task number to remove: ")) - 1
                    remove_task(tasks, idx)
                except ValueError:
                    print("Please enter a valid number.")
        elif choice == "5":
            save_tasks(email, tasks)
            print("Tasks saved. Logging out.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
