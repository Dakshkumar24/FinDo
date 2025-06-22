from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this for production!

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

from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@login_required
def index():
    username = session['username']
    tasks = get_tasks(username)
    return render_template('index.html', username=username, tasks=tasks)

@app.route('/add', methods=['POST'])
@login_required
def add():
    task = request.form.get('task')
    if task:
        add_task(session['username'], task)
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>')
@login_required
def toggle(task_id):
    username = session['username']
    tasks = get_tasks(username)
    if 0 <= task_id < len(tasks):
        tasks[task_id]['completed'] = not tasks[task_id]['completed']
        update_tasks(username, tasks)
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
@login_required
def delete(task_id):
    username = session['username']
    tasks = get_tasks(username)
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        update_tasks(username, tasks)
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_exists(username):
            flash('Username already exists.')
            return redirect(url_for('signup'))
        add_user(username, password)
        flash('Signup successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verify_user(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
