# from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS
# from models import db, Task
#
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# db.init_app(app)
# CORS(app)
#
# @app.before_first_request
# def create_tables():
#     db.create_all()
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
# @app.route('/tasks', methods=['GET'])
# def get_tasks():
#     tasks = Task.query.all()
#     return jsonify([{'id': t.id, 'title': t.title, 'completed': t.completed} for t in tasks])
#
# @app.route('/tasks', methods=['POST'])
# def add_task():
#     data = request.get_json()
#     new_task = Task(title=data['title'])
#     db.session.add(new_task)
#     db.session.commit()
#     return jsonify({'id': new_task.id, 'title': new_task.title, 'completed': new_task.completed})
#
# @app.route('/tasks/<int:task_id>', methods=['DELETE'])
# def delete_task(task_id):
#     task = Task.query.get(task_id)
#     db.session.delete(task)
#     db.session.commit()
#     return jsonify({'message': 'Task deleted'})
#
# @app.route('/tasks/<int:task_id>', methods=['PUT'])
# def update_task(task_id):
#     task = Task.query.get(task_id)
#     data = request.get_json()
#     task.completed = data['completed']
#     db.session.commit()
#     return jsonify({'message': 'Task updated'})
#
# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    completed = db.Column(db.Boolean, default=False)

# Initialize DB
with app.app_context():
    db.create_all()

# Serve base HTML
@app.route('/')
def index():
    return render_template('index.html')

# Get all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([
        {'id': task.id, 'title': task.title, 'completed': task.completed}
        for task in tasks
    ])

# Add new task and save to CSV
@app.route('/tasks', methods=['POST'])
def add_task():
    print("📩 Received POST /tasks request")
    data = request.get_json()
    print("📦 JSON received:", data)

    title = data.get('title') if data else None
    if not title:
        print("❌ Missing title in request body.")
        return jsonify({'error': 'Missing title'}), 400

    # Save to database
    task = Task(title=title)
    db.session.add(task)
    db.session.commit()
    print(f"✔ Task added to DB: {task.title}")

    # Save to CSV file
    csv_file = os.path.join(os.path.dirname(__file__), 'tasks.csv')
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['ID', 'Title', 'Completed'])
        writer.writerow([task.id, task.title, task.completed])

    print(f"📝 Task written to CSV: {task.title}")
    return jsonify({'id': task.id, 'title': task.title, 'completed': task.completed})

# Toggle task completion
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify({'message': 'Task updated'})

# Delete task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    print(f"🗑️ Task deleted from DB: {task.title}")

    # Rewrite tasks.csv after deletion
    csv_file = os.path.join(os.path.dirname(__file__), 'tasks.csv')
    tasks = Task.query.all()
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Title', 'Completed'])
        for t in tasks:
            writer.writerow([t.id, t.title, t.completed])
    print("🧹 CSV file rewritten after deletion.")

    return jsonify({'message': 'Task deleted'})

if __name__ == '__main__':
    app.run(debug=True)
