"""
Add Sample Data for Reports
Run this to populate the database with test data
"""

from app import db, hash_password
from datetime import datetime

print("🔧 Adding sample data for reports...\n")

# 1. Get existing students
students = db.fetch_all("SELECT student_id, first_name, last_name FROM students LIMIT 5")
print(f"✅ Found {len(students)} students")

# 2. Get existing courses
courses = db.fetch_all("SELECT course_id, course_name FROM courses LIMIT 3")
print(f"✅ Found {len(courses)} courses")

if not courses:
    print("⚠️  No courses found! Adding sample courses...")
    # Add sample courses
    db.execute_query(
        "INSERT INTO courses (course_name, course_code, credits, dept_id, semester) VALUES (?,?,?,?,?)",
        ("Data Structures", "CS301", 4, 1, 3)
    )
    db.execute_query(
        "INSERT INTO courses (course_name, course_code, credits, dept_id, semester) VALUES (?,?,?,?,?)",
        ("Database Systems", "CS401", 4, 1, 4)
    )
    courses = db.fetch_all("SELECT course_id, course_name FROM courses LIMIT 3")
    print(f"✅ Added {len(courses)} sample courses")

# 3. Enroll students in courses
print("\n🔧 Enrolling students in courses...")
academic_year = f"{datetime.now().year}-{datetime.now().year+1}"

for student in students:
    for course in courses[:2]:  # Enroll in 2 courses each
        try:
            enrollment_id = db.execute_query(
                "INSERT OR IGNORE INTO enrollments (student_id, course_id, academic_year, semester) VALUES (?,?,?,?)",
                (student['student_id'], course['course_id'], academic_year, 1)
            )
            if enrollment_id:
                print(f"   ✓ {student['first_name']} enrolled in {course['course_name']}")
        except:
            pass

# 4. Add grades for enrollments
print("\n🔧 Adding grades...")
enrollments = db.fetch_all("SELECT enrollment_id FROM enrollments")

import random
marks_list = [95, 88, 92, 85, 78, 90, 87, 82, 91, 89]

for i, e in enumerate(enrollments):
    marks = marks_list[i % len(marks_list)]
    
    # Determine grade based on marks
    if marks >= 90:
        grade = 'O'
    elif marks >= 80:
        grade = 'A+'
    elif marks >= 70:
        grade = 'A'
    elif marks >= 60:
        grade = 'B+'
    else:
        grade = 'B'
    
    try:
        db.execute_query(
            "INSERT OR IGNORE INTO grades (enrollment_id, marks_obtained, grade) VALUES (?,?,?)",
            (e['enrollment_id'], marks, grade)
        )
        print(f"   ✓ Grade added: {marks} ({grade})")
    except:
        pass

# 5. Verify data
print("\n📊 Verification:")
total_enrollments = db.fetch_one("SELECT COUNT(*) as c FROM enrollments")['c']
total_grades = db.fetch_one("SELECT COUNT(*) as c FROM grades")['c']
print(f"   Total Enrollments: {total_enrollments}")
print(f"   Total Grades: {total_grades}")

# 6. Check reports data
dept_stats = db.fetch_all("""
    SELECT d.dept_name, COUNT(s.student_id) as student_count
    FROM departments d
    LEFT JOIN students s ON d.dept_id=s.dept_id
    GROUP BY d.dept_id
""")

print(f"\n📈 Department Stats:")
for d in dept_stats:
    print(f"   {d['dept_name']}: {d['student_count']} students")

top_students = db.fetch_all("""
    SELECT s.first_name||' '||s.last_name as name,
           ROUND(AVG(g.marks_obtained), 2) as avg_marks
    FROM students s
    JOIN enrollments e ON s.student_id=e.student_id
    JOIN grades g ON e.enrollment_id=g.enrollment_id
    GROUP BY s.student_id
    ORDER BY avg_marks DESC
    LIMIT 5
""")

print(f"\n🏆 Top Performers:")
for t in top_students:
    print(f"   {t['name']}: {t['avg_marks']} marks")

print("\n✅ Sample data added successfully!")
print("🔄 Now refresh the Reports page in browser!")