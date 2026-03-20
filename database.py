import sqlite3
import hashlib
import os
from datetime import datetime, date

DB_PATH = "attendance.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'faculty', 'student')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Departments
    c.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL
        )
    """)

    # Student profiles
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            department_id INTEGER NOT NULL,
            semester INTEGER NOT NULL,
            section TEXT NOT NULL DEFAULT 'A',
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(department_id) REFERENCES departments(id)
        )
    """)

    # Faculty profiles
    c.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            employee_id TEXT UNIQUE NOT NULL,
            department_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(department_id) REFERENCES departments(id)
        )
    """)

    # Subjects
    c.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            department_id INTEGER NOT NULL,
            semester INTEGER NOT NULL,
            credits INTEGER DEFAULT 3,
            FOREIGN KEY(department_id) REFERENCES departments(id)
        )
    """)

    # Faculty-Subject assignment
    c.execute("""
        CREATE TABLE IF NOT EXISTS faculty_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            section TEXT DEFAULT 'A',
            academic_year TEXT DEFAULT '2024-25',
            UNIQUE(faculty_id, subject_id, section),
            FOREIGN KEY(faculty_id) REFERENCES faculty(id),
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        )
    """)

    # Attendance sessions (a class held on a date)
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            faculty_id INTEGER NOT NULL,
            date DATE NOT NULL,
            section TEXT DEFAULT 'A',
            topic TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(subject_id) REFERENCES subjects(id),
            FOREIGN KEY(faculty_id) REFERENCES faculty(id)
        )
    """)

    # Attendance records
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('present', 'absent', 'late')),
            marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, student_id),
            FOREIGN KEY(session_id) REFERENCES attendance_sessions(id),
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    conn.commit()

    # Seed default admin if not exists
    admin_email = "admin@college.edu"
    existing = c.execute("SELECT id FROM users WHERE email=?", (admin_email,)).fetchone()
    if not existing:
        _seed_demo_data(c)
        conn.commit()

    conn.close()

def _seed_demo_data(c):
    # Admin
    c.execute("INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
              ("Admin", "admin@college.edu", hash_password("admin123"), "admin"))

    # Departments
    depts = [
        ("Computer Science & Engineering", "CSE"),
        ("Electronics & Communication", "ECE"),
        ("Mechanical Engineering", "ME"),
    ]
    for name, code in depts:
        c.execute("INSERT INTO departments (name, code) VALUES (?,?)", (name, code))

    dept_cse = c.execute("SELECT id FROM departments WHERE code='CSE'").fetchone()[0]
    dept_ece = c.execute("SELECT id FROM departments WHERE code='ECE'").fetchone()[0]

    # Faculty
    c.execute("INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
              ("Dr. Priya Sharma", "priya@college.edu", hash_password("faculty123"), "faculty"))
    fac1_uid = c.lastrowid
    c.execute("INSERT INTO faculty (user_id, employee_id, department_id) VALUES (?,?,?)",
              (fac1_uid, "FAC001", dept_cse))

    c.execute("INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
              ("Prof. Rahul Gupta", "rahul@college.edu", hash_password("faculty123"), "faculty"))
    fac2_uid = c.lastrowid
    c.execute("INSERT INTO faculty (user_id, employee_id, department_id) VALUES (?,?,?)",
              (fac2_uid, "FAC002", dept_cse))

    fac1_id = c.execute("SELECT id FROM faculty WHERE user_id=?", (fac1_uid,)).fetchone()[0]
    fac2_id = c.execute("SELECT id FROM faculty WHERE user_id=?", (fac2_uid,)).fetchone()[0]

    # Subjects
    subjects = [
        ("Data Structures & Algorithms", "CS301", dept_cse, 3, 4),
        ("Database Management Systems", "CS302", dept_cse, 3, 4),
        ("Operating Systems", "CS303", dept_cse, 3, 4),
        ("Computer Networks", "CS401", dept_cse, 4, 4),
        ("Machine Learning", "CS402", dept_cse, 3, 4),
    ]
    for name, code, did, credits, sem in subjects:
        c.execute("INSERT INTO subjects (name, code, department_id, semester, credits) VALUES (?,?,?,?,?)",
                  (name, code, did, sem, credits))

    sub_ids = [c.execute("SELECT id FROM subjects WHERE code=?", (code,)).fetchone()[0]
               for _, code, _, _, _ in subjects]

    # Assign subjects to faculty
    c.execute("INSERT OR IGNORE INTO faculty_subjects (faculty_id, subject_id, section) VALUES (?,?,?)", (fac1_id, sub_ids[0], "A"))
    c.execute("INSERT OR IGNORE INTO faculty_subjects (faculty_id, subject_id, section) VALUES (?,?,?)", (fac1_id, sub_ids[1], "A"))
    c.execute("INSERT OR IGNORE INTO faculty_subjects (faculty_id, subject_id, section) VALUES (?,?,?)", (fac1_id, sub_ids[4], "A"))
    c.execute("INSERT OR IGNORE INTO faculty_subjects (faculty_id, subject_id, section) VALUES (?,?,?)", (fac2_id, sub_ids[2], "A"))
    c.execute("INSERT OR IGNORE INTO faculty_subjects (faculty_id, subject_id, section) VALUES (?,?,?)", (fac2_id, sub_ids[3], "A"))

    # Students
    students_data = [
        ("Arjun Kumar", "arjun@student.edu", "22CS001"),
        ("Sneha Patel", "sneha@student.edu", "22CS002"),
        ("Rohan Mehta", "rohan@student.edu", "22CS003"),
        ("Divya Singh", "divya@student.edu", "22CS004"),
        ("Karan Joshi", "karan@student.edu", "22CS005"),
    ]
    student_ids = []
    for name, email, roll in students_data:
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
                  (name, email, hash_password("student123"), "student"))
        uid = c.lastrowid
        c.execute("INSERT INTO students (user_id, roll_number, department_id, semester, section) VALUES (?,?,?,?,?)",
                  (uid, roll, dept_cse, 4, "A"))
        sid = c.execute("SELECT id FROM students WHERE user_id=?", (uid,)).fetchone()[0]
        student_ids.append(sid)

    # Sample attendance sessions & records
    import random
    from datetime import timedelta
    today = date.today()
    for sub_idx, sub_id in enumerate(sub_ids[:3]):
        fac_id = fac1_id if sub_idx < 3 else fac2_id
        for days_ago in range(20, 0, -1):
            d = today - timedelta(days=days_ago)
            if d.weekday() < 5:  # weekdays only
                c.execute("INSERT INTO attendance_sessions (subject_id, faculty_id, date, section, topic) VALUES (?,?,?,?,?)",
                          (sub_id, fac_id, d.isoformat(), "A", "Lecture"))
                sess_id = c.lastrowid
                for st_id in student_ids:
                    status = random.choices(["present", "absent", "late"], weights=[75, 20, 5])[0]
                    c.execute("INSERT OR IGNORE INTO attendance (session_id, student_id, status) VALUES (?,?,?)",
                              (sess_id, st_id, status))


# ──────────────────────────────────────────────────────
# Query helpers
# ──────────────────────────────────────────────────────

def authenticate(email: str, password: str):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_students(dept_id=None):
    conn = get_connection()
    q = """SELECT s.id, u.name, u.email, s.roll_number, d.name as dept, s.semester, s.section
           FROM students s JOIN users u ON s.user_id=u.id
           JOIN departments d ON s.department_id=d.id"""
    if dept_id:
        q += f" WHERE s.department_id={dept_id}"
    q += " ORDER BY s.roll_number"
    rows = [dict(r) for r in conn.execute(q).fetchall()]
    conn.close()
    return rows

def get_all_faculty():
    conn = get_connection()
    rows = conn.execute("""
        SELECT f.id, u.name, u.email, f.employee_id, d.name as dept
        FROM faculty f JOIN users u ON f.user_id=u.id
        JOIN departments d ON f.department_id=d.id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_departments():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM departments ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_subjects(dept_id=None, semester=None):
    conn = get_connection()
    q = "SELECT s.*, d.name as dept_name FROM subjects s JOIN departments d ON s.department_id=d.id WHERE 1=1"
    params = []
    if dept_id:
        q += " AND s.department_id=?"
        params.append(dept_id)
    if semester:
        q += " AND s.semester=?"
        params.append(semester)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_faculty_subjects(faculty_user_id: int):
    conn = get_connection()
    fac = conn.execute("SELECT id FROM faculty WHERE user_id=?", (faculty_user_id,)).fetchone()
    if not fac:
        return []
    rows = conn.execute("""
        SELECT fs.id as fs_id, s.id as subject_id, s.name, s.code, s.semester, d.name as dept,
               fs.section, fs.academic_year
        FROM faculty_subjects fs
        JOIN subjects s ON fs.subject_id=s.id
        JOIN departments d ON s.department_id=d.id
        WHERE fs.faculty_id=?
    """, (fac[0],)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_students_for_subject(subject_id: int, section: str):
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.id, u.name, s.roll_number, s.semester, s.section
        FROM students s JOIN users u ON s.user_id=u.id
        JOIN subjects sub ON sub.id=?
        WHERE s.department_id = sub.department_id
          AND s.semester = sub.semester
          AND s.section = ?
        ORDER BY s.roll_number
    """, (subject_id, section)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_faculty_id(user_id: int):
    conn = get_connection()
    row = conn.execute("SELECT id FROM faculty WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row[0] if row else None

def get_student_profile(user_id: int):
    conn = get_connection()
    row = conn.execute("""
        SELECT s.*, u.name, u.email, d.name as dept_name
        FROM students s JOIN users u ON s.user_id=u.id
        JOIN departments d ON s.department_id=d.id
        WHERE s.user_id=?
    """, (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def session_exists(subject_id, faculty_id, date_str, section):
    conn = get_connection()
    row = conn.execute("""
        SELECT id FROM attendance_sessions
        WHERE subject_id=? AND faculty_id=? AND date=? AND section=?
    """, (subject_id, faculty_id, date_str, section)).fetchone()
    conn.close()
    return row[0] if row else None

def create_attendance_session(subject_id, faculty_id, date_str, section, topic=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO attendance_sessions (subject_id, faculty_id, date, section, topic)
        VALUES (?,?,?,?,?)
    """, (subject_id, faculty_id, date_str, section, topic))
    sess_id = c.lastrowid
    conn.commit()
    conn.close()
    return sess_id

