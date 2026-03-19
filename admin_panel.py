import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from database import (
    get_overall_stats, get_all_students, get_all_faculty,
    get_departments, get_subjects, add_user, add_subject,
    assign_faculty_subject, get_faculty_id, get_faculty_subjects
)

# ── Color palette ──
COLORS = {
    "accent": "#6366f1", "accent2": "#8b5cf6", "accent3": "#06b6d4",
    "success": "#10b981", "warning": "#f59e0b", "danger": "#ef4444",
    "bg": "#111827", "bg2": "#1a2236", "text": "#f1f5f9", "text2": "#94a3b8"
}

def plot_cfg():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color=COLORS["text2"]),
        margin=dict(l=10, r=10, t=30, b=10)
    )

def render_admin():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">Admin Panel</div>
        <p class="hero-title">📊 System Dashboard</p>
        <p class="hero-subtitle">Manage students, faculty, subjects & attendance overview</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", "🎓 Students", "👩‍🏫 Faculty", "📚 Subjects", "⚙️ Assign"
    ])

    with tab1:
        _render_overview()
    with tab2:
        _render_students()
    with tab3:
        _render_faculty()
    with tab4:
        _render_subjects()
    with tab5:
        _render_assign()


def _render_overview():
    stats = get_overall_stats()

    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        (col1, "🎓", stats["total_students"], "Students"),
        (col2, "👩‍🏫", stats["total_faculty"], "Faculty"),
        (col3, "📚", stats["total_subjects"], "Subjects"),
        (col4, "📋", stats["total_sessions"], "Sessions Held"),
        (col5, "📊", f"{stats['avg_attendance']}%", "Avg Attendance"),
    ]
    for col, icon, val, label in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        _attendance_trend_chart()

    with col_right:
        _dept_distribution_chart()

    _low_attendance_alert()


