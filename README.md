# Normalised-University-Management-System
A comprehensive University Management System built with Python Flask featuring normalized database design, multi-user authentication, and role-based access control.
# 🎓 Normalised University Management System 🎓

A full-stack web application for managing university operations including student enrollment, faculty management, course administration, and grade tracking.

## ✨ Features

### Core Functionality
- **Multi-User Authentication** - Self-registration with role-based access (Admin, Faculty, Student)
- **Student Management** - Complete CRUD operations with profile management
- **Faculty Management** - Faculty records with course assignments
- **Course Management** - Course creation, enrollment tracking, and credit management
- **Grade System** - Automated grade calculation with CGPA computation
- **Reports & Analytics** - Department-wise statistics and top performers leaderboard

### Technical Features
- **Normalized Database Design** - 3NF compliant schema with 11+ tables
- **Role-Based Access Control** - Different permissions for Admin, Faculty, and Students
- **Password Security** - SHA-256 hashing for user credentials
- **Session Management** - Secure login/logout with Flask sessions
- **Responsive UI** - Bootstrap 5 with mobile-friendly design
- **RESTful Architecture** - Clean API structure with proper routing

## 🛠️ Tech Stack

**Backend:**
- Python 3.x
- Flask (Web Framework)
- SQLite (Database)
- Jinja2 (Templating)

**Frontend:**
- HTML5, CSS3
- Bootstrap 5
- Font Awesome Icons
- JavaScript

**Deployment:**
- Gunicorn (WSGI Server)
- Ready for Render.com/Heroku

## 📊 Database Schema

Normalized database structure following 1NF, 2NF, and 3NF:
- `departments` - Department information
- `students` - Student records
- `student_addresses` - Separate address table (1NF)
- `faculty` - Faculty information
- `courses` - Course catalog
- `enrollments` - Student-course junction (resolves M:N)
- `grades` - Grade records
- `grade_lookup` - Grade scale reference
- `faculty_courses` - Faculty-course assignments
- `users` - Authentication & authorization

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.9+
pip
```

### Installation

1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/university-management.git
cd university-management
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python app.py
```

4. Open in browser
```
http://127.0.0.1:5000
```

## 👤 Default Login Credentials

**Admin Access:**
- Username: `admin`
- Password: `admin123`

**Test Accounts:**
- Student: `student1` / `student123`
- Faculty: `faculty1` / `faculty123`

## 📸 Screenshots
<img width="1913" height="911" alt="Screenshot 2026-02-21 220814" src="https://github.com/user-attachments/assets/086f290a-e1dd-4ba0-aa68-53ca98fe4544" />

<img width="1917" height="915" alt="image" src="https://github.com/user-attachments/assets/6d9f4667-17e2-4ba4-bd97-16b849678521" />


## 🔐 Security Features

- Password hashing (SHA-256)
- SQL injection prevention (parameterized queries)
- Session-based authentication
- Role-based authorization
- CSRF protection

## 📝 Key Learnings

This project demonstrates:
- Object-Oriented Programming in Python
- Database normalization and design
- Web application architecture (MVC pattern)
- RESTful API design
- Exception handling and error management
- File I/O operations
- Session management
- SQL joins and complex queries

## 🌐 Deployment

Ready for deployment on:
- Render.com
- Heroku
- PythonAnywhere
- Railway.app

See `Procfile` for production configuration.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Soni**
- GitHub:(https://github.com/Soni875612/)
- LinkedIn:(https://www.linkedin.com/feed/)

## 🙏 Acknowledgments

Special thanks to **Saksham Mishra Sir** for guidance and mentorship throughout this project.

## 📞 Contact

8765568506

---

**⭐ If you found this project helpful, please give it a star!**
```

---

## 🎯 **Topics/Tags (GitHub repository settings mein):**
```
python
flask
sqlite
web-development
database
crud
authentication
authorization
bootstrap
education
university
management-system
full-stack
