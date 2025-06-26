from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key in production

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
        if email in users and check_password_hash(users[email]['password'], password):
            user = User(email, email, users[email]['password'])
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
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
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        users = load_users()
        if email in users:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        users[email] = {
            'password': generate_password_hash(password),
            'created_at': datetime.now().isoformat()
        }
        save_users(users)
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
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