def mark_attendance(session_id, student_id, status):
    conn = get_connection()
    conn.execute("""
        INSERT INTO attendance (session_id, student_id, status)
        VALUES (?,?,?)
        ON CONFLICT(session_id, student_id) DO UPDATE SET status=excluded.status
    """, (session_id, student_id, status))
    conn.commit()
    conn.close()

def get_attendance_for_session(session_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.student_id, a.status, u.name, s.roll_number
        FROM attendance a
        JOIN students s ON a.student_id=s.id
        JOIN users u ON s.user_id=u.id
        WHERE a.session_id=?
    """, (session_id,)).fetchall()
    conn.close()
    return {r["student_id"]: dict(r) for r in rows}

def get_subject_attendance_summary(subject_id, section):
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.name, s.roll_number,
               COUNT(a.id) as total_classes,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) as present,
               SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) as absent,
               SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) as late
        FROM students s
        JOIN users u ON s.user_id=u.id
        JOIN subjects sub ON sub.id=?
        LEFT JOIN attendance_sessions sess ON sess.subject_id=sub.id AND sess.section=?
        LEFT JOIN attendance a ON a.session_id=sess.id AND a.student_id=s.id
        WHERE s.department_id=sub.department_id AND s.semester=sub.semester AND s.section=?
        GROUP BY s.id, u.name, s.roll_number
        ORDER BY s.roll_number
    """, (subject_id, section, section)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_student_attendance_summary(student_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT sub.name as subject, sub.code,
               COUNT(sess.id) as total_classes,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) as present,
               SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) as absent,
               SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) as late
        FROM subjects sub
        JOIN attendance_sessions sess ON sess.subject_id=sub.id
        LEFT JOIN attendance a ON a.session_id=sess.id AND a.student_id=?
        JOIN students st ON st.id=?
        WHERE sub.department_id=st.department_id AND sub.semester=st.semester
        GROUP BY sub.id, sub.name, sub.code
        ORDER BY sub.name
    """, (student_id, student_id)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_overall_stats():
    conn = get_connection()
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_faculty = conn.execute("SELECT COUNT(*) FROM faculty").fetchone()[0]
    total_sessions = conn.execute("SELECT COUNT(*) FROM attendance_sessions").fetchone()[0]
    total_subjects = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]

    avg_attendance = conn.execute("""
        SELECT AVG(pct) FROM (
            SELECT
                CAST(SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) AS REAL) /
                NULLIF(COUNT(*), 0) * 100 as pct
            FROM attendance
        )
    """).fetchone()[0] or 0

    conn.close()
    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_sessions": total_sessions,
        "total_subjects": total_subjects,
        "avg_attendance": round(avg_attendance, 1)
    }

def get_sessions_for_subject(subject_id, section):
    conn = get_connection()
    rows = conn.execute("""
        SELECT sess.id, sess.date, sess.topic, u.name as faculty_name,
               COUNT(a.id) as total_marked,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) as present_count
        FROM attendance_sessions sess
        JOIN faculty f ON sess.faculty_id=f.id
        JOIN users u ON f.user_id=u.id
        LEFT JOIN attendance a ON a.session_id=sess.id
        WHERE sess.subject_id=? AND sess.section=?
        GROUP BY sess.id
        ORDER BY sess.date DESC
    """, (subject_id, section)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_user(name, email, password, role, extra=None):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
                  (name, email, hash_password(password), role))
        uid = c.lastrowid
        if role == "student" and extra:
            c.execute("INSERT INTO students (user_id, roll_number, department_id, semester, section) VALUES (?,?,?,?,?)",
                      (uid, extra["roll"], extra["dept_id"], extra["semester"], extra.get("section", "A")))
        elif role == "faculty" and extra:
            c.execute("INSERT INTO faculty (user_id, employee_id, department_id) VALUES (?,?,?)",
                      (uid, extra["emp_id"], extra["dept_id"]))
        conn.commit()
        return True, "User added successfully"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def add_subject(name, code, dept_id, semester, credits):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO subjects (name, code, department_id, semester, credits) VALUES (?,?,?,?,?)",
                     (name, code, dept_id, semester, credits))
        conn.commit()
        return True, "Subject added"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def assign_faculty_subject(faculty_id, subject_id, section):
    conn = get_connection()
    try:
        conn.execute("INSERT OR IGNORE INTO faculty_subjects (faculty_id, subject_id, section) VALUES (?,?,?)",
                     (faculty_id, subject_id, section))
        conn.commit()
        return True, "Assigned"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_student(student_id):
    conn = get_connection()
    try:
        # Delete attendance records first
        conn.execute("""DELETE FROM attendance WHERE student_id=?""", (student_id,))
        user_id = conn.execute("SELECT user_id FROM students WHERE id=?", (student_id,)).fetchone()
        conn.execute("DELETE FROM students WHERE id=?", (student_id,))
        if user_id:
            conn.execute("DELETE FROM users WHERE id=?", (user_id[0],))
        conn.commit()
        return True, "Student deleted"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_faculty(faculty_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM faculty_subjects WHERE faculty_id=?", (faculty_id,))
        user_id = conn.execute("SELECT user_id FROM faculty WHERE id=?", (faculty_id,)).fetchone()
        conn.execute("DELETE FROM faculty WHERE id=?", (faculty_id,))
        if user_id:
            conn.execute("DELETE FROM users WHERE id=?", (user_id[0],))
        conn.commit()
        return True, "Faculty deleted"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_subject(subject_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM faculty_subjects WHERE subject_id=?", (subject_id,))
        # delete attendance for sessions of this subject
        sessions = conn.execute("SELECT id FROM attendance_sessions WHERE subject_id=?", (subject_id,)).fetchall()
        for s in sessions:
            conn.execute("DELETE FROM attendance WHERE session_id=?", (s[0],))
        conn.execute("DELETE FROM attendance_sessions WHERE subject_id=?", (subject_id,))
        conn.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
        conn.commit()
        return True, "Subject deleted"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_assignment(fs_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM faculty_subjects WHERE id=?", (fs_id,))
        conn.commit()
        return True, "Assignment removed"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_session_topic(session_id, topic):
    conn = get_connection()
    conn.execute("UPDATE attendance_sessions SET topic=? WHERE id=?", (topic, session_id))
    conn.commit()
    conn.close()

def get_student_detailed_attendance(student_id, subject_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT sess.date, a.status, sess.topic
        FROM attendance_sessions sess
        LEFT JOIN attendance a ON a.session_id=sess.id AND a.student_id=?
        WHERE sess.subject_id=?
        ORDER BY sess.date DESC
    """, (student_id, subject_id)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
