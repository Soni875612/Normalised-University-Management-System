"""
NORMALISED UNIVERSITY MANAGEMENT SYSTEM
========================================
Python + Flask + SQLite
schema.sql ki zaroorat NAHI - sab kuch yahan hai
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import hashlib
from functools import wraps
from datetime import datetime

# ──────────────────────────────────────────────
# APP CONFIGURATION
# ──────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'university_secret_key_2024'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'database', 'university.db')


# ──────────────────────────────────────────────
# DATABASE CLASS
# ──────────────────────────────────────────────
class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        """Database aur tables banao - schema.sql ki zaroorat nahi"""
        try:
            # Database folder automatically banao
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)

            conn = self.get_connection()
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS departments (
                    dept_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    dept_name  TEXT NOT NULL UNIQUE,
                    dept_code  TEXT NOT NULL UNIQUE,
                    hod_name   TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS courses (
                    course_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_name TEXT NOT NULL,
                    course_code TEXT NOT NULL UNIQUE,
                    credits     INTEGER NOT NULL,
                    dept_id     INTEGER NOT NULL,
                    semester    INTEGER NOT NULL,
                    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
                );

                CREATE TABLE IF NOT EXISTS students (
                    student_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    enrollment_no  TEXT NOT NULL UNIQUE,
                    first_name     TEXT NOT NULL,
                    last_name      TEXT NOT NULL,
                    email          TEXT NOT NULL UNIQUE,
                    phone          TEXT,
                    dob            TEXT,
                    gender         TEXT,
                    dept_id        INTEGER NOT NULL,
                    semester       INTEGER NOT NULL,
                    admission_year INTEGER NOT NULL,
                    status         TEXT DEFAULT 'Active',
                    created_at     TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
                );

                CREATE TABLE IF NOT EXISTS student_addresses (
                    address_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL UNIQUE,
                    street     TEXT,
                    city       TEXT,
                    state      TEXT,
                    pincode    TEXT,
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS faculty (
                    faculty_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    faculty_code  TEXT NOT NULL UNIQUE,
                    first_name    TEXT NOT NULL,
                    last_name     TEXT NOT NULL,
                    email         TEXT NOT NULL UNIQUE,
                    phone         TEXT,
                    qualification TEXT,
                    designation   TEXT,
                    dept_id       INTEGER NOT NULL,
                    joining_date  TEXT,
                    status        TEXT DEFAULT 'Active',
                    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
                );

                CREATE TABLE IF NOT EXISTS enrollments (
                    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id    INTEGER NOT NULL,
                    course_id     INTEGER NOT NULL,
                    academic_year TEXT NOT NULL,
                    semester      INTEGER NOT NULL,
                    enrolled_on   TEXT DEFAULT (datetime('now')),
                    UNIQUE(student_id, course_id, academic_year),
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id)  REFERENCES courses(course_id)  ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS grade_lookup (
                    grade       TEXT PRIMARY KEY,
                    grade_point REAL NOT NULL,
                    min_marks   INTEGER NOT NULL,
                    max_marks   INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS grades (
                    grade_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    enrollment_id  INTEGER NOT NULL UNIQUE,
                    marks_obtained INTEGER,
                    grade          TEXT,
                    remarks        TEXT,
                    recorded_on    TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS faculty_courses (
                    assign_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    faculty_id    INTEGER NOT NULL,
                    course_id     INTEGER NOT NULL,
                    academic_year TEXT NOT NULL,
                    semester      INTEGER NOT NULL,
                    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id)  REFERENCES courses(course_id)  ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS users (
                    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    username      TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role          TEXT NOT NULL,
                    ref_id        INTEGER,
                    is_active     INTEGER DEFAULT 1,
                    created_at    TEXT DEFAULT (datetime('now'))
                );

                INSERT OR IGNORE INTO grade_lookup VALUES ('O',  10.0, 90, 100);
                INSERT OR IGNORE INTO grade_lookup VALUES ('A+',  9.0, 80,  89);
                INSERT OR IGNORE INTO grade_lookup VALUES ('A',   8.0, 70,  79);
                INSERT OR IGNORE INTO grade_lookup VALUES ('B+',  7.0, 60,  69);
                INSERT OR IGNORE INTO grade_lookup VALUES ('B',   6.0, 50,  59);
                INSERT OR IGNORE INTO grade_lookup VALUES ('C',   5.0, 40,  49);
                INSERT OR IGNORE INTO grade_lookup VALUES ('F',   0.0,  0,  39);

                INSERT OR IGNORE INTO departments (dept_name, dept_code, hod_name)
                    VALUES ('Computer Science', 'CS', 'Dr. Ramesh Kumar');
                INSERT OR IGNORE INTO departments (dept_name, dept_code, hod_name)
                    VALUES ('Information Technology', 'IT', 'Dr. Priya Sharma');
                INSERT OR IGNORE INTO departments (dept_name, dept_code, hod_name)
                    VALUES ('Electronics', 'EC', 'Dr. Suresh Patel');
                INSERT OR IGNORE INTO departments (dept_name, dept_code, hod_name)
                    VALUES ('Mechanical Engineering', 'ME', 'Dr. Anjali Singh');
            """)
            conn.commit()
            conn.close()
            self.create_admin_user()
        except Exception as e:
            raise Exception(f"Database init error: {e}")

    def create_admin_user(self):
        conn = self.get_connection()
        try:
            pwd_hash = hash_password('admin123')
            conn.execute(
                "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?,?,?)",
                ('admin', pwd_hash, 'admin')
            )
            conn.commit()
        except Exception as e:
            print(f"Warning: {e}")
        finally:
            conn.close()

    def execute_query(self, query, params=()):
        conn = self.get_connection()
        try:
            cur = conn.execute(query, params)
            conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Data conflict: {e}")
        except sqlite3.Error as e:
            raise Exception(f"DB Error: {e}")
        finally:
            conn.close()

    def fetch_all(self, query, params=()):
        conn = self.get_connection()
        try:
            cur = conn.execute(query, params)
            return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Fetch error: {e}")
        finally:
            conn.close()

    def fetch_one(self, query, params=()):
        conn = self.get_connection()
        try:
            cur = conn.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Fetch error: {e}")
        finally:
            conn.close()


