from app import(
    register_user, authenticate_user, is_user_verified, user_exists,
    set_verification_code, verify_user, send_email_verification_code,
    load_tasks, save_tasks, validate_email_address,
    edit_tasks_in_notepad, reset_password, initiate_password_reset, VERIFICATION_CODES
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

def handle_password_reset():
    email = input("Enter your registered email: ").strip()
    if not validate_email_address(email):
        print("Invalid email format. Please try again.")
        return
        
    if not user_exists(email):
        print("No account found with that email address.")
        return
        
    print("Sending verification code to your email...")
    if not initiate_password_reset(email):
        print("Failed to initiate password reset. Please try again later.")
        return
        
    print("A verification code has been sent to your email.")
    user_code = input("Enter the verification code: ").strip()
    
    if VERIFICATION_CODES.get(email) == user_code:
        new_password = get_password("Enter your new password: ")
        confirm_password = get_password("Confirm your new password: ")
        
        if new_password != confirm_password:
            print("Passwords do not match. Please try again.")
            return
            
        if reset_password(email, new_password):
            VERIFICATION_CODES.pop(email, None)  # Clear the used code
            print("Password has been reset successfully! You can now login with your new password.")
        else:
            print("Failed to reset password. Please try again.")
    else:
        print("Invalid verification code. Please try again.")

def main():
    print("=== Welcome to the Secure To-Do List App ===")
    email = None

    while True:
        print("\n1. Register\n2. Login\n3. Forgot Password\n4. Exit")
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
            handle_password_reset()
        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Invalid choice. Please try again.")

    # --- TASK MENU ---
    tasks = load_tasks(email)
    while True:
        print("\n===== To-Do List Menu =====")
        print("1. Open and Edit Tasks in Notepad++")
        print("2. Save and Logout")
        choice = input("Choose an option (1-2): ").strip()
        
        if choice == "1":
            print("\nOpening Notepad++ with your tasks...")
            print("• Add, edit, or delete tasks")
            print("• One task per line")
            print("• Just save and close Notepad++ when you're done")
            tasks = edit_tasks_in_notepad(email)
            print("\nTasks have been saved successfully!")
            
        elif choice == "2":
            save_tasks(email, tasks)
            print("\nTasks saved. Logging out.")
            break
            
        else:
            print("\nInvalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
