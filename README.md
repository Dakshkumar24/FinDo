# FinDo - Personal Finance & Task Manager

A secure, responsive web application for managing your finances and tasks, built with Python Flask. Features expense tracking, to-do list management, user registration, and secure login. The application utilizes Bootstrap 5 for a clean and modern interface.

## ✨ Features

### 🔐 User Authentication
- **Secure Registration** with password hashing
- **Login/Logout** functionality with session management
- **Password Hashing** for security

### 📝 Task & Expense Management
- **Track Expenses**: Log and categorize your daily expenses
- **Set Budgets**: Monitor your spending against budgets
- **Task Management**: Create and manage to-do items with due dates
- **Dashboard**: View your financial overview and upcoming tasks
- **Responsive Design**: Works on desktop and mobile devices

### 🛠️ Technical Features
- **Flask** web framework
- **SQLite** database (via SQLAlchemy)
- **Bootstrap 5** for responsive design
- **Flask-Login** for session management
- **CSRF Protection** for form security

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- Gmail account (for email sending)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/todo-app.git
   cd todo-app
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following content:
   ```
   FLASK_APP=flask_app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python flask_app.py
   ```

7. **Open in your browser**
   Visit `http://127.0.0.1:8000` in your web browser

## 🔧 Troubleshooting

### Common Issues
- **Database errors**: Make sure the `database` directory exists and is writable
- **Module not found**: Run `pip install -r requirements.txt`

![image](https://github.com/user-attachments/assets/e1818478-1473-4f79-867d-1dee646f2215)


## 📬 Contact
Have questions or suggestions? Feel free to open an issue or submit a pull request.

---
Built with ❤️ and Python
