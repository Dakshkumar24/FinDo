from app import(
    register_user, authenticate_user, is_user_verified,
    set_verification_code, verify_user, send_email_verification_code,
    load_tasks, save_tasks, validate_email_address,
    edit_tasks_in_notepad
)

import pwinput


def get_password(prompt="Enter password: "):
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
        print("1. Edit Tasks in Notepad++")
        print("2. Save and Logout")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            print("Your to-do list will open in Notepad++. Edit, add, or remove tasks as you wish.")
            print("Tip: You can add clickable links by pasting the full URL (e.g., https://example.com)")
            print("Save your changes and close Notepad++ when done.")
            tasks = edit_tasks_in_notepad(email)
            print("Tasks updated.")
        elif choice == "2":
            save_tasks(email, tasks)
            print("Tasks saved. Logging out.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

