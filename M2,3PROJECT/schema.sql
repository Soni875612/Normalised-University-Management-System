-- ============================================================
-- NORMALISED UNIVERSITY MANAGEMENT SYSTEM - DATABASE SCHEMA
-- Normal Forms: 1NF, 2NF, 3NF applied
-- ============================================================

PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. DEPARTMENTS TABLE (3NF - no transitive dependencies)
-- ============================================================
CREATE TABLE IF NOT EXISTS departments (
    dept_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    dept_name     TEXT NOT NULL UNIQUE,
    dept_code     TEXT NOT NULL UNIQUE,
    hod_name      TEXT,
    created_at    TEXT DEFAULT (datetime('now'))
);

-- ============================================================
-- 2. COURSES TABLE (3NF)
-- ============================================================
CREATE TABLE IF NOT EXISTS courses (
    course_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name   TEXT NOT NULL,
    course_code   TEXT NOT NULL UNIQUE,
    credits       INTEGER NOT NULL CHECK(credits BETWEEN 1 AND 6),
    dept_id       INTEGER NOT NULL,
    semester      INTEGER NOT NULL CHECK(semester BETWEEN 1 AND 8),
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE CASCADE
);

-- ============================================================
-- 3. STUDENTS TABLE (3NF - address separated, no partial deps)
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    student_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_no TEXT NOT NULL UNIQUE,
    first_name    TEXT NOT NULL,
    last_name     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    phone         TEXT,
    dob           TEXT,
    gender        TEXT CHECK(gender IN ('Male','Female','Other')),
    dept_id       INTEGER NOT NULL,
    semester      INTEGER NOT NULL CHECK(semester BETWEEN 1 AND 8),
    admission_year INTEGER NOT NULL,
    status        TEXT DEFAULT 'Active' CHECK(status IN ('Active','Inactive','Graduated')),
    created_at    TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
);

-- ============================================================
-- 4. STUDENT ADDRESSES (Separated for 1NF - no repeating groups)
-- ============================================================
CREATE TABLE IF NOT EXISTS student_addresses (
    address_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    INTEGER NOT NULL UNIQUE,
    street        TEXT,
    city          TEXT,
    state         TEXT,
    pincode       TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ============================================================
-- 5. FACULTY TABLE (3NF)
-- ============================================================
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
    status        TEXT DEFAULT 'Active' CHECK(status IN ('Active','Inactive')),
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
);

-- ============================================================
-- 6. COURSE ENROLLMENT (Junction Table - 2NF, resolves M:N)
-- ============================================================
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    INTEGER NOT NULL,
    course_id     INTEGER NOT NULL,
    academic_year TEXT NOT NULL,
    semester      INTEGER NOT NULL,
    enrolled_on   TEXT DEFAULT (datetime('now')),
    UNIQUE(student_id, course_id, academic_year),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- ============================================================
-- 7. GRADES TABLE (3NF - grade points in separate lookup)
-- ============================================================
CREATE TABLE IF NOT EXISTS grade_lookup (
    grade         TEXT PRIMARY KEY,
    grade_point   REAL NOT NULL,
    min_marks     INTEGER NOT NULL,
    max_marks     INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS grades (
    grade_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL UNIQUE,
    marks_obtained INTEGER,
    grade         TEXT,
    remarks       TEXT,
    recorded_on   TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id) ON DELETE CASCADE,
    FOREIGN KEY (grade) REFERENCES grade_lookup(grade)
);

-- ============================================================
-- 8. FACULTY COURSE ASSIGNMENT (Junction - resolves M:N)
-- ============================================================
CREATE TABLE IF NOT EXISTS faculty_courses (
    assign_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_id    INTEGER NOT NULL,
    course_id     INTEGER NOT NULL,
    academic_year TEXT NOT NULL,
    semester      INTEGER NOT NULL,
    UNIQUE(faculty_id, course_id, academic_year),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- ============================================================
-- 9. ATTENDANCE TABLE (3NF)
-- ============================================================
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL,
    date          TEXT NOT NULL,
    status        TEXT NOT NULL CHECK(status IN ('Present','Absent','Late')),
    UNIQUE(enrollment_id, date),
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id) ON DELETE CASCADE
);

-- ============================================================
-- 10. USERS TABLE (for login/auth)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK(role IN ('admin','faculty','student')),
    ref_id        INTEGER,
    is_active     INTEGER DEFAULT 1,
    created_at    TEXT DEFAULT (datetime('now'))
);

-- ============================================================
-- SEED DATA - Grade Lookup
-- ============================================================
INSERT OR IGNORE INTO grade_lookup VALUES ('O',  10.0, 90, 100);
INSERT OR IGNORE INTO grade_lookup VALUES ('A+',  9.0, 80, 89);
INSERT OR IGNORE INTO grade_lookup VALUES ('A',   8.0, 70, 79);
INSERT OR IGNORE INTO grade_lookup VALUES ('B+',  7.0, 60, 69);
INSERT OR IGNORE INTO grade_lookup VALUES ('B',   6.0, 50, 59);
INSERT OR IGNORE INTO grade_lookup VALUES ('C',   5.0, 40, 49);
INSERT OR IGNORE INTO grade_lookup VALUES ('F',   0.0,  0, 39);

-- SEED DATA - Sample Departments
INSERT OR IGNORE INTO departments (dept_name, dept_code, hod_name) VALUES
    ('Computer Science', 'CS', 'Dr. Ramesh Kumar'),
    ('Information Technology', 'IT', 'Dr. Priya Sharma'),
    ('Electronics', 'EC', 'Dr. Suresh Patel'),
    ('Mechanical Engineering', 'ME', 'Dr. Anjali Singh');

-- SEED DATA - Admin User (password: admin123)
INSERT OR IGNORE INTO users (username, password_hash, role) VALUES
    ('admin', 'pbkdf2:sha256:260000$admin123hashed', 'admin');