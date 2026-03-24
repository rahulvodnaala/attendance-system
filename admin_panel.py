import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import (
    get_overall_stats, get_all_students, get_all_faculty,
    get_departments, get_subjects, add_user, add_subject,
    assign_faculty_subject, get_connection,
    delete_student, delete_faculty, delete_subject, delete_assignment,
    add_department, delete_department, update_department,
    update_subject, get_audit_logs
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


def _confirm_action(state_key: str, message: str) -> bool:
    st.warning(message)
    c1, c2 = st.columns(2)
    confirmed = False
    with c1:
        if st.button("Confirm", key=f"{state_key}_confirm", use_container_width=True):
            confirmed = True
    with c2:
        if st.button("Cancel", key=f"{state_key}_cancel", use_container_width=True):
            st.session_state.pop(state_key, None)
            st.rerun()
    return confirmed


def render_admin():
    st.markdown("""
    <div class="page-header">
        <h1>Admin Dashboard</h1>
        <p>System overview, student & faculty management</p>
    </div>""", unsafe_allow_html=True)

    actor = st.session_state.get("user", {}).get("email", "admin")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["Overview", "Students", "Faculty", "Departments", "Subjects", "Assignments", "Audit Logs"])
    with tab1: _overview()
    with tab2: _students(actor)
    with tab3: _faculty(actor)
    with tab4: _departments(actor)
    with tab5: _subjects(actor)
    with tab6: _assignments(actor)
    with tab7: _audit_logs()


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
def _students(actor):
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
            password = st.text_input("Password", type="password")
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
                target_id = students[opts.index(sel)-1]["id"]
                if st.button("Delete Selected", key="del_student_btn"):
                    st.session_state["pending_del_student"] = target_id
                if st.session_state.get("pending_del_student") == target_id and _confirm_action(
                    "pending_del_student", "This will permanently delete this student and related user records."
                ):
                    ok, msg = delete_student(target_id, actor=actor)
                    st.success(msg) if ok else st.error(msg)
                    st.session_state.pop("pending_del_student", None)
                    st.rerun()
        else:
            st.info("No students added yet.")


# ── Faculty ───────────────────────────────────
def _faculty(actor):
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
            password = st.text_input("Password", type="password")
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
                target_id = faculty[opts.index(sel)-1]["id"]
                if st.button("Delete Selected", key="del_fac_btn"):
                    st.session_state["pending_del_faculty"] = target_id
                if st.session_state.get("pending_del_faculty") == target_id and _confirm_action(
                    "pending_del_faculty", "This will permanently delete this faculty, assignments, and linked sessions."
                ):
                    ok, msg = delete_faculty(target_id, actor=actor)
                    st.success(msg) if ok else st.error(msg)
                    st.session_state.pop("pending_del_faculty", None)
                    st.rerun()
        else:
            st.info("No faculty added yet.")


