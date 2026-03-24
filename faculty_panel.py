import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from database import (
    get_faculty_subjects, get_students_for_subject, get_faculty_id,
    session_exists, create_attendance_session, mark_attendance,
    get_attendance_for_session, get_subject_attendance_summary,
    get_sessions_for_subject, update_session_topic
)

C = {
    "faculty": "#0284c7", "admin": "#4f46e5", "student": "#059669",
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
    dot = color or C["faculty"]
    st.markdown(f"""
    <div class="section-header">
        <span class="section-dot" style="background:{dot}"></span>
        <h3>{title}</h3>
    </div>""", unsafe_allow_html=True)


def render_faculty(user):
    st.markdown(f"""
    <div class="page-header">
        <h1>Faculty Dashboard</h1>
        <p>Mark attendance, manage sessions and generate reports</p>
    </div>""", unsafe_allow_html=True)

    subjects = get_faculty_subjects(user["id"])
    if not subjects:
        st.warning("No subjects assigned yet. Contact the administrator.")
        return

    tab1, tab2, tab3 = st.tabs(["Mark Attendance", "Reports", "Session History"])
    with tab1: _mark_tab(user, subjects)
    with tab2: _reports_tab(subjects)
    with tab3: _history_tab(subjects)


# ── Mark Attendance ───────────────────────────
def _mark_tab(user, subjects):
    section("Mark Attendance", C["faculty"])

    c_sel, c_main = st.columns([1, 3])
    with c_sel:
        sub_opts = [f"{s['code']} — {s['name']} (Sec {s['section']})" for s in subjects]
        sel      = st.selectbox("Subject", sub_opts)
        sub      = subjects[sub_opts.index(sel)]
        att_date = st.date_input("Date", value=date.today(), max_value=date.today())
        topic    = st.text_input("Topic / Lecture Note", placeholder="e.g. Binary Trees")

    with c_main:
        faculty_id  = get_faculty_id(user["id"])
        if faculty_id is None:
            st.error("Faculty profile not found. Please contact the administrator.")
            return
        students    = get_students_for_subject(sub["subject_id"], sub["section"])

        if not students:
            st.info("No students enrolled in this subject / section.")
            return

        existing_id = session_exists(sub["subject_id"], faculty_id,
                                     att_date.isoformat(), sub["section"])
        existing    = get_attendance_for_session(existing_id) if existing_id else {}

        if existing_id:
            st.info(f"Editing existing session for {att_date}.")

        # Summary strip
        st.markdown(f"""
        <div class="info-card" style="display:flex;gap:2rem;align-items:center;padding:0.9rem 1.25rem;margin-bottom:1rem;">
            <span style="font-size:0.8rem;color:{C['text2']}">
                <b style="color:{C['faculty']}">{sub['code']}</b> — {sub['name']}
            </span>
            <span style="font-size:0.8rem;color:{C['muted']}">Section {sub['section']}</span>
            <span style="font-size:0.8rem;color:{C['muted']}">{len(students)} students</span>
        </div>""", unsafe_allow_html=True)

        action_cols = st.columns(4)
        if action_cols[0].button("All Present", use_container_width=True, key=f"bulk_present_{sub['subject_id']}_{att_date}"):
            for s in students:
                st.session_state[f"att_{s['id']}_{sub['subject_id']}_{att_date}"] = "Present"
            st.rerun()
        if action_cols[1].button("All Absent", use_container_width=True, key=f"bulk_absent_{sub['subject_id']}_{att_date}"):
            for s in students:
                st.session_state[f"att_{s['id']}_{sub['subject_id']}_{att_date}"] = "Absent"
            st.rerun()
        if action_cols[2].button("All Late", use_container_width=True, key=f"bulk_late_{sub['subject_id']}_{att_date}"):
            for s in students:
                st.session_state[f"att_{s['id']}_{sub['subject_id']}_{att_date}"] = "Late"
            st.rerun()
        if action_cols[3].button("Use Previous", use_container_width=True, key=f"bulk_previous_{sub['subject_id']}_{att_date}"):
            for s in students:
                status = existing.get(s["id"], {}).get("status", "present").capitalize()
                st.session_state[f"att_{s['id']}_{sub['subject_id']}_{att_date}"] = status
            st.rerun()

        with st.form(f"att_{sub['subject_id']}_{att_date}"):
            per_student = {}
            for s in students:
                default     = existing.get(s["id"], {}).get("status", "present")
                radio_key = f"att_{s['id']}_{sub['subject_id']}_{att_date}"
                current_ui = st.session_state.get(radio_key, default.capitalize())
                default_idx = ["Present", "Absent", "Late"].index(current_ui) if current_ui in ["Present", "Absent", "Late"] else ["present", "absent", "late"].index(default)
                chosen = st.radio(
                    f"**{s['roll_number']}** — {s['name']}",
                    ["Present", "Absent", "Late"],
                    index=default_idx, horizontal=True,
                    key=radio_key
                )
                per_student[s["id"]] = chosen.lower()

            saved = st.form_submit_button("Save Attendance", use_container_width=True)

        if saved:
            if not existing_id:
                sess_id = create_attendance_session(
                    sub["subject_id"], faculty_id,
                    att_date.isoformat(), sub["section"], topic)
            else:
                sess_id = existing_id
                if topic: update_session_topic(sess_id, topic)

            for st_id, status in per_student.items():
                mark_attendance(sess_id, st_id, status)

            present = sum(1 for v in per_student.values() if v == "present")
            absent  = sum(1 for v in per_student.values() if v == "absent")
            late    = sum(1 for v in per_student.values() if v == "late")

            # Mini summary cards
            st.success(f"Attendance saved successfully.")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-bar" style="background:{C['success']}"></div>
                    <div class="metric-value" style="color:{C['success']}">{present}</div>
                    <div class="metric-label">Present</div>
                </div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-bar" style="background:{C['danger']}"></div>
                    <div class="metric-value" style="color:{C['danger']}">{absent}</div>
                    <div class="metric-label">Absent</div>
                </div>""", unsafe_allow_html=True)
            with m3:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-bar" style="background:{C['warning']}"></div>
                    <div class="metric-value" style="color:{C['warning']}">{late}</div>
                    <div class="metric-label">Late</div>
                </div>""", unsafe_allow_html=True)


