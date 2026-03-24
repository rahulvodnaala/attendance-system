# 📊 AttendAI — Smart Attendance Management System
### BTech UG Minor Project | Streamlit + SQLite + AI Powered

---

## 🚀 Quick Start (3 Steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py

# 3. Open browser → http://localhost:8501
```

---

## 🔐 Demo Login Credentials

| Role    | Email                    | Password     |
|---------|--------------------------|--------------|
| Admin   | admin@college.edu        | Admin@2026#Secure     |
| Faculty | priya@college.edu        | Faculty@2026#Secure   |
| Faculty | rahul@college.edu        | Faculty@2026#Secure   |
| Student | arjun@student.edu        | Student@2026#Secure   |
| Student | sneha@student.edu        | Student@2026#Secure   |

---

## 📁 Project Structure

```
attendance_system/
├── app.py              ← Main entry point (routing + login)
├── database.py         ← SQLite DB schema + all queries
├── styles.py           ← Custom CSS (dark theme)
├── admin_panel.py      ← Admin dashboard
├── faculty_panel.py    ← Faculty: mark + view attendance
├── student_panel.py    ← Student: view own attendance
├── requirements.txt    ← Python dependencies
└── attendance.db       ← Auto-created SQLite database
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────┐
│              Streamlit Frontend              │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
│  │  Admin   │ │ Faculty  │ │   Student   │ │
│  │ Dashboard│ │  Panel   │ │   Portal    │ │
│  └────┬─────┘ └────┬─────┘ └──────┬──────┘ │
└───────┼────────────┼──────────────┼─────────┘
        │            │              │
┌───────▼────────────▼──────────────▼─────────┐
│              database.py (ORM Layer)         │
│        SQLite Queries + Business Logic       │
└───────────────────────┬─────────────────────┘
                        │
               ┌────────▼────────┐
               │  attendance.db  │
               │   (SQLite DB)   │
               └─────────────────┘
```

---

## ✨ Features

### 👨‍💼 Admin
- View system-wide dashboard with charts
- Add/manage students, faculty, departments, subjects
- Assign subjects to faculty
- See low attendance alerts (< 75%)
- View daily attendance trends

### 👩‍🏫 Faculty
- Mark subject-wise attendance (Present / Absent / Late)
- Mark for specific date (edit past sessions too)
- Add lecture topic notes
- View per-subject attendance reports with charts
- Download CSV reports
- Session history view

### 🎓 Student
- View overall and per-subject attendance %
- Radar chart across all subjects
- Classes needed to reach 75% calculator
- Subject-wise detailed timeline
- Monthly calendar view (color-coded)

---

## 🗃️ Database Schema

```
users          → id, name, email, password (hashed), role
departments    → id, name, code
students       → id, user_id, roll_number, dept_id, semester, section
faculty        → id, user_id, employee_id, dept_id
subjects       → id, name, code, dept_id, semester, credits
faculty_subjects → faculty_id, subject_id, section (assignments)
attendance_sessions → id, subject_id, faculty_id, date, section, topic
attendance     → session_id, student_id, status (present/absent/late)
```

---

## 🤖 AI Integration (Extend This!)

Add Gemini API for intelligent features:

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_GEMINI_KEY")
model = genai.GenerativeModel("gemini-pro")

def generate_ai_insight(attendance_data: str) -> str:
    prompt = f"""
    Analyze this student attendance data and give:
    1. Key insights (2-3 points)
    2. Risk assessment
    3. Recommendations
    
    Data: {attendance_data}
    """
    return model.generate_content(prompt).text
```

Add to requirements: `google-generativeai`

---

## 📊 Technologies Used

| Technology | Purpose |
|------------|---------|
| **Streamlit** | Web UI framework |
| **SQLite** | Lightweight database |
| **Pandas** | Data manipulation |
| **Plotly** | Interactive charts |
| **bcrypt** | Strong password hashing |
| **Gemini API** (optional) | AI insights |

---

## 🎓 Project Presentation Points

1. **Problem Statement** — Manual attendance is error-prone & slow
2. **Solution** — Digital, subject-wise, real-time tracking
3. **Tech Stack** — Pure Python, no heavy backend needed
4. **Database Design** — Normalized relational schema
5. **Role-Based Access** — Admin, Faculty, Student
6. **Analytics** — Charts, trends, low-attendance alerts
7. **AI Ready** — Easy to plug in LLM for insights
8. **Scalable** — Can switch to PostgreSQL for production

---

*Built as a BTech UG Minor Project*
