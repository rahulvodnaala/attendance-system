import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import (
    get_student_profile, get_student_attendance_summary,
    get_student_detailed_attendance, get_subjects
)

C = {
    "student": "#059669", "admin": "#4f46e5", "faculty": "#0284c7",
    "success": "#059669", "success_bg": "#ecfdf5", "success_b": "#a7f3d0",
    "warning": "#d97706", "warning_bg": "#fffbeb", "warning_b": "#fde68a",
    "danger":  "#dc2626", "danger_bg":  "#fef2f2", "danger_b":  "#fecaca",
    "text":    "#0f172a", "text2": "#475569", "muted": "#94a3b8",
    "border":  "#e2e6f0", "bg2": "#eaecf4",
}

def _pct_color(p):
    if p >= 75: return C["success"]
    if p >= 60: return C["warning"]
    return C["danger"]

def _badge(p):
    if p >= 75:   return '<span class="badge badge-success">Safe</span>'
    if p >= 60:   return '<span class="badge badge-warning">Warning</span>'
    return '<span class="badge badge-danger">Critical</span>'

def section(title, color=None):
    dot = color or C["student"]
    st.markdown(f"""
    <div class="section-header">
        <span class="section-dot" style="background:{dot}"></span>
        <h3>{title}</h3>
    </div>""", unsafe_allow_html=True)


