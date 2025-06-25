# To-Do List Application

A simple, secure, terminal-based to-do list application built with Python.  
Features user registration, email-based verification, login, and basic task management (add, view, mark as done, remove).  
Verification codes are sent to the user's email using Gmail SMTP.

---

## Features

- **User Registration & Login**  
  Sign up with your email and password. Login is only possible after email verification.

- **Email Verification**  
  Upon registration, a verification code is sent to your email. Enter the code to activate your account.

- **Task Management**  
  - Add new tasks  
  - View all tasks  
  - Mark tasks as done  
  - Remove tasks  
  - Tasks are saved per user

---

## Requirements

- Python 3.7+
- Gmail account with [App Password](https://support.google.com/accounts/answer/185833?hl=en) for email sending

Install dependencies:

## pip install -r requirements.txt

requirements.txt

---
## How It Works

- **Register:**  
Enter your email and password.  
A verification code is sent to your email.

- **Verify:**  
Enter the code from your inbox to complete registration.

- **Login:**  
Use your email and password to access your personal to-do list.

- **Manage Tasks:**  
Add, view, mark as done, and remove your tasks directly from the terminal.

---

## Notes

- All user data and tasks are stored in the `database/` folder as CSV and text files.
- The app uses only your terminal—no web interface required.
- For security, never share your Gmail app password.

---

**Built with Python and ❤️ for learning and productivity.**