# ──────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login first!', 'warning')
                return redirect(url_for('login'))
            if role and session.get('role') != role and session.get('role') != 'admin':
                flash('Access denied!', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

def generate_enrollment_no():
    year  = datetime.now().year
    count = db.fetch_one("SELECT COUNT(*) as cnt FROM students")
    num   = (count['cnt'] + 1) if count else 1
    return f"UMS{year}{num:04d}"

def generate_faculty_code():
    count = db.fetch_one("SELECT COUNT(*) as cnt FROM faculty")
    num   = (count['cnt'] + 1) if count else 1
    return f"FAC{num:04d}"


# ──────────────────────────────────────────────
# INITIALIZE DB
# ──────────────────────────────────────────────
db = Database(DB_PATH)


# ══════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        try:
            user = db.fetch_one(
                "SELECT * FROM users WHERE username=? AND is_active=1", (username,)
            )
            if user and user['password_hash'] == hash_password(password):
                session['user_id']  = user['user_id']
                session['username'] = user['username']
                session['role']     = user['role']
                flash(f"Welcome, {username}!", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password!', 'danger')
        except Exception as e:
            flash(f'Login error: {e}', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validation
        if not username or not password or not full_name or not email:
            flash('All fields are required!', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match!', 'danger')
        else:
            try:
                # Check if username already exists
                existing = db.fetch_one("SELECT user_id FROM users WHERE username=?", (username,))
                if existing:
                    flash('Username already taken!', 'danger')
                else:
                    # Create new user with 'student' role by default
                    pwd_hash = hash_password(password)
                    user_id = db.execute_query(
                        "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                        (username, pwd_hash, 'student')
                    )
                    # Auto-create student record
                    enrollment_no = generate_enrollment_no()
                    names = full_name.split(' ', 1)
                    first_name = names[0]
                    last_name = names[1] if len(names) > 1 else ''
                    
                    student_id = db.execute_query("""
                        INSERT INTO students
                        (enrollment_no, first_name, last_name, email, dept_id, semester, admission_year)
                        VALUES (?,?,?,?,1,1,?)
                    """, (enrollment_no, first_name, last_name, email, datetime.now().year))
                    
                    # Link user to student
                    db.execute_query(
                        "UPDATE users SET ref_id=? WHERE user_id=?",
                        (student_id, user_id)
                    )
                    
                    flash(f'Account created! Your enrollment no: {enrollment_no}', 'success')
                    return redirect(url_for('login'))
            except Exception as e:
                flash(f'Registration error: {e}', 'danger')
    return render_template('register.html')

@app.route('/dashboard')
@login_required()
def dashboard():
    stats = {
        'students':    db.fetch_one("SELECT COUNT(*) as c FROM students WHERE status='Active'")['c'],
        'faculty':     db.fetch_one("SELECT COUNT(*) as c FROM faculty WHERE status='Active'")['c'],
        'departments': db.fetch_one("SELECT COUNT(*) as c FROM departments")['c'],
        'courses':     db.fetch_one("SELECT COUNT(*) as c FROM courses")['c'],
    }
    recent = db.fetch_all("""
        SELECT s.first_name||' '||s.last_name as name, d.dept_name, s.created_at
        FROM students s JOIN departments d ON s.dept_id=d.dept_id
        ORDER BY s.created_at DESC LIMIT 5
    """)
    return render_template('dashboard.html', stats=stats, recent=recent)


# ── DEPARTMENTS ────────────────────────────────
@app.route('/departments')
@login_required()
def departments():
    depts = db.fetch_all("""
        SELECT d.*, COUNT(s.student_id) as student_count
        FROM departments d
        LEFT JOIN students s ON d.dept_id=s.dept_id
        GROUP BY d.dept_id ORDER BY d.dept_name
    """)
    return render_template('departments.html', departments=depts)

@app.route('/departments/add', methods=['GET', 'POST'])
@login_required('admin')
def add_department():
    if request.method == 'POST':
        try:
            db.execute_query(
                "INSERT INTO departments (dept_name, dept_code, hod_name) VALUES (?,?,?)",
                (request.form['dept_name'], request.form['dept_code'], request.form['hod_name'])
            )
            flash('Department added!', 'success')
            return redirect(url_for('departments'))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('add_department.html')

@app.route('/departments/delete/<int:dept_id>')
@login_required('admin')
def delete_department(dept_id):
    try:
        db.execute_query("DELETE FROM departments WHERE dept_id=?", (dept_id,))
        flash('Department deleted!', 'success')
    except Exception as e:
        flash(f'Cannot delete: {e}', 'danger')
    return redirect(url_for('departments'))


# ── STUDENTS ────────────────────────────────────
@app.route('/students')
@login_required()
def students():
    search  = request.args.get('search', '')
    dept_id = request.args.get('dept_id', '')
    query   = """
        SELECT s.*, d.dept_name, a.city, a.state
        FROM students s
        JOIN departments d ON s.dept_id=d.dept_id
        LEFT JOIN student_addresses a ON s.student_id=a.student_id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (s.first_name||' '||s.last_name LIKE ? OR s.enrollment_no LIKE ? OR s.email LIKE ?)"
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    if dept_id:
        query += " AND s.dept_id=?"
        params.append(dept_id)
    query += " ORDER BY s.created_at DESC"
    student_list = db.fetch_all(query, params)
    depts = db.fetch_all("SELECT * FROM departments ORDER BY dept_name")
    return render_template('students.html', students=student_list, departments=depts,
                           search=search, dept_id=dept_id)

@app.route('/students/add', methods=['GET', 'POST'])
@login_required('admin')
def add_student():
    depts = db.fetch_all("SELECT * FROM departments ORDER BY dept_name")
    if request.method == 'POST':
        try:
            enrollment_no = generate_enrollment_no()
            student_id = db.execute_query("""
                INSERT INTO students
                (enrollment_no, first_name, last_name, email, phone,
                 dob, gender, dept_id, semester, admission_year)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                enrollment_no,
                request.form['first_name'], request.form['last_name'],
                request.form['email'], request.form.get('phone', ''),
                request.form.get('dob', ''), request.form.get('gender', ''),
                request.form['dept_id'], request.form['semester'],
                request.form['admission_year']
            ))
            db.execute_query(
                "INSERT INTO student_addresses (student_id, street, city, state, pincode) VALUES (?,?,?,?,?)",
                (student_id, request.form.get('street',''), request.form.get('city',''),
                 request.form.get('state',''), request.form.get('pincode',''))
            )
            db.execute_query(
                "INSERT OR IGNORE INTO users (username, password_hash, role, ref_id) VALUES (?,?,?,?)",
                (enrollment_no, hash_password(enrollment_no), 'student', student_id)
            )
            flash(f'Student added! Enrollment No: {enrollment_no}', 'success')
            return redirect(url_for('students'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    return render_template('add_student.html', departments=depts, current_year=datetime.now().year)

@app.route('/students/view/<int:student_id>')
@login_required()
def view_student(student_id):
    student = db.fetch_one("""
        SELECT s.*, d.dept_name, a.street, a.city, a.state, a.pincode
        FROM students s
        JOIN departments d ON s.dept_id=d.dept_id
        LEFT JOIN student_addresses a ON s.student_id=a.student_id
        WHERE s.student_id=?
    """, (student_id,))
    if not student:
        flash('Student not found!', 'danger')
        return redirect(url_for('students'))
    enrollments = db.fetch_all("""
        SELECT e.*, c.course_name, c.course_code, c.credits,
               g.marks_obtained, g.grade, gl.grade_point
        FROM enrollments e
        JOIN courses c ON e.course_id=c.course_id
        LEFT JOIN grades g ON e.enrollment_id=g.enrollment_id
        LEFT JOIN grade_lookup gl ON g.grade=gl.grade
        WHERE e.student_id=? ORDER BY e.academic_year DESC
    """, (student_id,))
    cgpa = 0
    graded = [e for e in enrollments if e.get('grade_point') is not None]
    if graded:
        total_credits = sum(e['credits'] for e in graded)
        total_points  = sum(e['credits'] * e['grade_point'] for e in graded)
        cgpa = round(total_points / total_credits, 2) if total_credits else 0
    return render_template('view_student.html', student=student, enrollments=enrollments, cgpa=cgpa)

@app.route('/students/delete/<int:student_id>')
@login_required('admin')
def delete_student(student_id):
    try:
        db.execute_query("DELETE FROM students WHERE student_id=?", (student_id,))
        flash('Student deleted!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('students'))


# ── FACULTY ─────────────────────────────────────
@app.route('/faculty')
@login_required()
def faculty_list():
    faculty = db.fetch_all("""
        SELECT f.*, d.dept_name, COUNT(fc.course_id) as courses_assigned
        FROM faculty f
        JOIN departments d ON f.dept_id=d.dept_id
        LEFT JOIN faculty_courses fc ON f.faculty_id=fc.faculty_id
        GROUP BY f.faculty_id ORDER BY f.first_name
    """)
    return render_template('faculty.html', faculty=faculty)

@app.route('/faculty/add', methods=['GET', 'POST'])
@login_required('admin')
def add_faculty():
    depts = db.fetch_all("SELECT * FROM departments ORDER BY dept_name")
    if request.method == 'POST':
        try:
            faculty_code = generate_faculty_code()
            fac_id = db.execute_query("""
                INSERT INTO faculty
                (faculty_code, first_name, last_name, email, phone,
                 qualification, designation, dept_id, joining_date)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                faculty_code,
                request.form['first_name'], request.form['last_name'],
                request.form['email'], request.form.get('phone',''),
                request.form.get('qualification',''), request.form.get('designation',''),
                request.form['dept_id'], request.form.get('joining_date','')
            ))
            db.execute_query(
                "INSERT OR IGNORE INTO users (username, password_hash, role, ref_id) VALUES (?,?,?,?)",
                (faculty_code, hash_password(faculty_code), 'faculty', fac_id)
            )
            flash(f'Faculty added! Code: {faculty_code}', 'success')
            return redirect(url_for('faculty_list'))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('add_faculty.html', departments=depts)

@app.route('/faculty/delete/<int:faculty_id>')
@login_required('admin')
def delete_faculty(faculty_id):
    try:
        db.execute_query("DELETE FROM faculty WHERE faculty_id=?", (faculty_id,))
        flash('Faculty deleted!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('faculty_list'))


# ── COURSES ─────────────────────────────────────
@app.route('/courses')
@login_required()
def courses():
    course_list = db.fetch_all("""
        SELECT c.*, d.dept_name, COUNT(e.enrollment_id) as enrolled_count
        FROM courses c
        JOIN departments d ON c.dept_id=d.dept_id
        LEFT JOIN enrollments e ON c.course_id=e.course_id
        GROUP BY c.course_id ORDER BY d.dept_name, c.semester
    """)
    return render_template('courses.html', courses=course_list)

@app.route('/courses/add', methods=['GET', 'POST'])
@login_required('admin')
def add_course():
    depts = db.fetch_all("SELECT * FROM departments ORDER BY dept_name")
    if request.method == 'POST':
        try:
            db.execute_query(
                "INSERT INTO courses (course_name, course_code, credits, dept_id, semester) VALUES (?,?,?,?,?)",
                (request.form['course_name'], request.form['course_code'],
                 request.form['credits'], request.form['dept_id'], request.form['semester'])
            )
            flash('Course added!', 'success')
            return redirect(url_for('courses'))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('add_course.html', departments=depts)

@app.route('/courses/delete/<int:course_id>')
@login_required('admin')
def delete_course(course_id):
    try:
        db.execute_query("DELETE FROM courses WHERE course_id=?", (course_id,))
        flash('Course deleted!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('courses'))


# ── ENROLLMENTS ──────────────────────────────────
@app.route('/enrollments', methods=['GET', 'POST'])
@login_required('admin')
def enrollments():
    if request.method == 'POST':
        try:
            db.execute_query(
                "INSERT INTO enrollments (student_id, course_id, academic_year, semester) VALUES (?,?,?,?)",
                (request.form['student_id'], request.form['course_id'],
                 request.form['academic_year'], request.form['semester'])
            )
            flash('Student enrolled!', 'success')
        except ValueError as e:
            flash(str(e), 'danger')
    enroll_list = db.fetch_all("""
        SELECT e.*, s.first_name||' '||s.last_name as student_name,
               s.enrollment_no, c.course_name, c.course_code, d.dept_name
        FROM enrollments e
        JOIN students s ON e.student_id=s.student_id
        JOIN courses c  ON e.course_id=c.course_id
        JOIN departments d ON s.dept_id=d.dept_id
        ORDER BY e.enrolled_on DESC
    """)
    students_list = db.fetch_all(
        "SELECT student_id, first_name||' '||last_name as name, enrollment_no FROM students WHERE status='Active'"
    )
    courses_list = db.fetch_all("SELECT course_id, course_name, course_code FROM courses")
    year = datetime.now().year
    return render_template('enrollments.html', enrollments=enroll_list,
                           students=students_list, courses=courses_list,
                           academic_year=f"{year}-{year+1}")

@app.route('/enrollments/delete/<int:enrollment_id>')
@login_required('admin')
def delete_enrollment(enrollment_id):
    try:
        db.execute_query("DELETE FROM enrollments WHERE enrollment_id=?", (enrollment_id,))
        flash('Enrollment deleted!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('enrollments'))


# ── GRADES ───────────────────────────────────────
@app.route('/grades', methods=['GET', 'POST'])
@login_required()
def grades():
    if request.method == 'POST' and session['role'] in ('admin', 'faculty'):
        marks = int(request.form['marks'])
        grade_row = db.fetch_one(
            "SELECT grade FROM grade_lookup WHERE ? BETWEEN min_marks AND max_marks", (marks,)
        )
        grade = grade_row['grade'] if grade_row else 'F'
        try:
            db.execute_query("""
                INSERT INTO grades (enrollment_id, marks_obtained, grade, remarks)
                VALUES (?,?,?,?)
                ON CONFLICT(enrollment_id) DO UPDATE SET
                    marks_obtained=excluded.marks_obtained,
                    grade=excluded.grade,
                    remarks=excluded.remarks
            """, (request.form['enrollment_id'], marks, grade, request.form.get('remarks','')))
            flash(f'Grade saved: {grade}', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')

    grades_list = db.fetch_all("""
        SELECT g.*, e.academic_year,
               s.first_name||' '||s.last_name as student_name, s.enrollment_no,
               c.course_name, c.course_code, gl.grade_point
        FROM grades g
        JOIN enrollments e ON g.enrollment_id=e.enrollment_id
        JOIN students s    ON e.student_id=s.student_id
        JOIN courses c     ON e.course_id=c.course_id
        LEFT JOIN grade_lookup gl ON g.grade=gl.grade
        ORDER BY g.recorded_on DESC
    """)
    enrollments_list = db.fetch_all("""
        SELECT e.enrollment_id,
               s.first_name||' '||s.last_name as student_name,
               s.enrollment_no, c.course_name, e.academic_year
        FROM enrollments e
        JOIN students s ON e.student_id=s.student_id
        JOIN courses c  ON e.course_id=c.course_id
        LEFT JOIN grades g ON e.enrollment_id=g.enrollment_id
        WHERE g.grade_id IS NULL
    """)
    return render_template('grades.html', grades=grades_list, enrollments=enrollments_list)

@app.route('/grades/delete/<int:grade_id>')
@login_required('admin')
def delete_grade(grade_id):
    try:
        db.execute_query("DELETE FROM grades WHERE grade_id=?", (grade_id,))
        flash('Grade deleted!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('grades'))


# ── REPORTS ──────────────────────────────────────
@app.route('/reports')
@login_required()
def reports():
    dept_stats = db.fetch_all("""
        SELECT d.dept_name, d.dept_code,
               COUNT(CASE WHEN s.status='Active'    THEN 1 END) as active,
               COUNT(CASE WHEN s.status='Graduated' THEN 1 END) as graduated
        FROM departments d
        LEFT JOIN students s ON d.dept_id=s.dept_id
        GROUP BY d.dept_id
    """)
    top_students = db.fetch_all("""
        SELECT s.first_name||' '||s.last_name as name,
               s.enrollment_no, d.dept_name,
               ROUND(SUM(c.credits * gl.grade_point) / SUM(c.credits), 2) as cgpa
        FROM enrollments e
        JOIN students s     ON e.student_id=s.student_id
        JOIN courses c      ON e.course_id=c.course_id
        JOIN departments d  ON s.dept_id=d.dept_id
        JOIN grades g       ON e.enrollment_id=g.enrollment_id
        JOIN grade_lookup gl ON g.grade=gl.grade
        GROUP BY s.student_id
        HAVING COUNT(g.grade_id) >= 1
        ORDER BY cgpa DESC LIMIT 10
    """)
    return render_template('reports.html', dept_stats=dept_stats, top_students=top_students)


# ── API ──────────────────────────────────────────
@app.route('/api/stats')
@login_required()
def api_stats():
    return jsonify({
        'students':    db.fetch_one("SELECT COUNT(*) as c FROM students")['c'],
        'faculty':     db.fetch_one("SELECT COUNT(*) as c FROM faculty")['c'],
        'courses':     db.fetch_one("SELECT COUNT(*) as c FROM courses")['c'],
        'enrollments': db.fetch_one("SELECT COUNT(*) as c FROM enrollments")['c'],
    })


# ══════════════════════════════════════════════
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)