def _attendance_trend_chart():
    import sqlite3
    from database import get_connection
    conn = get_connection()
    rows = conn.execute("""
        SELECT sess.date,
               COUNT(a.id) as total,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) as present
        FROM attendance_sessions sess
        LEFT JOIN attendance a ON a.session_id=sess.id
        GROUP BY sess.date
        ORDER BY sess.date
        LIMIT 30
    """).fetchall()
    conn.close()

    if not rows:
        st.info("No attendance data yet.")
        return

    df = pd.DataFrame(rows, columns=["date", "total", "present"])
    df["pct"] = (df["present"] / df["total"].replace(0, 1) * 100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["pct"],
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.08)",
        line=dict(color=COLORS["accent"], width=2.5),
        mode="lines+markers",
        marker=dict(color=COLORS["accent2"], size=6),
        name="Attendance %",
        hovertemplate="%{x}<br><b>%{y:.1f}%</b><extra></extra>"
    ))
    fig.add_hline(y=75, line_dash="dash", line_color=COLORS["warning"],
                  annotation_text="75% Threshold", annotation_font_color=COLORS["warning"])
    fig.update_layout(
        **plot_cfg(),
        title=dict(text="📈 Daily Attendance Trend", font=dict(size=14, color=COLORS["text"])),
        yaxis=dict(range=[0, 105], gridcolor="rgba(255,255,255,0.05)", ticksuffix="%"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        showlegend=False,
        height=280
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _dept_distribution_chart():
    from database import get_connection
    conn = get_connection()
    rows = conn.execute("""
        SELECT d.name, COUNT(s.id) as cnt
        FROM departments d
        LEFT JOIN students s ON s.department_id=d.id
        GROUP BY d.id
    """).fetchall()
    conn.close()

    labels = [r[0].replace("&", "&").split(" ")[0] for r in rows]
    values = [r[1] for r in rows]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.6,
        marker=dict(colors=[COLORS["accent"], COLORS["accent2"], COLORS["accent3"]]),
        textfont=dict(color=COLORS["text"]),
        hovertemplate="%{label}<br><b>%{value} students</b><extra></extra>"
    ))
    fig.update_layout(
        **plot_cfg(),
        title=dict(text="🏫 Students by Dept", font=dict(size=14, color=COLORS["text"])),
        showlegend=True,
        legend=dict(font=dict(color=COLORS["text2"])),
        height=280
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _low_attendance_alert():
    from database import get_connection
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.name, s.roll_number,
               CAST(SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS REAL) /
               NULLIF(COUNT(a.id),0) * 100 as pct
        FROM students s
        JOIN users u ON s.user_id=u.id
        LEFT JOIN attendance a ON a.student_id=s.id
        GROUP BY s.id
        HAVING pct IS NOT NULL AND pct < 75
        ORDER BY pct ASC
        LIMIT 10
    """).fetchall()
    conn.close()

    if rows:
        st.markdown("""
        <div class="section-header">
            <h3>🚨 Low Attendance Alert (&lt;75%)</h3>
        </div>
        """, unsafe_allow_html=True)
        df = pd.DataFrame(rows, columns=["Student", "Roll No", "Attendance %"])
        df["Attendance %"] = df["Attendance %"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df, use_container_width=True, hide_index=True)


def _render_students():
    st.markdown("""<div class="section-header"><h3>🎓 Student Management</h3></div>""",
                unsafe_allow_html=True)

    col_add, col_list = st.columns([1, 2])

    with col_add:
        st.markdown("**Add New Student**")
        with st.form("add_student_form", clear_on_submit=True):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            roll = st.text_input("Roll Number")
            depts = get_departments()
            dept = st.selectbox("Department", [d["name"] for d in depts])
            semester = st.selectbox("Semester", list(range(1, 9)))
            section = st.selectbox("Section", ["A", "B", "C"])
            password = st.text_input("Password", value="student123")

            if st.form_submit_button("➕ Add Student", use_container_width=True):
                dept_id = next(d["id"] for d in depts if d["name"] == dept)
                ok, msg = add_user(name, email, password, "student",
                                   {"roll": roll, "dept_id": dept_id, "semester": semester, "section": section})
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

    with col_list:
        st.markdown("**All Students**")
        students = get_all_students()
        if students:
            df = pd.DataFrame(students)[["roll_number", "name", "dept", "semester", "section"]]
            df.columns = ["Roll No", "Name", "Department", "Sem", "Section"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No students found.")


def _render_faculty():
    st.markdown("""<div class="section-header"><h3>👩‍🏫 Faculty Management</h3></div>""",
                unsafe_allow_html=True)

    col_add, col_list = st.columns([1, 2])

    with col_add:
        st.markdown("**Add New Faculty**")
        with st.form("add_faculty_form", clear_on_submit=True):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            emp_id = st.text_input("Employee ID")
            depts = get_departments()
            dept = st.selectbox("Department", [d["name"] for d in depts])
            password = st.text_input("Password", value="faculty123")

            if st.form_submit_button("➕ Add Faculty", use_container_width=True):
                dept_id = next(d["id"] for d in depts if d["name"] == dept)
                ok, msg = add_user(name, email, password, "faculty",
                                   {"emp_id": emp_id, "dept_id": dept_id})
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

    with col_list:
        st.markdown("**All Faculty**")
        faculty = get_all_faculty()
        if faculty:
            df = pd.DataFrame(faculty)[["employee_id", "name", "dept", "email"]]
            df.columns = ["Emp ID", "Name", "Department", "Email"]
            st.dataframe(df, use_container_width=True, hide_index=True)


def _render_subjects():
    st.markdown("""<div class="section-header"><h3>📚 Subject Management</h3></div>""",
                unsafe_allow_html=True)

    col_add, col_list = st.columns([1, 2])

    with col_add:
        st.markdown("**Add New Subject**")
        with st.form("add_subject_form", clear_on_submit=True):
            name = st.text_input("Subject Name")
            code = st.text_input("Subject Code")
            depts = get_departments()
            dept = st.selectbox("Department", [d["name"] for d in depts])
            semester = st.selectbox("Semester", list(range(1, 9)))
            credits = st.selectbox("Credits", [1, 2, 3, 4, 5])

            if st.form_submit_button("➕ Add Subject", use_container_width=True):
                dept_id = next(d["id"] for d in depts if d["name"] == dept)
                ok, msg = add_subject(name, code, dept_id, semester, credits)
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

    with col_list:
        st.markdown("**All Subjects**")
        subjects = get_subjects()
        if subjects:
            df = pd.DataFrame(subjects)[["code", "name", "dept_name", "semester", "credits"]]
            df.columns = ["Code", "Name", "Department", "Sem", "Credits"]
            st.dataframe(df, use_container_width=True, hide_index=True)


def _render_assign():
    st.markdown("""<div class="section-header"><h3>⚙️ Assign Subject to Faculty</h3></div>""",
                unsafe_allow_html=True)

    col_form, col_current = st.columns([1, 1])

    with col_form:
        st.markdown("**New Assignment**")
        faculty = get_all_faculty()
        subjects = get_subjects()

        if not faculty or not subjects:
            st.warning("Add faculty and subjects first.")
            return

        with st.form("assign_form", clear_on_submit=True):
            fac_names = [f"{f['employee_id']} - {f['name']}" for f in faculty]
            sub_names = [f"{s['code']} - {s['name']}" for s in subjects]

            sel_fac = st.selectbox("Faculty", fac_names)
            sel_sub = st.selectbox("Subject", sub_names)
            section = st.selectbox("Section", ["A", "B", "C"])

            if st.form_submit_button("✅ Assign", use_container_width=True):
                fac_idx = fac_names.index(sel_fac)
                sub_idx = sub_names.index(sel_sub)
                ok, msg = assign_faculty_subject(faculty[fac_idx]["id"], subjects[sub_idx]["id"], section)
                if ok:
                    st.success("✅ Assigned successfully!")
                else:
                    st.error(f"❌ {msg}")

    with col_current:
        st.markdown("**Current Assignments**")
        from database import get_connection
        conn = get_connection()
        rows = conn.execute("""
            SELECT u.name as faculty, s.code, s.name as subject, fs.section
            FROM faculty_subjects fs
            JOIN faculty f ON fs.faculty_id=f.id
            JOIN users u ON f.user_id=u.id
            JOIN subjects s ON fs.subject_id=s.id
            ORDER BY u.name
        """).fetchall()
        conn.close()
        if rows:
            df = pd.DataFrame(rows, columns=["Faculty", "Code", "Subject", "Section"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No assignments yet.")
