import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from database import (
    get_faculty_subjects, get_students_for_subject, get_faculty_id,
    session_exists, create_attendance_session, mark_attendance,
    get_attendance_for_session, get_subject_attendance_summary,
    get_sessions_for_subject
)

COLORS = {
    "accent": "#6366f1", "accent2": "#8b5cf6",
    "success": "#10b981", "warning": "#f59e0b", "danger": "#ef4444",
    "bg": "#111827", "bg2": "#1a2236", "text": "#f1f5f9", "text2": "#94a3b8"
}

def plot_cfg():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color=COLORS["text2"]),
        margin=dict(l=10, r=10, t=30, b=10)
    )


def render_faculty(user):
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-badge">Faculty Panel</div>
        <p class="hero-title">👩‍🏫 Welcome, {user['name']}</p>
        <p class="hero-subtitle">Mark attendance, track class stats & generate reports</p>
    </div>
    """, unsafe_allow_html=True)

    subjects = get_faculty_subjects(user["id"])

    if not subjects:
        st.warning("⚠️ No subjects assigned yet. Contact admin.")
        return

    tab1, tab2, tab3 = st.tabs(["✏️ Mark Attendance", "📊 Reports", "📋 Session History"])

    with tab1:
        _mark_attendance_tab(user, subjects)
    with tab2:
        _reports_tab(subjects)
    with tab3:
        _session_history_tab(subjects)


def _mark_attendance_tab(user, subjects):
    st.markdown("""<div class="section-header"><h3>✏️ Mark Today's Attendance</h3></div>""",
                unsafe_allow_html=True)

    col_sel, col_form = st.columns([1, 3])

    with col_sel:
        sub_options = [f"{s['code']} — {s['name']} (Sec {s['section']})" for s in subjects]
        sel_sub = st.selectbox("Select Subject", sub_options)
        sub_idx = sub_options.index(sel_sub)
        subject = subjects[sub_idx]

        att_date = st.date_input("Date", value=date.today(), max_value=date.today())
        topic = st.text_input("Topic / Lecture Note", placeholder="e.g. Recursion intro")

    with col_form:
        faculty_id = get_faculty_id(user["id"])
        students = get_students_for_subject(subject["subject_id"], subject["section"])

        if not students:
            st.warning("No students found for this subject/section.")
            return

        # Check if session already exists
        existing_sess_id = session_exists(
            subject["subject_id"], faculty_id, att_date.isoformat(), subject["section"]
        )

        existing_records = {}
        if existing_sess_id:
            existing_records = get_attendance_for_session(existing_sess_id)
            st.info(f"📝 Editing existing session for {att_date}")

        st.markdown(f"**Marking attendance for {len(students)} students**")

        # Build attendance form
        status_map = {}
        with st.form(f"att_form_{subject['subject_id']}_{att_date}"):
            cols = st.columns([3, 2, 2, 2])
            cols[0].markdown("**Student**")
            cols[1].markdown("**Present**")
            cols[2].markdown("**Absent**")
            cols[3].markdown("**Late**")

            for s in students:
                c0, c1, c2, c3 = st.columns([3, 2, 2, 2])
                c0.markdown(f"<div style='color:#f1f5f9;font-size:0.9rem;padding-top:0.4rem'>"
                            f"<b>{s['roll_number']}</b> — {s['name']}</div>",
                            unsafe_allow_html=True)
                default = existing_records.get(s["id"], {}).get("status", "present")
                default_idx = ["present", "absent", "late"].index(default)

                val = c1.radio(f"_p_{s['id']}", ["P"], key=f"p_{s['id']}",
                               label_visibility="collapsed")
                status_map[s["id"]] = "present"  # placeholder, overridden by radio below

            # Full width radio per student
            st.markdown("<hr style='border-color:rgba(255,255,255,0.05)'>", unsafe_allow_html=True)

            per_student = {}
            for s in students:
                existing_status = existing_records.get(s["id"], {}).get("status", "Present")
                opts = ["Present", "Absent", "Late"]
                def_idx = ["present", "absent", "late"].index(
                    existing_records.get(s["id"], {}).get("status", "present")
                ) if s["id"] in existing_records else 0
                chosen = st.radio(
                    f"**{s['roll_number']}** — {s['name']}",
                    opts, index=def_idx,
                    horizontal=True,
                    key=f"att_{s['id']}_{subject['subject_id']}_{att_date}"
                )
                per_student[s["id"]] = chosen.lower()

            submitted = st.form_submit_button("💾 Save Attendance", use_container_width=True)

        if submitted:
            if not existing_sess_id:
                sess_id = create_attendance_session(
                    subject["subject_id"], faculty_id, att_date.isoformat(),
                    subject["section"], topic
                )
            else:
                sess_id = existing_sess_id

            for st_id, status in per_student.items():
                mark_attendance(sess_id, st_id, status)

            present = sum(1 for v in per_student.values() if v == "present")
            absent = sum(1 for v in per_student.values() if v == "absent")
            late = sum(1 for v in per_student.values() if v == "late")

            st.success(f"✅ Attendance saved! Present: {present} | Absent: {absent} | Late: {late}")
            _mini_summary_chart(present, absent, late)


