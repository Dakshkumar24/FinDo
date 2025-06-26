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

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key in production

# Email configuration - ensure all required variables are set
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
app.config['MAIL_USERNAME'] = 'dakshkumar19860@gmail.com'  # Using the email directly for now
app.config['MAIL_PASSWORD'] = 'jpud hbik syny jsnn'  # Using the app password directly for now
app.config['MAIL_DEFAULT_SENDER'] = 'dakshkumar19860@gmail.com'

# Enable debug mode for development
app.debug = True

# Verification codes storage (in production, use a database like Redis)
verification_codes = {}

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code):
    """Send verification email with the code"""
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = email
        msg['Subject'] = 'Email Verification Code'
        
        body = f"""
        <h2>Email Verification</h2>
        <p>Thank you for registering!</p>
        <p>Your verification code is: <strong>{code}</strong></p>
        <p>This code will expire in 10 minutes.</p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    if user_id in users:
        user_data = users[user_id]
        return User(user_id, user_id, user_data['password'])
    return None

# Database setup
DATABASE_FOLDER = 'database'
USERS_FILE = os.path.join(DATABASE_FOLDER, 'users.json')
TODOS_FILE = os.path.join(DATABASE_FOLDER, 'todos.json')

# Ensure database folder exists
os.makedirs(DATABASE_FOLDER, exist_ok=True)

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

# The @login_required decorator is now provided by Flask-Login

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        users = load_users()
        if email in users:
            if not users[email].get('verified', False):
                # If user exists but email isn't verified, allow them to resend verification
                verification_code = generate_verification_code()
                verification_codes[email] = {
                    'code': verification_code,
                    'expires_at': datetime.now() + timedelta(minutes=10)
                }
                session['pending_user'] = {
                    'email': email,
                    'password': users[email]['password']
                }
                if send_verification_email(email, verification_code):
                    flash('Your email is not verified. A new verification code has been sent to your email.', 'warning')
                    return redirect(url_for('verify_email'))
                else:
                    flash('Error sending verification email. Please try again.', 'danger')
                    return redirect(url_for('login'))
            
            if check_password_hash(users[email]['password'], password):
                user = User(email, email, users[email]['password'])
                login_user(user)
                flash('Logged in successfully!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        
        flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/resend_verification', methods=['GET'])
def resend_verification():
    if 'pending_user' not in session:
        flash('No pending verification. Please register again.', 'danger')
        return redirect(url_for('register'))
    
    email = session['pending_user']['email']
    
    # Generate new verification code
    verification_code = generate_verification_code()
    verification_codes[email] = {
        'code': verification_code,
        'expires_at': datetime.now() + timedelta(minutes=10)
    }
    
    # Send verification email
    try:
        if send_verification_email(email, verification_code):
            flash('New verification code has been sent to your email.', 'success')
        else:
            flash('Failed to send verification email. Please check your email configuration.', 'danger')
    except Exception as e:
        print(f"Error sending verification email: {e}")
        flash('An error occurred while sending the verification email. Please try again later.', 'danger')
    
    return redirect(url_for('verify_email'))

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    # Check if there's a pending user in the session
    if 'pending_user' not in session:
        flash('No pending verification. Please register first.', 'info')
        return redirect(url_for('register'))
    
    user_data = session['pending_user']
    email = user_data.get('email')
    
    if not email:
        flash('Invalid session. Please register again.', 'danger')
        session.pop('pending_user', None)
        return redirect(url_for('register'))
        
    if request.method == 'POST':
        user_code = request.form.get('verification_code', '').strip()
        
        if not user_code:
            flash('Please enter the verification code', 'danger')
            return render_template('verify_email.html', email=email)
        
        # Check if verification code exists and is not expired
        if (email in verification_codes and 
            'code' in verification_codes[email] and
            'expires_at' in verification_codes[email] and
            verification_codes[email]['code'] == user_code and 
            datetime.now() < verification_codes[email]['expires_at']):
            
            try:
                # Save the user
                users = load_users()
                users[email] = {
                    'password': user_data['password'],
                    'created_at': datetime.now().isoformat(),
                    'verified': True
                }
                save_users(users)
                
                # Clean up
                if email in verification_codes:
                    del verification_codes[email]
                session.pop('pending_user', None)
                
                flash('Email verified successfully! Please log in.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                print(f"Error during verification: {e}")
                flash('An error occurred during verification. Please try again.', 'danger')
                return redirect(url_for('verify_email'))
        else:
            flash('Invalid or expired verification code. Please try again or request a new code.', 'danger')
    
    return render_template('verify_email.html', email=email)

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
        
        users = load_users()
        if email in users and users[email].get('verified', False):
            flash('Email already registered. Please log in.', 'info')
            return redirect(url_for('login'))
        
        try:
            # Generate verification code
            verification_code = generate_verification_code()
            verification_codes[email] = {
                'code': verification_code,
                'expires_at': datetime.now() + timedelta(minutes=10)
            }
            
            # Send verification email
            if not send_verification_email(email, verification_code):
                flash('Error sending verification email. Please try again.', 'danger')
                return redirect(url_for('register'))
            
            # Store user data in session for verification
            session['pending_user'] = {
                'email': email,
                'password': generate_password_hash(password)
            }
            
            flash('Verification code sent to your email. Please check your inbox.', 'success')
            return redirect(url_for('verify_email'))
            
        except Exception as e:
            print(f"Error during registration: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    todos = load_todos()
    user_todos = todos.get(current_user.id, [])
    return render_template('dashboard.html', todos=user_todos)

@app.route('/add_todo', methods=['POST'])
@login_required
def add_todo():
    title = request.form.get('title')
    description = request.form.get('description', '')
    due_date = request.form.get('due_date')
    
    if not title or not due_date:
        return jsonify({'error': 'Title and due date are required'}), 400
    
    todos = load_todos()
    user_todos = todos.get(current_user.id, [])
    
    new_todo = {
        'id': len(user_todos) + 1,
        'title': title,
        'description': description,
        'due_date': due_date,
        'completed': False,
        'created_at': datetime.now().isoformat()
    }
    
    user_todos.append(new_todo)
    todos[current_user.id] = user_todos
    save_todos(todos)
    
    return jsonify({'success': True, 'todo': new_todo})

@app.route('/delete_todo/<int:todo_id>', methods=['DELETE'])
@login_required
def delete_todo(todo_id):
    todos = load_todos()
    user_todos = todos.get(current_user.id, [])
    
    initial_length = len(user_todos)
    user_todos = [todo for todo in user_todos if todo['id'] != todo_id]
    
    if len(user_todos) == initial_length:
        return jsonify({'error': 'Todo not found'}), 404
    
    todos[current_user.id] = user_todos
    save_todos(todos)
    
    return jsonify({'success': True, 'message': 'Todo deleted successfully'})

@app.route('/update_todo/<int:todo_id>', methods=['POST'])
@login_required
def update_todo(todo_id):
    todos = load_todos()
    user_todos = todos.get(current_user.id, [])
    
    todo_to_update = next((todo for todo in user_todos if todo['id'] == todo_id), None)
    if not todo_to_update:
        return jsonify({'error': 'Todo not found'}), 404
    
    # Update todo fields
    todo_to_update['title'] = request.form.get('title', todo_to_update['title'])
    todo_to_update['description'] = request.form.get('description', todo_to_update.get('description', ''))
    todo_to_update['due_date'] = request.form.get('due_date', todo_to_update['due_date'])
    todo_to_update['completed'] = 'completed' in request.form
    
    todos[current_user.id] = user_todos
    save_todos(todos)
    
    return jsonify({'success': True, 'message': 'Todo updated successfully'})

@app.route('/toggle_todo/<int:todo_id>', methods=['POST'])
@login_required
def toggle_todo(todo_id):
    todos = load_todos()
    user_todos = todos.get(current_user.id, [])
    
    todo_to_update = next((todo for todo in user_todos if todo['id'] == todo_id), None)
    if not todo_to_update:
        return jsonify({'error': 'Todo not found'}), 404
    
    todo_to_update['completed'] = not todo_to_update['completed']
    
    todos[current_user.id] = user_todos
    save_todos(todos)
    
    return jsonify({'success': True, 'completed': todo_to_update['completed']})

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)
