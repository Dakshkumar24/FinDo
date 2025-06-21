const API = '/tasks';

function fetchTasks() {
  fetch(API)
    .then(res => res.json())
    .then(tasks => {
      const list = document.getElementById('taskList');
      list.innerHTML = '';
      tasks.forEach(task => {
        const li = document.createElement('li');
        li.innerHTML = `
          <input type="checkbox" ${task.completed ? 'checked' : ''} onclick="toggleTask(${task.id}, ${!task.completed})" />
          ${task.title}
          <button onclick="deleteTask(${task.id})">Delete</button>
        `;
        list.appendChild(li);
      });
    });
}

function addTask() {
  const input = document.getElementById('taskInput');
  const title = input.value;
  if (!title) return;
  fetch(API, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ title })
  }).then(() => {
    input.value = '';
    fetchTasks();
  });
}

function deleteTask(id) {
  fetch(`${API}/${id}`, { method: 'DELETE' })
    .then(() => fetchTasks());
}

function toggleTask(id, completed) {
  fetch(`${API}/${id}`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ completed })
  }).then(() => fetchTasks());
}

document.addEventListener('DOMContentLoaded', fetchTasks);
