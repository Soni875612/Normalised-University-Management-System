# 🎓 Normalised University Management System (NUMS)

**Python + Flask + SQLite | Fully Normalized Database (1NF, 2NF, 3NF)**

---

## 📚 Topics Used in This Project

| Topic | Where Used |
|-------|-----------|
| Python Fundamentals | Variables, loops, conditions in app.py |
| Data Structures | Lists, Dictionaries for DB results |
| Functions | Helper functions: hash_password(), generate_enrollment_no() |
| OOP (Classes) | `Database` class with methods |
| Modules & Packages | Flask, sqlite3, os, hashlib, datetime |
| Exception Handling | try/except in all DB operations |
| File Handling | Reading schema.sql file to init DB |
| Database & SQL | SQLite with normalized schema |
| RDBMS | Foreign keys, Joins, Normalization |
| Database Design | 1NF, 2NF, 3NF applied |
| Database Security | Password hashing, role-based access |
| DB Backup/Recovery | SQLite file = easy backup |

---

## 🗄️ Database Normalization Explained

### 1NF (First Normal Form)
- Student address stored in **separate table** `student_addresses`
- No repeating groups
- Each cell has atomic value

### 2NF (Second Normal Form)
- **Junction tables** used: `enrollments`, `faculty_courses`
- No partial dependencies on composite keys

### 3NF (Third Normal Form)
- **Grade lookup table** separates grade → grade_point mapping
- No transitive dependencies
- Every non-key column depends only on the primary key

---

## 📁 Project Structure

```
university_management/
├── app.py                  # Main Flask application
├── requirements.txt        # Python packages
├── Procfile                # For Heroku/Render hosting
├── .gitignore
├── database/
│   └── schema.sql          # Normalized SQL schema
└── templates/
    ├── base.html           # Base layout
    ├── login.html
    ├── dashboard.html
    ├── students.html
    ├── add_student.html
    ├── view_student.html
    ├── departments.html
    ├── add_department.html
    ├── faculty.html
    ├── add_faculty.html
    ├── courses.html
    ├── add_course.html
    ├── enrollments.html
    ├── grades.html
    └── reports.html
```

---

## 🚀 LOCAL SETUP (Step-by-Step)

### Step 1: Python Install karo
```bash
# Check Python version
python --version   # Python 3.9+ chahiye
```

### Step 2: Project folder me jaao
```bash
cd university_management
```

### Step 3: Virtual Environment banao
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 4: Packages install karo
```bash
pip install -r requirements.txt
```

### Step 5: App run karo
```bash
python app.py
```

### Step 6: Browser me kholо
```
http://localhost:5000
Username: admin
Password: admin123
```

---

## 🌐 HOSTING ON RENDER.COM (FREE - Recommended)

### Step 1: GitHub pe upload karo
```bash
git init
git add .
git commit -m "University Management System"
git remote add origin https://github.com/YOUR_USERNAME/university-management.git
git push -u origin main
```

### Step 2: Render.com pe jaao
1. https://render.com pe account banao (free)
2. "New Web Service" click karo
3. GitHub repo select karo
4. Settings:
   - **Name**: university-management
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. "Create Web Service" click karo
6. 2-3 minute mein live ho jayega!

### Step 3: Live URL milega
```
https://university-management-xxxx.onrender.com
```

---

## 📊 ER DIAGRAM (Tables & Relations)

```
departments (1) ──< students (M)
departments (1) ──< faculty  (M)
departments (1) ──< courses  (M)
students    (M) >──< courses (M)  [via enrollments]
faculty     (M) >──< courses (M)  [via faculty_courses]
enrollments (1) ──< grades   (1)
enrollments (1) ──< attendance (M)
grade_lookup(1) ──< grades   (M)
students    (1) ──< student_addresses (1)
```

---

## 👤 User Roles

| Role | Access |
|------|--------|
| admin | Full access - add/delete everything |
| faculty | View + Enter grades |
| student | View own profile + grades |

---

## 🔐 Security Features
- Password hashing (SHA-256)
- Session-based authentication
- Role-based access control (RBAC)
- SQL parameterized queries (no SQL injection)
- Foreign key constraints

---

## 📝 Default Login
- **Username**: admin
- **Password**: admin123