def _mini_summary_chart(present, absent, late):
    fig = go.Figure(go.Pie(
        labels=["Present", "Absent", "Late"],
        values=[present, absent, late],
        hole=0.65,
        marker=dict(colors=["#10b981", "#ef4444", "#f59e0b"]),
        textinfo="label+percent",
        hovertemplate="%{label}: %{value}<extra></extra>"
    ))
    fig.update_layout(
        **plot_cfg(), height=220,
        title=dict(text="Today's Class Summary", font=dict(size=13, color="#f1f5f9")),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _reports_tab(subjects):
    st.markdown("""<div class="section-header"><h3>📊 Subject Attendance Report</h3></div>""",
                unsafe_allow_html=True)

    sub_options = [f"{s['code']} — {s['name']} (Sec {s['section']})" for s in subjects]
    sel = st.selectbox("Select Subject", sub_options, key="rep_sub")
    sub_idx = sub_options.index(sel)
    subject = subjects[sub_idx]

    summary = get_subject_attendance_summary(subject["subject_id"], subject["section"])

    if not summary:
        st.info("No attendance data yet.")
        return

    df = pd.DataFrame(summary)
    df["pct"] = df.apply(
        lambda r: round(r["present"] / r["total_classes"] * 100, 1) if r["total_classes"] > 0 else 0,
        axis=1
    )
    df["Status"] = df["pct"].apply(
        lambda p: "🟢 Safe" if p >= 75 else ("🟡 Warning" if p >= 60 else "🔴 Critical")
    )

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)
    total_classes = df["total_classes"].max() if len(df) > 0 else 0
    avg_pct = df["pct"].mean()
    below_75 = (df["pct"] < 75).sum()

    c1.metric("Total Classes", total_classes)
    c2.metric("Avg Attendance", f"{avg_pct:.1f}%")
    c3.metric("Below 75%", below_75)
    c4.metric("Safe Students", len(df) - below_75)

    # Bar chart
    fig = go.Figure(go.Bar(
        x=df["roll_number"], y=df["pct"],
        marker_color=[
            COLORS["success"] if p >= 75 else (COLORS["warning"] if p >= 60 else COLORS["danger"])
            for p in df["pct"]
        ],
        hovertemplate="%{x}<br><b>%{y:.1f}%</b><extra></extra>",
        text=[f"{p:.0f}%" for p in df["pct"]],
        textposition="outside"
    ))
    fig.add_hline(y=75, line_dash="dash", line_color=COLORS["warning"],
                  annotation_text="75% Min")
    fig.update_layout(
        **plot_cfg(), height=320,
        title=dict(text="Attendance % per Student", font=dict(size=14, color=COLORS["text"])),
        yaxis=dict(range=[0, 115], ticksuffix="%", gridcolor="rgba(255,255,255,0.05)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Table
    display_df = df[["roll_number", "name", "total_classes", "present", "absent", "late", "pct", "Status"]]
    display_df.columns = ["Roll No", "Name", "Total", "Present", "Absent", "Late", "Att %", "Status"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Export
    csv = display_df.to_csv(index=False)
    st.download_button(
        "⬇️ Download CSV Report",
        data=csv,
        file_name=f"attendance_{subject['code']}_sec{subject['section']}.csv",
        mime="text/csv"
    )


def _session_history_tab(subjects):
    st.markdown("""<div class="section-header"><h3>📋 Session History</h3></div>""",
                unsafe_allow_html=True)

    sub_options = [f"{s['code']} — {s['name']} (Sec {s['section']})" for s in subjects]
    sel = st.selectbox("Select Subject", sub_options, key="hist_sub")
    sub_idx = sub_options.index(sel)
    subject = subjects[sub_idx]

    sessions = get_sessions_for_subject(subject["subject_id"], subject["section"])

    if not sessions:
        st.info("No sessions held yet.")
        return

    df = pd.DataFrame(sessions)
    df["att_pct"] = df.apply(
        lambda r: round(r["present_count"] / r["total_marked"] * 100, 1) if r["total_marked"] > 0 else 0,
        axis=1
    )
    display = df[["date", "topic", "total_marked", "present_count", "att_pct", "faculty_name"]]
    display.columns = ["Date", "Topic", "Total Students", "Present", "Att %", "Faculty"]
    st.dataframe(display, use_container_width=True, hide_index=True)
