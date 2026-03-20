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
    "text": "#1a1a1a", "text2": "#5a5652", "muted": "#8a8680",
    "success": "#2d6a4f", "warning": "#8b5e00", "danger": "#922b21",
    "border": "#e5e2db", "bg2": "#f9f8f6", "bg3": "#f2f0ec",
}

def pcfg():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=C["muted"]),
        margin=dict(l=10, r=10, t=36, b=10)
    )


def render_admin():
    st.markdown("""
    <div class="page-header">
        <h1>Dashboard</h1>
        <p>System overview and management</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", "Students", "Faculty", "Subjects", "Assignments"
    ])
    with tab1: _overview()
    with tab2: _students()
    with tab3: _faculty()
    with tab4: _subjects()
    with tab5: _assignments()


# ── Overview ──────────────────────────────────
def _overview():
    stats = get_overall_stats()
    cols = st.columns(5)
    items = [
        ("Total Students",   stats["total_students"]),
        ("Faculty Members",  stats["total_faculty"]),
        ("Subjects",         stats["total_subjects"]),
        ("Sessions Held",    stats["total_sessions"]),
        ("Avg Attendance",   f"{stats['avg_attendance']}%"),
    ]
    for col, (label, val) in zip(cols, items):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

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
        fill="tozeroy", fillcolor="rgba(26,26,26,0.05)",
        line=dict(color=C["text"], width=1.5),
        mode="lines+markers", marker=dict(size=4, color=C["text"]),
        hovertemplate="%{x}<br><b>%{y:.1f}%</b><extra></extra>"
    ))
    fig.add_hline(y=75, line_dash="dash", line_color=C["warning"],
                  annotation_text="75%", annotation_font_color=C["warning"])
    fig.update_layout(**pcfg(), height=260,
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
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.6,
        marker=dict(colors=["#1a1a1a", "#5a5652", "#8a8680"]),
        hovertemplate="%{label}: %{value} students<extra></extra>"
    ))
    fig.update_layout(**pcfg(), height=260,
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
        st.markdown("""<div class="section-header"><h3>Low Attendance — Below 75%</h3></div>""",
                    unsafe_allow_html=True)
        df = pd.DataFrame(rows, columns=["Student", "Roll No", "Attendance %"])
        df["Attendance %"] = df["Attendance %"].apply(lambda x: f"{x}%")
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── Students ──────────────────────────────────
def _students():
    st.markdown("""<div class="section-header"><h3>Students</h3></div>""", unsafe_allow_html=True)
    c_add, c_list = st.columns([1, 2])

    with c_add:
        st.markdown("**Add Student**")
        depts = get_departments()
        with st.form("add_student", clear_on_submit=True):
            name     = st.text_input("Full Name")
            email    = st.text_input("Email")
            roll     = st.text_input("Roll Number")
            dept     = st.selectbox("Department", ["Select department"] + [d["name"] for d in depts])
            semester = st.selectbox("Semester", list(range(1, 9)))
            section  = st.selectbox("Section", ["A", "B", "C"])
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
                                        "semester": semester, "section": section})
                    st.success(msg) if ok else st.error(msg)

    with c_list:
        st.markdown("**All Students**")
        students = get_all_students()
        if students:
            df = pd.DataFrame(students)
            df_show = df[["roll_number", "name", "dept", "semester", "section"]].copy()
            df_show.columns = ["Roll No", "Name", "Department", "Sem", "Section"]
            st.dataframe(df_show, use_container_width=True, hide_index=True)

            st.markdown("**Delete Student**")
            opts = ["Select student"] + [f"{s['roll_number']} — {s['name']}" for s in students]
            sel = st.selectbox("", opts, key="del_student_sel", label_visibility="collapsed")
            if sel != "Select student":
                idx = opts.index(sel) - 1
                if st.button("Delete Selected Student", key="del_student_btn"):
                    ok, msg = delete_student(students[idx]["id"])
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
        else:
            st.info("No students added yet.")


# ── Faculty ───────────────────────────────────
def _faculty():
    st.markdown("""<div class="section-header"><h3>Faculty</h3></div>""", unsafe_allow_html=True)
    c_add, c_list = st.columns([1, 2])

    with c_add:
        st.markdown("**Add Faculty**")
        depts = get_departments()
        with st.form("add_faculty", clear_on_submit=True):
            name    = st.text_input("Full Name")
            email   = st.text_input("Email")
            emp_id  = st.text_input("Employee ID")
            dept    = st.selectbox("Department", ["Select department"] + [d["name"] for d in depts])
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
        st.markdown("**All Faculty**")
        faculty = get_all_faculty()
        if faculty:
            df = pd.DataFrame(faculty)[["employee_id", "name", "dept", "email"]]
            df.columns = ["Emp ID", "Name", "Department", "Email"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("**Delete Faculty**")
            opts = ["Select faculty"] + [f"{f['employee_id']} — {f['name']}" for f in faculty]
            sel = st.selectbox("", opts, key="del_fac_sel", label_visibility="collapsed")
            if sel != "Select faculty":
                idx = opts.index(sel) - 1
                if st.button("Delete Selected Faculty", key="del_fac_btn"):
                    ok, msg = delete_faculty(faculty[idx]["id"])
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
        else:
            st.info("No faculty added yet.")


# ── Subjects ──────────────────────────────────
def _subjects():
    st.markdown("""<div class="section-header"><h3>Subjects</h3></div>""", unsafe_allow_html=True)
    c_add, c_list = st.columns([1, 2])

    with c_add:
        st.markdown("**Add Subject**")
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
                    from database import add_subject as db_add_subject
                    ok, msg = db_add_subject(name, code, dept_id, semester, credits)
                    st.success(msg) if ok else st.error(msg)

    with c_list:
        st.markdown("**All Subjects**")
        subjects = get_subjects()
        if subjects:
            df = pd.DataFrame(subjects)[["code", "name", "dept_name", "semester", "credits"]]
            df.columns = ["Code", "Name", "Department", "Sem", "Credits"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("**Delete Subject**")
            opts = ["Select subject"] + [f"{s['code']} — {s['name']}" for s in subjects]
            sel = st.selectbox("", opts, key="del_sub_sel", label_visibility="collapsed")
            if sel != "Select subject":
                idx = opts.index(sel) - 1
                if st.button("Delete Selected Subject", key="del_sub_btn"):
                    ok, msg = delete_subject(subjects[idx]["id"])
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
        else:
            st.info("No subjects added yet.")


# ── Assignments ───────────────────────────────
def _assignments():
    st.markdown("""<div class="section-header"><h3>Assign Subject to Faculty</h3></div>""",
                unsafe_allow_html=True)
    c_form, c_cur = st.columns([1, 1])

    with c_form:
        st.markdown("**New Assignment**")
        faculty  = get_all_faculty()
        subjects = get_subjects()

        if not faculty or not subjects:
            st.warning("Add faculty and subjects first.")
            return

        with st.form("assign_form", clear_on_submit=True):
            fac_opts = ["Select faculty"] + [f["employee_id"] + " — " + f["name"] for f in faculty]
            sub_opts = ["Select subject"] + [s["code"] + " — " + s["name"] for s in subjects]

            sel_fac = st.selectbox("Faculty", fac_opts)
            sel_sub = st.selectbox("Subject", sub_opts)
            section = st.selectbox("Section", ["A", "B", "C"])

            if st.form_submit_button("Assign", use_container_width=True):
                if sel_fac == "Select faculty" or sel_sub == "Select subject":
                    st.error("Please select both faculty and subject.")
                else:
                    fi = fac_opts.index(sel_fac) - 1
                    si = sub_opts.index(sel_sub) - 1
                    ok, msg = assign_faculty_subject(faculty[fi]["id"], subjects[si]["id"], section)
                    st.success("Assigned successfully.") if ok else st.error(msg)

    with c_cur:
        st.markdown("**Current Assignments**")
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
            df = pd.DataFrame(assignments)[["faculty", "code", "subject", "section"]]
            df.columns = ["Faculty", "Code", "Subject", "Section"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("**Remove Assignment**")
            opts = ["Select assignment"] + [
                f"{a['faculty']} / {a['code']} / Sec {a['section']}"
                for a in assignments
            ]
            sel = st.selectbox("", opts, key="del_assign_sel", label_visibility="collapsed")
            if sel != "Select assignment":
                idx = opts.index(sel) - 1
                if st.button("Remove Assignment", key="del_assign_btn"):
                    ok, msg = delete_assignment(assignments[idx]["id"])
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
        else:
            st.info("No assignments yet.")