# ── Subjects ──────────────────────────────────
def _departments(actor):
    section("Departments", C["admin"])
    c_add, c_list = st.columns([1, 2])

    with c_add:
        st.markdown(
            f"<p style='font-size:0.82rem;font-weight:700;color:{C['admin']};margin-bottom:0.75rem'>Add New Department</p>",
            unsafe_allow_html=True
        )
        with st.form("add_department", clear_on_submit=True):
            name = st.text_input("Department Name")
            code = st.text_input("Department Code")
            if st.form_submit_button("Add Department", use_container_width=True):
                ok, msg = add_department(name, code, actor=actor)
                st.success(msg) if ok else st.error(msg)
                if ok:
                    st.rerun()

    with c_list:
        st.markdown(
            f"<p style='font-size:0.82rem;font-weight:700;color:{C['text2']};margin-bottom:0.75rem'>All Departments</p>",
            unsafe_allow_html=True
        )
        depts = get_departments()
        if depts:
            df = pd.DataFrame(depts)[["code", "name"]]
            df.columns = ["Code", "Department"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown(
                f"<p style='font-size:0.8rem;font-weight:600;color:{C['danger']};margin:0.75rem 0 0.3rem'>Delete Department</p>",
                unsafe_allow_html=True
            )
            opts = ["Select department"] + [f"{d['code']} — {d['name']}" for d in depts]
            sel = st.selectbox("", opts, key="del_dept_sel", label_visibility="collapsed")
            edit_sel = st.selectbox("Edit Department", opts, key="edit_dept_sel")
            if edit_sel != "Select department":
                d = depts[opts.index(edit_sel) - 1]
                with st.form("edit_department"):
                    new_name = st.text_input("Department Name", value=d["name"])
                    new_code = st.text_input("Department Code", value=d["code"])
                    if st.form_submit_button("Update Department", use_container_width=True):
                        ok, msg = update_department(d["id"], new_name, new_code, actor=actor)
                        st.success(msg) if ok else st.error(msg)
                        if ok:
                            st.rerun()
            if sel != "Select department":
                target_id = depts[opts.index(sel) - 1]["id"]
                if st.button("Delete Selected", key="del_dept_btn"):
                    st.session_state["pending_del_department"] = target_id
                if st.session_state.get("pending_del_department") == target_id and _confirm_action(
                    "pending_del_department", "This will permanently delete this department if it is not in use."
                ):
                    ok, msg = delete_department(target_id, actor=actor)
                    st.success(msg) if ok else st.error(msg)
                    st.session_state.pop("pending_del_department", None)
                    if ok:
                        st.rerun()
        else:
            st.info("No departments added yet.")


# ── Subjects ──────────────────────────────────
def _subjects(actor):
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
                    ok, msg = db_add(name, code, dept_id, semester, credits, actor=actor)
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
            edit_sel = st.selectbox("Edit Subject", opts, key="edit_sub_sel")
            if edit_sel != "Select subject":
                s = subjects[opts.index(edit_sel) - 1]
                dept_names = [d["name"] for d in depts]
                current_dept_name = next((d["name"] for d in depts if d["id"] == s["department_id"]), dept_names[0] if dept_names else "")
                with st.form("edit_subject"):
                    new_name = st.text_input("Subject Name", value=s["name"])
                    new_code = st.text_input("Subject Code", value=s["code"])
                    new_dept = st.selectbox("Department", dept_names, index=dept_names.index(current_dept_name) if current_dept_name in dept_names else 0)
                    new_sem = st.selectbox("Semester", list(range(1, 9)), index=max(0, int(s["semester"]) - 1))
                    credit_values = [1, 2, 3, 4, 5]
                    new_credits = st.selectbox("Credits", credit_values, index=credit_values.index(s["credits"]) if s["credits"] in credit_values else 2)
                    if st.form_submit_button("Update Subject", use_container_width=True):
                        dept_id = next(d["id"] for d in depts if d["name"] == new_dept)
                        ok, msg = update_subject(s["id"], new_name, new_code, dept_id, new_sem, new_credits, actor=actor)
                        st.success(msg) if ok else st.error(msg)
                        if ok:
                            st.rerun()
            if sel != "Select subject":
                target_id = subjects[opts.index(sel)-1]["id"]
                if st.button("Delete Selected", key="del_sub_btn"):
                    st.session_state["pending_del_subject"] = target_id
                if st.session_state.get("pending_del_subject") == target_id and _confirm_action(
                    "pending_del_subject", "This will permanently delete this subject and all linked attendance sessions."
                ):
                    ok, msg = delete_subject(target_id, actor=actor)
                    st.success(msg) if ok else st.error(msg)
                    st.session_state.pop("pending_del_subject", None)
                    st.rerun()
        else:
            st.info("No subjects added yet.")


# ── Assignments ───────────────────────────────
def _assignments(actor):
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
                    ok, msg = assign_faculty_subject(faculty[fi]["id"], subjects[si]["id"], section_, actor=actor)
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
                target_id = assignments[opts.index(sel)-1]["id"]
                if st.button("Remove Selected", key="del_assign_btn"):
                    st.session_state["pending_del_assignment"] = target_id
                if st.session_state.get("pending_del_assignment") == target_id and _confirm_action(
                    "pending_del_assignment", "This will permanently remove this faculty-subject assignment."
                ):
                    ok, msg = delete_assignment(target_id, actor=actor)
                    st.success(msg) if ok else st.error(msg)
                    st.session_state.pop("pending_del_assignment", None)
                    st.rerun()
        else:
            st.info("No assignments yet.")


def _audit_logs():
    section("Recent Activity", C["admin"])
    top = st.columns([1, 1, 1, 2])
    with top[0]:
        limit = st.selectbox("Rows", [50, 100, 200, 300, 500], index=2, key="audit_limit")
    with top[1]:
        action_filter = st.selectbox("Action", ["All", "create", "update", "delete"], key="audit_action")
    with top[2]:
        entity_filter = st.selectbox("Entity", ["All", "department", "subject", "student", "faculty", "faculty_subject"], key="audit_entity")
    with top[3]:
        query = st.text_input("Search (actor/details)", key="audit_query", placeholder="e.g. admin@college.edu")

    logs = get_audit_logs(limit=limit)
    if not logs:
        st.info("No audit logs yet.")
        return

    df = pd.DataFrame(logs)
    if action_filter != "All":
        df = df[df["action"] == action_filter]
    if entity_filter != "All":
        df = df[df["entity"] == entity_filter]
    if query:
        q = query.strip().lower()
        df = df[df.apply(lambda r: q in str(r["actor"]).lower() or q in str(r["details"]).lower(), axis=1)]

    if df.empty:
        st.info("No audit logs match current filters.")
        return

    df = df[["created_at", "actor", "action", "entity", "entity_id", "details"]]
    df.columns = ["Timestamp", "Actor", "Action", "Entity", "Entity ID", "Details"]
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download Audit CSV",
        data=df.to_csv(index=False),
        file_name="audit_logs.csv",
        mime="text/csv",
        use_container_width=True
    )
