from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from flask_mail import Mail, Message
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Change this to a secure secret key in production
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
# Email configuration
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your-app-password')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'your-email@gmail.com')

# Email settings
app.config['MAIL_MAX_EMAILS'] = 10
app.config['MAIL_DEBUG'] = True  # Enable debug output

# Enable debug mode for development
app.debug = True

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, password, first_name=None):
        self.id = id
        self.email = email
        self.password = password
        self.first_name = first_name or email.split('@')[0]  # Default to part before @ if no first name

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    if user_id in users:
        user_data = users[user_id]
        return User(
            id=user_id,
            email=user_id,
            password=user_data['password'],
            first_name=user_data.get('first_name')
        )
    return None

# Database setup
DATABASE_FOLDER = 'database'
USERS_FILE = os.path.join(DATABASE_FOLDER, 'users.json')
TODOS_FILE = os.path.join(DATABASE_FOLDER, 'todos.json')
DELETED_TODOS_FILE = os.path.join(DATABASE_FOLDER, 'deleted_todos.json')
EXPENSES_FILE = os.path.join(DATABASE_FOLDER, 'expenses.json')

# Ensure database folder exists
os.makedirs(DATABASE_FOLDER, exist_ok=True)

# Initialize expenses file if it doesn't exist
if not os.path.exists(EXPENSES_FILE):
    with open(EXPENSES_FILE, 'w') as f:
        json.dump({"expenses": [], "next_id": 1}, f)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_todos():
    if os.path.exists(TODOS_FILE):
        with open(TODOS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_todos(todos):
    with open(TODOS_FILE, 'w') as f:
        json.dump(todos, f, indent=4)

def load_deleted_todos():
    if os.path.exists(DELETED_TODOS_FILE):
        with open(DELETED_TODOS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_deleted_todos(deleted_todos):
    with open(DELETED_TODOS_FILE, 'w') as f:
        json.dump(deleted_todos, f, indent=4)

def load_expenses():
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, 'r') as f:
            return json.load(f)
    return {"expenses": [], "next_id": 1}

def save_expenses(data):
    with open(EXPENSES_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def cleanup_old_deleted_todos():
    """Remove deleted todos that are older than 15 days"""
    deleted_todos = load_deleted_todos()
    cutoff_date = datetime.now() - timedelta(days=15)
    
    for user_email in list(deleted_todos.keys()):
        if not deleted_todos[user_email]:
            continue
            
        # Filter out todos older than 15 days
        filtered_todos = [
            todo for todo in deleted_todos[user_email]
            if 'deleted_at' in todo and 
            datetime.fromisoformat(todo['deleted_at']) > cutoff_date
        ]
        
        deleted_todos[user_email] = filtered_todos
    
    save_deleted_todos(deleted_todos)

@app.route('/')
def index():
    if 'user_id' in session or current_user.is_authenticated:
        return redirect(url_for('welcome'))
    return redirect(url_for('login'))

@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')

@app.route('/expenses')
@login_required
def expenses():
    return render_template('expenses.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        users = load_users()
        if email in users:
            if check_password_hash(users[email]['password'], password):
                user = User(email, email, users[email]['password'])
                login_user(user)
                flash('Logged in successfully!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('welcome'))
        
        flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
            
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return redirect(url_for('register'))
        
        users = load_users()
        if email in users:
            flash('Email already registered. Please log in.', 'info')
            return redirect(url_for('login'))
        
        try:
            # Create user account directly without verification
            first_name = request.form.get('first_name', '').strip()
            users[email] = {
                'password': generate_password_hash(password),
                'verified': True,
                'first_name': first_name if first_name else None
            }
            save_users(users)
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            app.logger.error(f"Error during registration for {email}: {str(e)}")
            flash('An error occurred during registration. Please try again later.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/test_email')
def test_email():
    """Test email sending functionality"""
    test_email = 'test@example.com'  # Replace with your test email
    test_code = generate_verification_code()
    
    if send_verification_email(test_email, test_code):
        return jsonify({
            'status': 'success',
            'message': f'Test email sent to {test_email} with code: {test_code}'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to send test email. Check server logs for details.'
        }), 500

@app.route('/tasks')
@login_required
def tasks():
    todos = load_todos()
    user_todos = todos.get(str(current_user.id), [])
    return render_template('tasks.html', todos=user_todos)

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get form data
    amount = request.form.get('amount', type=float)
    category = request.form.get('category')
    description = request.form.get('description', '')
    date = request.form.get('date')
    
    # Validate required fields
    if not amount or amount <= 0:
        return jsonify({"error": "Please enter a valid amount"}), 400
    if not category:
        return jsonify({"error": "Please select a category"}), 400
    if not date:
        return jsonify({"error": "Please select a date"}), 400
    
    # Load existing expenses
    data = load_expenses()
    user_email = current_user.email
    
    # Create new expense
    new_expense = {
        "id": data["next_id"],
        "user_email": user_email,
        "amount": float(amount),
        "category": category,
        "description": description,
        "date": date,
        "created_at": datetime.now().isoformat()
    }
    
    # Add to expenses list and increment next_id
    data["expenses"].append(new_expense)
    data["next_id"] += 1
    
    # Save expenses
    save_expenses(data)
    
    return jsonify({"message": "Expense added successfully", "expense": new_expense})

@app.route('/get_expenses')
@login_required
def get_expenses():
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Not authenticated"}), 401
        
        # Get filter parameters
        category = request.args.get('category', '').lower()
        
        # Load expenses
        data = load_expenses()
        user_email = current_user.email
        
        # Initialize expenses list if it doesn't exist
        if "expenses" not in data:
            data["expenses"] = []
        
        # Filter expenses by user and optionally by category
        user_expenses = [
            exp for exp in data["expenses"]
            if exp.get("user_email") == user_email and 
            (not category or exp.get("category") == category)
        ]
        
        # Calculate total
        total = sum(float(exp.get("amount", 0)) for exp in user_expenses)
        
        # Sort by date (newest first)
        user_expenses.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        response_data = {
            "expenses": user_expenses,
            "total": total,
            "status": "success"
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        app.logger.error(f"Error in get_expenses: {str(e)}")
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Load expenses
    data = load_expenses()
    user_email = current_user.email
    
    # Find and remove the expense
    initial_count = len(data["expenses"])
    data["expenses"] = [
        exp for exp in data["expenses"]
        if not (exp["id"] == expense_id and exp["user_email"] == user_email)
    ]
    
    # Check if expense was found and removed
    if len(data["expenses"]) == initial_count:
        return jsonify({"error": "Expense not found or unauthorized"}), 404
    
    # Save updated expenses
    save_expenses(data)
    
    return jsonify({"message": "Expense deleted successfully"})

@app.route('/add_todo', methods=['POST'])
@login_required
def add_todo():
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated"}), 401
        
    # Get form data
    title = request.form.get('title')
    description = request.form.get('description', '')
    due_date = request.form.get('due_date')
    
    # Validate required fields
    if not title or not due_date:
        return jsonify({"error": "Title and due date are required"}), 400
    
    # Load existing todos
    todos = load_todos()
    user_email = current_user.email
    
    # Create new todo
    new_todo = {
        "id": len(todos.get(user_email, [])) + 1,
        "title": title,
        "description": description,
        "due_date": due_date,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    
    # Add to user's todos
    if user_email not in todos:
        todos[user_email] = []
    todos[user_email].append(new_todo)
    
    # Save todos
    save_todos(todos)
    
    return jsonify({"message": "Todo added successfully", "todo": new_todo})

@app.route('/delete_todo/<int:todo_id>', methods=['DELETE'])
@login_required
def delete_todo(todo_id):
    todos = load_todos()
    # ... (rest of the code remains the same)
    deleted_todos = load_deleted_todos()
    
    user_todos = todos.get(str(current_user.id), [])
    todo_to_delete = None
    updated_todos = []
    
    # Find and remove the todo
    for todo in user_todos:
        if todo['id'] == todo_id:
            todo_to_delete = todo
        else:
            updated_todos.append(todo)
    
    if not todo_to_delete:
        return jsonify({'error': 'Todo not found'}), 404
    
    # Add to deleted todos with timestamp
    if str(current_user.id) not in deleted_todos:
        deleted_todos[str(current_user.id)] = []
    
    todo_to_delete['deleted_at'] = datetime.now().isoformat()
    deleted_todos[str(current_user.id)].append(todo_to_delete)
    
    # Save changes
    todos[str(current_user.id)] = updated_todos
    save_todos(todos)
    save_deleted_todos(deleted_todos)
    
    # Clean up old deleted todos
    cleanup_old_deleted_todos()
    
    return jsonify({'success': True, 'message': 'Todo moved to trash'})

@app.route('/get_deleted_todos')
@login_required
def get_deleted_todos():
    deleted_todos = load_deleted_todos()
    user_email = current_user.id  # Assuming current_user.id contains the email
    user_deleted_todos = deleted_todos.get(user_email, [])
    return jsonify(user_deleted_todos)

@app.route('/restore_todo/<int:todo_id>', methods=['POST'])
@login_required
def restore_todo(todo_id):
    todos = load_todos()
    deleted_todos = load_deleted_todos()
    
    user_deleted_todos = deleted_todos.get(str(current_user.id), [])
    todo_to_restore = None
    updated_deleted_todos = []
    
    # Find and remove the todo from deleted
    for todo in user_deleted_todos:
        if todo['id'] == todo_id:
            todo_to_restore = todo
        else:
            updated_deleted_todos.append(todo)
    
    if not todo_to_restore:
        return jsonify({'error': 'Deleted todo not found'}), 404
    
    # Remove deleted_at field and add back to active todos
    if 'deleted_at' in todo_to_restore:
        del todo_to_restore['deleted_at']
    
    if str(current_user.id) not in todos:
        todos[str(current_user.id)] = []
    
    todos[str(current_user.id)].append(todo_to_restore)
    deleted_todos[str(current_user.id)] = updated_deleted_todos
    
    # Save changes
    save_todos(todos)
    save_deleted_todos(deleted_todos)
    
    return jsonify({'success': True, 'message': 'Todo restored successfully'})

@app.route('/delete_permanently/<int:todo_id>', methods=['DELETE'])
@login_required
def delete_permanently(todo_id):
    deleted_todos = load_deleted_todos()
    user_deleted_todos = deleted_todos.get(str(current_user.id), [])
    updated_deleted_todos = []
    found = False
    
    # Remove the todo from deleted
    for todo in user_deleted_todos:
        if todo['id'] != todo_id:
            updated_deleted_todos.append(todo)
        else:
            found = True
    
    if not found:
        return jsonify({'error': 'Deleted todo not found'}), 404
    
    deleted_todos[str(current_user.id)] = updated_deleted_todos
    save_deleted_todos(deleted_todos)
    
    return jsonify({'success': True, 'message': 'Todo permanently deleted'})

@app.route('/update_todo/<int:todo_id>', methods=['POST'])
@login_required
def update_todo(todo_id):
    todos = load_todos()
    user_todos = todos.get(str(current_user.id), [])
    
    todo_to_update = next((todo for todo in user_todos if todo['id'] == todo_id), None)
    if not todo_to_update:
        return jsonify({'error': 'Todo not found'}), 404
    
    # Get data from form
    data = request.get_json()
    if not data:
        data = request.form
    
    # Update todo fields
    if 'title' in data:
        todo_to_update['title'] = data['title']
    if 'description' in data:
        todo_to_update['description'] = data['description']
    if 'due_date' in data:
        todo_to_update['due_date'] = data['due_date']
    if 'completed' in data:
        todo_to_update['completed'] = data['completed'] == 'true' or data['completed'] is True
    
    # Save changes
    todos[str(current_user.id)] = user_todos
    save_todos(todos)
    
    return jsonify({'success': True, 'message': 'Todo updated successfully'})

@app.route('/toggle_todo/<int:todo_id>', methods=['POST'])
@login_required
def toggle_todo(todo_id):
    todos = load_todos()
    user_todos = todos.get(str(current_user.id), [])
    
    todo_to_update = next((todo for todo in user_todos if todo['id'] == todo_id), None)
    if not todo_to_update:
        return jsonify({'error': 'Todo not found'}), 404
    
    todo_to_update['completed'] = not todo_to_update['completed']
    
    todos[str(current_user.id)] = user_todos
    save_todos(todos)
    
    return jsonify({'success': True, 'completed': todo_to_update['completed']})

# Password reset tokens storage (in production, use a database like Redis)
password_reset_tokens = {}

def generate_reset_token():
    """Generate a secure random token for password reset"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        
        if not email:
            flash('Email is required', 'danger')
            return render_template('forgot_password.html', email=email)
        
        users = load_users()
        if email not in users:
            # For security, don't reveal if the email exists or not
            flash('If your email is registered, you will receive a password reset link', 'info')
            return redirect(url_for('login'))
        
        # Generate reset token
        reset_token = generate_reset_token()
        reset_url = url_for('reset_password', token=reset_token, _external=True)
        
        # Store token with expiration (1 hour)
        password_reset_tokens[email] = {
            'token': reset_token,
            'expires_at': datetime.now() + timedelta(hours=1)
        }
        
        # Send reset email
        try:
            print(f"Attempting to send password reset email to {email}")
            msg = MIMEMultipart()
            msg['From'] = app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = email
            msg['Subject'] = 'Password Reset Request - FinDo'
            
            body = f"""
            <h2>Password Reset Request</h2>
            <p>You requested to reset your password for your FinDo account.</p>
            <p>Click the button below to set a new password:</p>
            <p style="margin: 25px 0;">
                <a href="{reset_url}" style="display: inline-block; padding: 12px 25px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                    Reset My Password
                </a>
            </p>
            <p>Or copy and paste this URL into your browser:</p>
            <p style="word-break: break-all;">{reset_url}</p>
            <p>This link will expire in 1 hour.</p>
            <p style="color: #666; font-size: 0.9em;">
                If you didn't request this, you can safely ignore this email. Your password will remain unchanged.
            </p>
            <p>Best regards,<br>FinDo Team</p>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
                server.set_debuglevel(1)  # Enable debug output
                server.ehlo()
                if app.config['MAIL_USE_TLS']:
                    server.starttls()
                    server.ehlo()
                
                username = app.config['MAIL_USERNAME']
                password = app.config['MAIL_PASSWORD']
                print(f"Attempting to login with username: {username}")
                
                if username and password:
                    server.login(username, password)
                
                server.send_message(msg)
            
            print(f"Password reset email sent successfully to {email}")
            flash('If your email is registered, you will receive a password reset link', 'info')
            return redirect(url_for('login'))
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP Authentication Error while sending password reset: {str(e)}"
            print(error_msg)
            app.logger.error(error_msg)
            flash('Failed to send password reset email due to authentication error. Please contact support.', 'danger')
        except smtplib.SMTPException as e:
            error_msg = f"SMTP Error while sending password reset: {str(e)}"
            print(error_msg)
            app.logger.error(error_msg)
            flash('Failed to send password reset email. Please try again later.', 'danger')
        except Exception as e:
            error_msg = f"Error sending password reset email to {email}: {str(e)}"
            print(error_msg)
            app.logger.error(error_msg)
            flash('An unexpected error occurred. Please try again later.', 'danger')
        
        return render_template('forgot_password.html', email=email)
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Find the email associated with this token
    email = None
    for user_email, token_data in password_reset_tokens.items():
        if token_data['token'] == token and token_data['expires_at'] > datetime.now():
            email = user_email
            break
    
    if not email:
        flash('Invalid or expired reset token', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Both password fields are required', 'danger')
            return redirect(request.url)
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(request.url)
            
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return redirect(request.url)
        
        # Update the user's password
        users = load_users()
        if email in users:
            users[email]['password'] = generate_password_hash(password)
            save_users(users)
            
            # Remove the used token
            if email in password_reset_tokens:
                del password_reset_tokens[email]
            
            flash('Your password has been reset successfully. Please log in with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found', 'danger')
            return redirect(url_for('forgot_password'))
    
    return render_template('reset_password.html', token=token)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate input
        if not all(key in data for key in ['name', 'email', 'message']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        name = data['name']
        email = data['email']
        message = data['message']
        
        try:
            # Send email
            msg = Message(
                subject=f'New Contact Form Submission from {name}',
                recipients=[os.getenv('MAIL_DEFAULT_SENDER')],
                reply_to=email,
                body=f"""
                You have received a new contact form submission:
                
                Name: {name}
                Email: {email}
                
                Message:
                {message}
                """
            )
            
            mail.send(msg)
            return jsonify({'success': True, 'message': 'Your message has been sent successfully!'})
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return jsonify({'success': False, 'error': 'Failed to send message. Please try again later.'}), 500
    
    return jsonify({'success': False, 'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    app.run(debug=True, port=8000)