def render_student(user):
    profile = get_student_profile(user["id"])
    if not profile:
        st.error("Student profile not found.")
        return

    st.markdown(f"""
    <div class="page-header">
        <h1>{profile['name']}</h1>
        <p>
            <b style="color:{C['student']}">{profile['roll_number']}</b>
            &nbsp;&middot;&nbsp; {profile['dept_name']}
            &nbsp;&middot;&nbsp; Semester {profile['semester']}
            &nbsp;&middot;&nbsp; Section {profile['section']}
        </p>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["My Attendance", "Subject Detail", "Calendar"])
    with tab1: _overview_tab(profile)
    with tab2: _subject_tab(profile)
    with tab3: _calendar_tab(profile)


# ── Overview ──────────────────────────────────
def _overview_tab(profile):
    summary = get_student_attendance_summary(profile["id"])
    if not summary:
        st.info("No attendance data available yet.")
        return

    df = pd.DataFrame(summary)
    df["pct"] = df.apply(
        lambda r: round(r["present"] / r["total_classes"] * 100, 1) if r["total_classes"] > 0 else 0.0,
        axis=1)

    overall     = round(df["pct"].mean(), 1)
    below_75    = int((df["pct"] < 75).sum())
    safe        = int((df["pct"] >= 75).sum())
    tot_present = int(df["present"].sum())
    tot_classes = int(df["total_classes"].sum())
    col         = _pct_color(overall)

    # Hero card
    grad = "linear-gradient(135deg,#059669,#0d9488)" if overall >= 75 else (
           "linear-gradient(135deg,#d97706,#f59e0b)" if overall >= 60 else
           "linear-gradient(135deg,#dc2626,#ef4444)")
    st.markdown(f"""
    <div class="metric-card" style="text-align:center;padding:2rem 1.5rem;margin-bottom:1.5rem;">
        <div class="metric-bar" style="background:{grad}"></div>
        <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;
                    color:{C['muted']};margin-bottom:0.5rem;font-weight:600;">
            Overall Attendance
        </div>
        <div style="font-size:3.5rem;font-weight:800;color:{col};line-height:1;
                    font-family:'Sora',sans-serif;letter-spacing:-0.03em;">
            {overall}%
        </div>
        <div style="margin-top:0.6rem">{_badge(overall)}</div>
    </div>""", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    mdata = [
        (m1, safe,        "Safe Subjects",    C["success"], "linear-gradient(135deg,#059669,#0d9488)"),
        (m2, below_75,    "Below 75%",        C["danger"],  "linear-gradient(135deg,#dc2626,#ef4444)"),
        (m3, f"{tot_present}/{tot_classes}", "Classes Attended", C["student"], "linear-gradient(135deg,#059669,#0d9488)"),
    ]
    for col_el, val, label, color, bar in mdata:
        with col_el:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-bar" style="background:{bar}"></div>
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section("Subject-wise Breakdown", C["student"])

    for _, row in df.iterrows():
        p    = row["pct"]
        col  = _pct_color(p)
        barw = max(0, min(100, p))
        st.markdown(f"""
        <div class="info-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem">
                <div>
                    <span style="font-size:0.85rem;font-weight:700;color:{C['text']}">{row['code']}</span>
                    <span style="font-size:0.78rem;color:{C['muted']};margin-left:0.6rem">{row['subject']}</span>
                </div>
                <div style="display:flex;align-items:center;gap:0.6rem">
                    {_badge(p)}
                    <span style="font-size:1rem;font-weight:800;color:{col};
                                 font-family:'Sora',sans-serif;">{p}%</span>
                </div>
            </div>
            <div class="att-progress-wrap">
                <div class="att-progress-bar" style="width:{barw}%;background:{col}"></div>
            </div>
            <div style="display:flex;gap:1.5rem;margin-top:0.45rem;font-size:0.72rem;color:{C['muted']}">
                <span style="color:{C['success']}">Present: <b>{row['present']}</b></span>
                <span style="color:{C['danger']}">Absent: <b>{row['absent']}</b></span>
                <span style="color:{C['warning']}">Late: <b>{row['late']}</b></span>
                <span>Total: <b>{row['total_classes']}</b></span>
            </div>
        </div>""", unsafe_allow_html=True)

    needs = [(row["code"], row["subject"], row["present"], row["total_classes"])
             for _, row in df.iterrows() if row["pct"] < 75 and row["total_classes"] > 0]
    if needs:
        section("Classes Required to Reach 75%", C["warning"])
        for code, name, present, total in needs:
            needed = max(0, int((0.75 * total - present) / 0.25) + 1)
            st.markdown(f"""
            <div class="info-card" style="border-left:3px solid {C['warning']};">
                <span style="font-weight:700;color:{C['text']};font-size:0.85rem">{code}</span>
                <span style="color:{C['muted']};font-size:0.8rem;margin-left:0.5rem">{name}</span><br>
                <span style="font-size:0.82rem;color:{C['text2']}">
                    Attend <b style="color:{C['warning']}">{needed} more consecutive class(es)</b> to reach 75%
                </span>
            </div>""", unsafe_allow_html=True)


# ── Subject Detail ────────────────────────────
def _subject_tab(profile):
    section("Subject Detail", C["student"])

    subjects = get_subjects(dept_id=profile["department_id"], semester=profile["semester"])
    if not subjects:
        st.info("No subjects found.")
        return

    opts = ["Select subject"] + [f"{s['code']} — {s['name']}" for s in subjects]
    sel  = st.selectbox("Subject", opts)
    if sel == "Select subject":
        return

    subject = subjects[opts.index(sel)-1]
    records = get_student_detailed_attendance(profile["id"], subject["id"])
    if not records:
        st.info("No attendance records for this subject yet.")
        return

    df      = pd.DataFrame(records)
    df["status"] = df["status"].fillna("not marked")
    total   = len(df)
    present = int((df["status"] == "present").sum())
    absent  = int((df["status"] == "absent").sum())
    late    = int((df["status"] == "late").sum())
    pct     = round(present / total * 100, 1) if total > 0 else 0
    col     = _pct_color(pct)

    m1, m2, m3, m4 = st.columns(4)
    for c, label, val, color in [
        (m1, "Total Classes", total,   C["faculty"]),
        (m2, "Present",       present, C["success"]),
        (m3, "Absent",        absent,  C["danger"]),
        (m4, "Attendance %",  f"{pct}%", col),
    ]:
        with c:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-bar" style="background:{color}"></div>
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Timeline
    scmap = {"present": C["success"], "absent": C["danger"],
             "late": C["warning"], "not marked": C["muted"]}
    fig = go.Figure()
    for status, color in scmap.items():
        mask = df["status"] == status
        if mask.any():
            fig.add_trace(go.Scatter(
                x=df[mask]["date"], y=[status.capitalize()] * mask.sum(),
                mode="markers", marker=dict(size=13, color=color, symbol="square"),
                name=status.capitalize(),
                hovertemplate="%{x}<extra></extra>"
            ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=C["muted"]),
        margin=dict(l=10, r=10, t=36, b=10), height=180,
        title=dict(text="Attendance Timeline", font=dict(size=12, color=C["text"])),
        xaxis=dict(gridcolor="rgba(0,0,0,0.04)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0.04)"),
        showlegend=True, legend=dict(font=dict(color=C["muted"], size=11))
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    disp = df.rename(columns={"date":"Date","status":"Status","topic":"Topic"})
    disp["Status"] = disp["Status"].apply(
        lambda s: "Present" if s=="present" else ("Absent" if s=="absent" else ("Late" if s=="late" else "—")))
    st.dataframe(disp[["Date","Status","Topic"]], use_container_width=True, hide_index=True)


# ── Calendar ──────────────────────────────────
def _calendar_tab(profile):
    section("Monthly Calendar", C["student"])

    from database import get_connection
    conn = get_connection()
    rows = conn.execute("""
        SELECT sess.date, sub.code, a.status
        FROM attendance_sessions sess
        JOIN subjects sub ON sess.subject_id=sub.id
        LEFT JOIN attendance a ON a.session_id=sess.id AND a.student_id=?
        JOIN students st ON st.id=?
        WHERE sub.department_id=st.department_id AND sub.semester=st.semester
        ORDER BY sess.date DESC LIMIT 60
    """, (profile["id"], profile["id"])).fetchall()
    conn.close()

    if not rows:
        st.info("No data available yet.")
        return

    df = pd.DataFrame(rows, columns=["date","subject","status"])
    df["date"]   = pd.to_datetime(df["date"])
    df["status"] = df["status"].fillna("not marked")
    df["day"]    = df["date"].dt.day
    df["month"]  = df["date"].dt.strftime("%B %Y")

    for month in df["month"].unique()[:3]:
        st.markdown(f"<p style='font-size:0.78rem;font-weight:700;color:{C['muted']};"
                    f"text-transform:uppercase;letter-spacing:0.08em;margin:1rem 0 0.5rem'>{month}</p>",
                    unsafe_allow_html=True)
        mdf  = df[df["month"] == month]
        days = sorted(mdf["day"].unique())

        day_map = {}
        for day in days:
            statuses = mdf[mdf["day"] == day]["status"].tolist()
            if "absent"  in statuses: day_map[day] = (C["danger"],  "A")
            elif "late"  in statuses: day_map[day] = (C["warning"], "L")
            elif "present" in statuses: day_map[day] = (C["success"], "P")
            else: day_map[day] = (C["muted"], "—")

        cols = st.columns(min(len(day_map), 10))
        for i, (day, (color, label)) in enumerate(day_map.items()):
            with cols[i % len(cols)]:
                st.markdown(
                    f"<div style='text-align:center;border:1px solid {color}55;"
                    f"border-radius:8px;padding:0.4rem 0.25rem;margin-bottom:0.3rem;"
                    f"background:{color}12'>"
                    f"<div style='font-size:0.65rem;color:{C['muted']}'>{day}</div>"
                    f"<div style='font-size:0.78rem;font-weight:700;color:{color}'>{label}</div>"
                    f"</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:flex;gap:1.75rem;margin-top:1rem;font-size:0.78rem;">
        <span style="color:{C['success']}"><b>P</b> — Present</span>
        <span style="color:{C['danger']}"><b>A</b> — Absent</span>
        <span style="color:{C['warning']}"><b>L</b> — Late</span>
        <span style="color:{C['muted']}"><b>—</b> — No class</span>
    </div>""", unsafe_allow_html=True)
