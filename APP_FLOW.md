# FinDo Application Flow Documentation

## Overview
FinDo is a Flask-based web application that provides task management and expense tracking functionality. It includes user authentication, task management, expense tracking, and password recovery features.

## Project Structure

### Main Files
- `flask_app.py`: Main application file containing all routes and business logic
- `requirements.txt`: Lists all Python dependencies
- `APP_FLOW.md`: This documentation file

### Directories
- `database/`: Contains JSON files for data storage
  - `users.json`: Stores user account information
  - `todos.json`: Stores active todos
  - `deleted_todos.json`: Stores deleted todos (kept for 15 days)
  - `expenses.json`: Stores expense records

- `templates/`: Contains HTML templates
  - `base.html`: Base template with common layout
  - `login.html`: User login page
  - `register.html`: User registration page
  - `welcome.html`: Dashboard/landing page after login
  - `tasks.html`: Task management interface
  - `expenses.html`: Expense tracking interface
  - `forgot_password.html`: Password recovery page
  - `reset_password.html`: Password reset page
  - `about_contact.html`: Contact information page

- `static/`: Contains static files (CSS, JS, images)

## Application Flow

### 1. Authentication Flow

#### Registration
1. User visits `/register`
2. Submits email and password
3. System validates input and creates new user
4. User is redirected to login page

#### Login
1. User visits `/login`
2. Submits credentials
3. System authenticates and creates session
4. User is redirected to `/welcome` dashboard

#### Password Recovery
1. User clicks "Forgot Password"
2. Enters email on `/forgot-password`
3. System sends password reset email with token
4. User clicks reset link
5. Submits new password on `/reset-password/<token>`
6. Password is updated

### 2. Core Features

#### Task Management
- **Add Task**: POST to `/add_todo`
- **View Tasks**: GET `/tasks`
- **Update Task**: PUT `/update_todo/<id>`
- **Delete Task**: DELETE `/delete_todo/<id>` (moves to deleted_todos.json)
- **Restore Task**: POST `/restore_todo/<id>`
- **Permanent Delete**: DELETE `/delete_permanently/<id>`
- **Toggle Complete**: POST `/toggle_todo/<id>`

#### Expense Tracking
- **Add Expense**: POST `/add_expense`
- **View Expenses**: GET `/get_expenses`
- **Delete Expense**: DELETE `/delete_expense/<id>`

### 3. Data Storage
- All data is stored in JSON files in the `database/` directory
- User passwords are hashed using Werkzeug's security functions
- Deleted todos are kept for 15 days before permanent removal

## Security Features
- Password hashing with salt
- CSRF protection
- Session management
- Secure password reset tokens
- Input validation
- Environment variables for sensitive data

## Dependencies
- Flask: Web framework
- Flask-Login: User session management
- python-dotenv: Environment variable management
- email-validator: Email validation
- Werkzeug: Security utilities

## Running the Application
1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env` file
3. Run: `python flask_app.py`
4. Access at: `http://localhost:8000`

## Maintenance
- Run `cleanup_old_deleted_todos()` periodically to remove old deleted todos
- Back up JSON files regularly
- Monitor logs for errors
