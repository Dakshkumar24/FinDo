from flask import Flask, request, jsonify, render_template, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import csv
import io
import os

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
    data = request.get_json()
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Missing title'}), 400

    # Save to database
    task = Task(title=title)
    db.session.add(task)
    db.session.commit()

    # Append to CSV
    csv_file = os.path.join(os.path.dirname(__file__), 'tasks.csv')
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['ID', 'Title', 'Completed'])
        writer.writerow([task.id, task.title, task.completed])

    print(f"✔ Task saved to tasks.csv → {task.title}")
    print(f"✔ Added to DB: {task.title}")
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
    return jsonify({'message': 'Task deleted'})

# Export tasks to CSV (Download)
@app.route('/export', methods=['GET'])
def export_tasks():
    tasks = Task.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'Completed'])
    for task in tasks:
        writer.writerow([task.id, task.title, task.completed])
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=tasks.csv'
    return response

# Save tasks to CSV file on server (overwrite)
@app.route('/save_csv', methods=['GET'])
def save_csv():
    tasks = Task.query.all()
    with open('tasks.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Title', 'Completed'])
        for task in tasks:
            writer.writerow([task.id, task.title, task.completed])
    return 'tasks.csv file has been saved in project directory.'

if __name__ == '__main__':
    app.run(debug=True)
