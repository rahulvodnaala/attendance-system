import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import (
    get_overall_stats, get_all_students, get_all_faculty,
    get_departments, get_subjects, add_user, add_subject,
    assign_faculty_subject, get_connection,
    delete_student, delete_faculty, delete_subject, delete_assignment
)

C = {
    "admin":   "#4f46e5", "faculty": "#0284c7", "student": "#059669",
    "success": "#059669", "success_bg": "#ecfdf5", "success_b": "#a7f3d0",
    "warning": "#d97706", "warning_bg": "#fffbeb", "warning_b": "#fde68a",
    "danger":  "#dc2626", "danger_bg":  "#fef2f2", "danger_b":  "#fecaca",
    "text":    "#0f172a", "text2": "#475569", "muted": "#94a3b8",
    "border":  "#e2e6f0", "bg2": "#eaecf4",
}

def pcfg():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=C["muted"]),
        margin=dict(l=10, r=10, t=36, b=10)
    )

def section(title, color=None):
    dot_color = color or C["admin"]
    st.markdown(f"""
    <div class="section-header">
        <span class="section-dot" style="background:{dot_color}"></span>
        <h3>{title}</h3>
    </div>""", unsafe_allow_html=True)


def render_admin():
    st.markdown("""
    <div class="page-header">
        <h1>Admin Dashboard</h1>
        <p>System overview, student & faculty management</p>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Overview", "Students", "Faculty", "Subjects", "Assignments"])
    with tab1: _overview()
    with tab2: _students()
    with tab3: _faculty()
    with tab4: _subjects()
    with tab5: _assignments()


# ── Overview ──────────────────────────────────
def _overview():
    stats = get_overall_stats()
    cols  = st.columns(5)
    items = [
        ("Total Students",  stats["total_students"],  C["student"], "student-grad"),
        ("Faculty Members", stats["total_faculty"],   C["faculty"], "faculty-grad"),
        ("Subjects",        stats["total_subjects"],  C["admin"],   "admin-grad"),
        ("Sessions Held",   stats["total_sessions"],  "#7c3aed",    ""),
        ("Avg Attendance",  f"{stats['avg_attendance']}%",
         C["success"] if stats["avg_attendance"] >= 75 else C["warning"], ""),
    ]
    grad_map = {
        "student-grad": "linear-gradient(135deg,#059669,#0d9488)",
        "faculty-grad": "linear-gradient(135deg,#0284c7,#0891b2)",
        "admin-grad":   "linear-gradient(135deg,#4f46e5,#7c3aed)",
        "":             "linear-gradient(135deg,#7c3aed,#a855f7)",
    }
    for col, (label, val, color, grad_key) in zip(cols, items):
        bar = grad_map.get(grad_key, f"linear-gradient(135deg,{color},{color})")
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-bar" style="background:{bar}"></div>
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([3, 2])
    with cl: _trend_chart()
    with cr: _dept_chart()
    _low_att_table()


def _trend_chart():
    conn = get_connection()
    rows = conn.execute("""
        SELECT sess.date,
               COUNT(a.id) as total,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) as present
        FROM attendance_sessions sess
        LEFT JOIN attendance a ON a.session_id=sess.id
        GROUP BY sess.date ORDER BY sess.date LIMIT 30
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
        fill="tozeroy", fillcolor="rgba(79,70,229,0.07)",
        line=dict(color=C["admin"], width=2),
        mode="lines+markers", marker=dict(size=5, color=C["admin"]),
        hovertemplate="%{x}<br><b>%{y:.1f}%</b><extra></extra>"
    ))
    fig.add_hline(y=75, line_dash="dash", line_color=C["warning"],
                  annotation_text="75% minimum", annotation_font_color=C["warning"])
    fig.update_layout(**pcfg(), height=270,
        title=dict(text="Daily Attendance Trend", font=dict(size=12, color=C["text"])),
        yaxis=dict(range=[0,105], ticksuffix="%", gridcolor="rgba(0,0,0,0.04)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0.04)"), showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _dept_chart():
    conn = get_connection()
    rows = conn.execute("""
        SELECT d.code, COUNT(s.id) as cnt
        FROM departments d LEFT JOIN students s ON s.department_id=d.id
        GROUP BY d.id
    """).fetchall()
    conn.close()
    fig = go.Figure(go.Pie(
        labels=[r[0] for r in rows], values=[r[1] for r in rows], hole=0.6,
        marker=dict(colors=[C["admin"], C["faculty"], C["student"]]),
        hovertemplate="%{label}: %{value} students<extra></extra>"
    ))
    fig.update_layout(**pcfg(), height=270,
        title=dict(text="Students by Department", font=dict(size=12, color=C["text"])),
        showlegend=True, legend=dict(font=dict(color=C["muted"])))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _low_att_table():
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.name, s.roll_number,
               ROUND(CAST(SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS REAL) /
               NULLIF(COUNT(a.id),0) * 100, 1) as pct
        FROM students s JOIN users u ON s.user_id=u.id
        LEFT JOIN attendance a ON a.student_id=s.id
        GROUP BY s.id HAVING pct IS NOT NULL AND pct < 75
        ORDER BY pct ASC LIMIT 10
    """).fetchall()
    conn.close()
    if rows:
        section("Low Attendance — Below 75%", C["danger"])
        df = pd.DataFrame(rows, columns=["Student", "Roll No", "Attendance %"])
        df["Attendance %"] = df["Attendance %"].apply(lambda x: f"{x}%")
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── Students ──────────────────────────────────
def _students():
    section("Students", C["student"])
    c_add, c_list = st.columns([1, 2])

    with c_add:
        st.markdown(f"<p style='font-size:0.82rem;font-weight:700;color:{C['student']};margin-bottom:0.75rem'>Add New Student</p>", unsafe_allow_html=True)
        depts = get_departments()
        with st.form("add_student", clear_on_submit=True):
            name     = st.text_input("Full Name")
            email    = st.text_input("Email")
            roll     = st.text_input("Roll Number")
            dept     = st.selectbox("Department", ["Select department"] + [d["name"] for d in depts])
            semester = st.selectbox("Semester", list(range(1, 9)))
            section_ = st.selectbox("Section", ["A", "B", "C"])
            password = st.text_input("Password")
            if st.form_submit_button("Add Student", use_container_width=True):
                if dept == "Select department":
                    st.error("Please select a department.")
                elif not all([name, email, roll, password]):
                    st.error("All fields are required.")
                else:
                    dept_id = next(d["id"] for d in depts if d["name"] == dept)
                    ok, msg = add_user(name, email, password, "student",
                                       {"roll": roll, "dept_id": dept_id,
                                        "semester": semester, "section": section_})
                    st.success(msg) if ok else st.error(msg)

    with c_list:
        st.markdown(f"<p style='font-size:0.82rem;font-weight:700;color:{C['text2']};margin-bottom:0.75rem'>All Students</p>", unsafe_allow_html=True)
        students = get_all_students()
        if students:
            df = pd.DataFrame(students)
            df_show = df[["roll_number","name","dept","semester","section"]].copy()
            df_show.columns = ["Roll No","Name","Department","Sem","Section"]
            st.dataframe(df_show, use_container_width=True, hide_index=True)
            st.markdown(f"<p style='font-size:0.8rem;font-weight:600;color:{C['danger']};margin:0.75rem 0 0.3rem'>Delete Student</p>", unsafe_allow_html=True)
            opts = ["Select student"] + [f"{s['roll_number']} — {s['name']}" for s in students]
            sel  = st.selectbox("", opts, key="del_student_sel", label_visibility="collapsed")
            if sel != "Select student":
                if st.button("Delete Selected", key="del_student_btn"):
                    ok, msg = delete_student(students[opts.index(sel)-1]["id"])
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
        else:
            st.info("No students added yet.")


# ── Faculty ───────────────────────────────────
def _faculty():
    section("Faculty", C["faculty"])
    c_add, c_list = st.columns([1, 2])

    with c_add:
        st.markdown(f"<p style='font-size:0.82rem;font-weight:700;color:{C['faculty']};margin-bottom:0.75rem'>Add New Faculty</p>", unsafe_allow_html=True)
        depts = get_departments()
        with st.form("add_faculty", clear_on_submit=True):
            name     = st.text_input("Full Name")
            email    = st.text_input("Email")
            emp_id   = st.text_input("Employee ID")
            dept     = st.selectbox("Department", ["Select department"] + [d["name"] for d in depts])
            password = st.text_input("Password")
            if st.form_submit_button("Add Faculty", use_container_width=True):
                if dept == "Select department":
                    st.error("Please select a department.")
                elif not all([name, email, emp_id, password]):
                    st.error("All fields are required.")
                else:
                    dept_id = next(d["id"] for d in depts if d["name"] == dept)
                    ok, msg = add_user(name, email, password, "faculty",
                                       {"emp_id": emp_id, "dept_id": dept_id})
                    st.success(msg) if ok else st.error(msg)

    with c_list:
        st.markdown(f"<p style='font-size:0.82rem;font-weight:700;color:{C['text2']};margin-bottom:0.75rem'>All Faculty</p>", unsafe_allow_html=True)
        faculty = get_all_faculty()
        if faculty:
            df = pd.DataFrame(faculty)[["employee_id","name","dept","email"]]
            df.columns = ["Emp ID","Name","Department","Email"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown(f"<p style='font-size:0.8rem;font-weight:600;color:{C['danger']};margin:0.75rem 0 0.3rem'>Delete Faculty</p>", unsafe_allow_html=True)
            opts = ["Select faculty"] + [f"{f['employee_id']} — {f['name']}" for f in faculty]
            sel  = st.selectbox("", opts, key="del_fac_sel", label_visibility="collapsed")
            if sel != "Select faculty":
                if st.button("Delete Selected", key="del_fac_btn"):
                    ok, msg = delete_faculty(faculty[opts.index(sel)-1]["id"])
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
        else:
            st.info("No faculty added yet.")


# ── Subjects ──────────────────────────────────
def _subjects():
    section("Subjects", "#7c3aed")
    c_add, c_list = st.columns([1, 2])

    with c_add:
        st.markdown(f"<p style='font-size:0.82rem;font-weight:700;color:#7c3aed;margin-bottom:0.75rem'>Add New Subject</p>", unsafe_allow_html=True)
        depts = get_departments()
        with st.form("add_subject", clear_on_submit=True):
            name     = st.text_input("Subject Name")
            code     = st.text_input("Subject Code")
            dept     = st.selectbox("Department", ["Select department"] + [d["name"] for d in depts])
            semester = st.selectbox("Semester", list(range(1, 9)))
            credits  = st.selectbox("Credits", [1, 2, 3, 4, 5])
            if st.form_submit_button("Add Subject", use_container_width=True):
                if dept == "Select department":
                    st.error("Please select a department.")
                elif not all([name, code]):
                    st.error("Name and code are required.")
                else:
                    dept_id = next(d["id"] for d in depts if d["name"] == dept)
                    from database import add_subject as db_add
                    ok, msg = db_add(name, code, dept_id, semester, credits)
                    st.success(msg) if ok else st.error(msg)

    with c_list:
        st.markdown(f"<p style='font-size:0.82rem;font-weight:700;color:{C['text2']};margin-bottom:0.75rem'>All Subjects</p>", unsafe_allow_html=True)
        subjects = get_subjects()
        if subjects:
            df = pd.DataFrame(subjects)[["code","name","dept_name","semester","credits"]]
            df.columns = ["Code","Name","Department","Sem","Credits"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown(f"<p style='font-size:0.8rem;font-weight:600;color:{C['danger']};margin:0.75rem 0 0.3rem'>Delete Subject</p>", unsafe_allow_html=True)
            opts = ["Select subject"] + [f"{s['code']} — {s['name']}" for s in subjects]
            sel  = st.selectbox("", opts, key="del_sub_sel", label_visibility="collapsed")
            if sel != "Select subject":
                if st.button("Delete Selected", key="del_sub_btn"):
                    ok, msg = delete_subject(subjects[opts.index(sel)-1]["id"])
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
        else:
            st.info("No subjects added yet.")


# ── Assignments ───────────────────────────────
def _assignments():
    section("Assign Subject to Faculty", C["admin"])
    c_form, c_cur = st.columns([1, 1])

    with c_form:
        st.markdown(f"<p style='font-size:0.82rem;font-weight:700;color:{C['admin']};margin-bottom:0.75rem'>New Assignment</p>", unsafe_allow_html=True)
        faculty  = get_all_faculty()
        subjects = get_subjects()
        if not faculty or not subjects:
            st.warning("Add faculty and subjects first.")
            return
        with st.form("assign_form", clear_on_submit=True):
            fac_opts = ["Select faculty"] + [f["employee_id"] + " — " + f["name"] for f in faculty]
            sub_opts = ["Select subject"] + [s["code"] + " — " + s["name"] for s in subjects]
            sel_fac  = st.selectbox("Faculty", fac_opts)
            sel_sub  = st.selectbox("Subject", sub_opts)
            section_ = st.selectbox("Section", ["A", "B", "C"])
            if st.form_submit_button("Assign", use_container_width=True):
                if sel_fac == "Select faculty" or sel_sub == "Select subject":
                    st.error("Please select both faculty and subject.")
                else:
                    fi = fac_opts.index(sel_fac) - 1
                    si = sub_opts.index(sel_sub) - 1
                    ok, msg = assign_faculty_subject(faculty[fi]["id"], subjects[si]["id"], section_)
                    st.success("Assigned successfully.") if ok else st.error(msg)

    with c_cur:
        st.markdown(f"<p style='font-size:0.82rem;font-weight:700;color:{C['text2']};margin-bottom:0.75rem'>Current Assignments</p>", unsafe_allow_html=True)
        conn = get_connection()
        rows = conn.execute("""
            SELECT fs.id, u.name as faculty, s.code, s.name as subject, fs.section
            FROM faculty_subjects fs
            JOIN faculty f ON fs.faculty_id=f.id
            JOIN users u ON f.user_id=u.id
            JOIN subjects s ON fs.subject_id=s.id
            ORDER BY u.name
        """).fetchall()
        conn.close()
        if rows:
            assignments = [dict(r) for r in rows]
            df = pd.DataFrame(assignments)[["faculty","code","subject","section"]]
            df.columns = ["Faculty","Code","Subject","Section"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown(f"<p style='font-size:0.8rem;font-weight:600;color:{C['danger']};margin:0.75rem 0 0.3rem'>Remove Assignment</p>", unsafe_allow_html=True)
            opts = ["Select assignment"] + [f"{a['faculty']} / {a['code']} / Sec {a['section']}" for a in assignments]
            sel  = st.selectbox("", opts, key="del_assign_sel", label_visibility="collapsed")
            if sel != "Select assignment":
                if st.button("Remove Selected", key="del_assign_btn"):
                    ok, msg = delete_assignment(assignments[opts.index(sel)-1]["id"])
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
        else:
            st.info("No assignments yet.")
