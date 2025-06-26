# Web-Based Todo List Application

A secure, responsive web application for managing your tasks, built with Python Flask. Features user registration with email verification, secure login, and full CRUD operations for tasks. The application uses Bootstrap 5 for a clean, modern interface and includes email verification for enhanced security.

![Todo App Screenshot](https://via.placeholder.com/800x500.png?text=Todo+App+Screenshot)

## ✨ Features

### 🔐 User Authentication
- **Secure Registration** with email verification
- **Login/Logout** functionality with session management
- **Password Hashing** for security
- **Email Verification** with expiring verification codes

### 📝 Task Management
- **Create** new tasks with title, description, and due date
- **Read** all your tasks in a clean, organized view
- **Update** task details or mark as complete
- **Delete** tasks you no longer need
- **Responsive Design** works on desktop and mobile devices

### 🛠️ Technical Features
- **Flask** web framework
- **SQLite** database (via SQLAlchemy)
- **Bootstrap 5** for responsive design
- **Flask-Login** for session management
- **Email verification** with SMTP
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
   SECRET_KEY=your-secret-key-here
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
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

## 📧 Email Configuration
For email verification to work, you need to:
1. Use a Gmail account
2. Enable "Less secure app access" or create an App Password
3. Update the `.env` file with your email credentials

## 🔧 Troubleshooting

### Common Issues
- **Email not sending**: Check your Gmail security settings and app password
- **Database errors**: Make sure the `database` directory exists and is writable
- **Module not found**: Run `pip install -r requirements.txt`

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- Flask Team for the amazing web framework
- Bootstrap for the responsive design
- All open-source contributors

## 📬 Contact
Have questions or suggestions? Feel free to open an issue or submit a pull request.

---
Built with ❤️ and Python