# ── Reports ───────────────────────────────────
def _reports_tab(subjects):
    section("Attendance Reports", C["faculty"])

    sub_opts = [f"{s['code']} — {s['name']} (Sec {s['section']})" for s in subjects]
    sel      = st.selectbox("Subject", sub_opts, key="rep_sub")
    sub      = subjects[sub_opts.index(sel)]

    summary = get_subject_attendance_summary(sub["subject_id"], sub["section"])
    if not summary:
        st.info("No attendance data for this subject yet.")
        return

    df = pd.DataFrame(summary)
    df["pct"] = df.apply(
        lambda r: round(r["present"] / r["total_classes"] * 100, 1) if r["total_classes"] > 0 else 0.0,
        axis=1)

    total_cls = int(df["total_classes"].max()) if len(df) > 0 else 0
    avg_pct   = round(df["pct"].mean(), 1)
    below_75  = int((df["pct"] < 75).sum())

    m1, m2, m3, m4 = st.columns(4)
    mdata = [
        (m1, "Total Classes", total_cls, C["faculty"]),
        (m2, "Avg Attendance", f"{avg_pct}%",
         C["success"] if avg_pct >= 75 else C["warning"], ),
        (m3, "Below 75%", below_75, C["danger"]),
        (m4, "Safe Students", len(df)-below_75, C["success"]),
    ]
    for col, label, val, color in mdata:
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-bar" style="background:{color}"></div>
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    bar_colors = [
        C["success"] if p >= 75 else (C["warning"] if p >= 60 else C["danger"])
        for p in df["pct"]
    ]
    fig = go.Figure(go.Bar(
        x=df["roll_number"], y=df["pct"],
        marker_color=bar_colors,
        text=[f"{p:.0f}%" for p in df["pct"]], textposition="outside",
        hovertemplate="%{x}<br><b>%{y:.1f}%</b><extra></extra>"
    ))
    fig.add_hline(y=75, line_dash="dash", line_color=C["warning"],
                  annotation_text="75% minimum", annotation_font_color=C["warning"])
    fig.update_layout(**pcfg(), height=300,
        title=dict(text="Attendance % per Student", font=dict(size=12, color=C["text"])),
        yaxis=dict(range=[0,115], ticksuffix="%", gridcolor="rgba(0,0,0,0.04)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0.04)"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    display = df[["roll_number","name","total_classes","present","absent","late","pct"]].copy()
    display.columns = ["Roll No","Name","Total","Present","Absent","Late","Att %"]
    display["Att %"] = display["Att %"].apply(lambda x: f"{x}%")
    st.dataframe(display, use_container_width=True, hide_index=True)

    # Edit record
    section("Edit Attendance Record", C["warning"])
    st.caption("Select a student and session date to correct their status.")

    students_in_sub = get_students_for_subject(sub["subject_id"], sub["section"])
    sessions        = get_sessions_for_subject(sub["subject_id"], sub["section"])
    if not students_in_sub or not sessions:
        st.info("No sessions to edit.")
        return

    ec1, ec2 = st.columns(2)
    with ec1:
        stu_opts = ["Select student"] + [f"{s['roll_number']} — {s['name']}" for s in students_in_sub]
        sel_stu  = st.selectbox("Student", stu_opts, key="edit_stu")
    with ec2:
        sess_opts = ["Select date"] + [s["date"] for s in sessions]
        sel_sess  = st.selectbox("Session Date", sess_opts, key="edit_sess")

    if sel_stu != "Select student" and sel_sess != "Select date":
        student  = students_in_sub[stu_opts.index(sel_stu)-1]
        session  = sessions[sess_opts.index(sel_sess)-1]
        existing_rec = get_attendance_for_session(session["id"])
        current  = existing_rec.get(student["id"], {}).get("status", "present")
        cur_idx  = ["present", "absent", "late"].index(current)
        new_st   = st.radio(f"Status for {student['name']} on {session['date']}",
                            ["Present", "Absent", "Late"], index=cur_idx, horizontal=True, key="edit_status")
        if st.button("Update Record", key="edit_save"):
            mark_attendance(session["id"], student["id"], new_st.lower())
            st.success("Record updated.")
            st.rerun()

    csv = display.to_csv(index=False)
    st.download_button("Download CSV", data=csv,
                       file_name=f"report_{sub['code']}_sec{sub['section']}.csv",
                       mime="text/csv")


# ── Session History ───────────────────────────
def _history_tab(subjects):
    section("Session History", C["faculty"])

    sub_opts = [f"{s['code']} — {s['name']} (Sec {s['section']})" for s in subjects]
    sel      = st.selectbox("Subject", sub_opts, key="hist_sub")
    sub      = subjects[sub_opts.index(sel)]
    sessions = get_sessions_for_subject(sub["subject_id"], sub["section"])

    if not sessions:
        st.info("No sessions held yet.")
        return

    df = pd.DataFrame(sessions)
    df["att_pct"] = df.apply(
        lambda r: round(r["present_count"] / r["total_marked"] * 100, 1) if r["total_marked"] > 0 else 0,
        axis=1)
    display = df[["date","topic","total_marked","present_count","att_pct","faculty_name"]].copy()
    display.columns = ["Date","Topic","Students","Present","Att %","Faculty"]
    display["Att %"] = display["Att %"].apply(lambda x: f"{x}%")
    st.dataframe(display, use_container_width=True, hide_index=True)

    section("Edit Session Topic", C["warning"])
    sess_opts = ["Select session"] + [f"{s['date']} — {s['topic'] or 'No topic'}" for s in sessions]
    sel_sess  = st.selectbox("Session", sess_opts, key="edit_topic_sess")
    if sel_sess != "Select session":
        idx       = sess_opts.index(sel_sess) - 1
        session   = sessions[idx]
        new_topic = st.text_input("Topic", value=session["topic"] or "", key="edit_topic_val")
        if st.button("Update Topic", key="update_topic_btn"):
            update_session_topic(session["id"], new_topic)
            st.success("Topic updated.")
            st.rerun()
