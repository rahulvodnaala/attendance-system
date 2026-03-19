import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from database import (
    get_student_profile, get_student_attendance_summary,
    get_student_detailed_attendance, get_subjects
)

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


def _pct_color(pct):
    if pct >= 75: return COLORS["success"]
    if pct >= 60: return COLORS["warning"]
    return COLORS["danger"]

def _status_badge(pct):
    if pct >= 75:
        return '<span class="att-badge att-high">✅ Safe</span>'
    if pct >= 60:
        return '<span class="att-badge att-mid">⚠️ Warning</span>'
    return '<span class="att-badge att-low">🚨 Critical</span>'


def render_student(user):
    profile = get_student_profile(user["id"])
    if not profile:
        st.error("Student profile not found.")
        return

    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-badge">Student Portal</div>
        <p class="hero-title">🎓 {profile['name']}</p>
        <p class="hero-subtitle">
            Roll No: <b>{profile['roll_number']}</b> &nbsp;|&nbsp;
            {profile['dept_name']} &nbsp;|&nbsp;
            Semester {profile['semester']} — Section {profile['section']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 My Attendance", "📚 Subject Detail", "📅 Calendar View"])

    with tab1:
        _overview_tab(profile)
    with tab2:
        _subject_detail_tab(profile)
    with tab3:
        _calendar_tab(profile)


def _overview_tab(profile):
    summary = get_student_attendance_summary(profile["id"])

    if not summary:
        st.info("No attendance data yet. Check back after classes begin.")
        return

    df = pd.DataFrame(summary)
    df["pct"] = df.apply(
        lambda r: round(r["present"] / r["total_classes"] * 100, 1) if r["total_classes"] > 0 else 0.0,
        axis=1
    )

    overall_pct = df["pct"].mean()
    below_75 = (df["pct"] < 75).sum()
    safe_subs = (df["pct"] >= 75).sum()

    # Overall metric hero
    pct_color = _pct_color(overall_pct)
    st.markdown(f"""
    <div class="info-card" style="text-align:center; padding: 2rem;">
        <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.1em;
                    color:{COLORS['text2']};margin-bottom:0.5rem;">Overall Attendance</div>
        <div style="font-size:4rem;font-weight:700;color:{pct_color};line-height:1;">
            {overall_pct:.1f}%
        </div>
        {_status_badge(overall_pct)}
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-icon">✅</div>
            <div class="metric-value" style="color:{COLORS['success']}">{safe_subs}</div>
            <div class="metric-label">Safe Subjects</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-icon">🚨</div>
            <div class="metric-value" style="color:{COLORS['danger']}">{below_75}</div>
            <div class="metric-label">Below 75%</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        total_present = df["present"].sum()
        total_classes = df["total_classes"].sum()
        st.markdown(f"""<div class="metric-card">
            <div class="metric-icon">📋</div>
            <div class="metric-value">{total_present}/{total_classes}</div>
            <div class="metric-label">Total Classes Attended</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Radar chart
    col_radar, col_table = st.columns([1, 1])

    with col_radar:
        fig = go.Figure(go.Scatterpolar(
            r=df["pct"].tolist() + [df["pct"].iloc[0]],
            theta=df["code"].tolist() + [df["code"].iloc[0]],
            fill='toself',
            fillcolor="rgba(99,102,241,0.15)",
            line=dict(color=COLORS["accent"], width=2),
            marker=dict(color=COLORS["accent2"], size=6)
        ))
        fig.update_layout(
            **plot_cfg(), height=300,
            polar=dict(
                radialaxis=dict(range=[0, 100], ticksuffix="%",
                                gridcolor="rgba(255,255,255,0.08)",
                                tickcolor=COLORS["text2"]),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
                bgcolor="rgba(0,0,0,0)"
            ),
            title=dict(text="Subject-wise Radar", font=dict(size=13, color=COLORS["text"]))
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_table:
        st.markdown("**Subject-wise Breakdown**")
        for _, row in df.iterrows():
            pct = row["pct"]
            col = _pct_color(pct)
            bar_w = max(0, min(100, pct))
            badge = _status_badge(pct)
            st.markdown(f"""
            <div class="info-card" style="padding:0.8rem 1rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem">
                    <span style="color:{COLORS['text']};font-weight:600;font-size:0.85rem">{row['code']}</span>
                    <span style="color:{col};font-weight:700">{pct:.1f}%</span>
                </div>
                <div style="font-size:0.75rem;color:{COLORS['text2']};margin-bottom:0.4rem">{row['subject']}</div>
                <div class="att-progress-wrap">
                    <div class="att-progress-bar" style="width:{bar_w}%;background:{col}"></div>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:0.4rem;font-size:0.72rem;color:{COLORS['text2']}">
                    <span>Present: {row['present']}</span>
                    <span>Absent: {row['absent']}</span>
                    <span>Late: {row['late']}</span>
                    <span>Total: {row['total_classes']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Classes needed to reach 75%
    st.markdown("""<div class="section-header"><h3>📐 Classes Needed to Reach 75%</h3></div>""",
                unsafe_allow_html=True)
    for _, row in df.iterrows():
        if row["pct"] < 75 and row["total_classes"] > 0:
            n = row["total_classes"]
            p = row["present"]
            # Solve: (p + x) / (n + x) >= 0.75
            # p + x >= 0.75n + 0.75x  =>  0.25x >= 0.75n - p  =>  x >= (0.75n - p)/0.25
            needed = max(0, int((0.75 * n - p) / 0.25) + 1)
            st.markdown(f"""
            <div class="info-card" style="border-left:3px solid {COLORS['warning']};">
                <span style="color:{COLORS['text']};font-weight:600">{row['code']}</span> —
                Attend <b style="color:{COLORS['warning']}">{needed} more consecutive classes</b>
                to reach 75%
            </div>
            """, unsafe_allow_html=True)


def _subject_detail_tab(profile):
    st.markdown("""<div class="section-header"><h3>📚 Detailed Subject View</h3></div>""",
                unsafe_allow_html=True)

    subjects = get_subjects(dept_id=profile["department_id"], semester=profile["semester"])
    if not subjects:
        st.info("No subjects found.")
        return

    sub_opts = [f"{s['code']} — {s['name']}" for s in subjects]
    sel = st.selectbox("Select Subject", sub_opts)
    sub_idx = sub_opts.index(sel)
    subject = subjects[sub_idx]

    records = get_student_detailed_attendance(profile["id"], subject["id"])

    if not records:
        st.info("No attendance records for this subject yet.")
        return

    df = pd.DataFrame(records)
    df["status"] = df["status"].fillna("not marked")

    # Summary
    total = len(df)
    present = (df["status"] == "present").sum()
    absent = (df["status"] == "absent").sum()
    late = (df["status"] == "late").sum()
    pct = round(present / total * 100, 1) if total > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Classes", total)
    c2.metric("Present", present)
    c3.metric("Absent", absent)
    c4.metric("Attendance %", f"{pct}%")

    # Timeline chart
    status_color_map = {"present": COLORS["success"], "absent": COLORS["danger"],
                        "late": COLORS["warning"], "not marked": COLORS["text2"]}

    fig = go.Figure()
    for status, color in status_color_map.items():
        mask = df["status"] == status
        if mask.any():
            fig.add_trace(go.Scatter(
                x=df[mask]["date"], y=[status] * mask.sum(),
                mode="markers",
                marker=dict(size=14, color=color, symbol="square"),
                name=status.capitalize(),
                hovertemplate="%{x}<extra></extra>"
            ))
    fig.update_layout(
        **plot_cfg(), height=200,
        title=dict(text="Attendance Timeline", font=dict(size=13, color=COLORS["text"])),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Table
    display = df.rename(columns={"date": "Date", "status": "Status", "topic": "Topic"})
    display["Status"] = display["Status"].apply(
        lambda s: f"✅ Present" if s == "present" else (
            "❌ Absent" if s == "absent" else ("⏰ Late" if s == "late" else "—"))
    )
    st.dataframe(display[["Date", "Status", "Topic"]], use_container_width=True, hide_index=True)


def _calendar_tab(profile):
    st.markdown("""<div class="section-header"><h3>📅 Monthly Attendance Calendar</h3></div>""",
                unsafe_allow_html=True)

    from database import get_connection
    conn = get_connection()
    rows = conn.execute("""
        SELECT sess.date, sub.code,
               a.status
        FROM attendance_sessions sess
        JOIN subjects sub ON sess.subject_id=sub.id
        LEFT JOIN attendance a ON a.session_id=sess.id AND a.student_id=?
        JOIN students st ON st.id=?
        WHERE sub.department_id=st.department_id AND sub.semester=st.semester
        ORDER BY sess.date DESC
        LIMIT 60
    """, (profile["id"], profile["id"])).fetchall()
    conn.close()

    if not rows:
        st.info("No data yet.")
        return

    df = pd.DataFrame(rows, columns=["date", "subject", "status"])
    df["date"] = pd.to_datetime(df["date"])
    df["status"] = df["status"].fillna("not marked")

    # Monthly pivot
    monthly = df.copy()
    monthly["day"] = monthly["date"].dt.day
    monthly["month"] = monthly["date"].dt.strftime("%b %Y")

    months = monthly["month"].unique()[:3]

    for month in months:
        st.markdown(f"**{month}**")
        mdf = monthly[monthly["month"] == month]
        days = sorted(mdf["day"].unique())

        day_summary = {}
        for day in days:
            day_records = mdf[mdf["day"] == day]["status"].tolist()
            if "absent" in day_records:
                day_summary[day] = ("🔴", COLORS["danger"])
            elif "late" in day_records:
                day_summary[day] = ("🟡", COLORS["warning"])
            elif "present" in day_records:
                day_summary[day] = ("🟢", COLORS["success"])
            else:
                day_summary[day] = ("⚪", COLORS["text2"])

        cols = st.columns(7)
        for i, (day, (emoji, color)) in enumerate(day_summary.items()):
            cols[i % 7].markdown(
                f"<div style='text-align:center;background:{color}22;border:1px solid {color}44;"
                f"border-radius:8px;padding:0.4rem;margin-bottom:0.3rem'>"
                f"<div style='font-size:0.7rem;color:{COLORS['text2']}'>{day}</div>"
                f"<div>{emoji}</div></div>",
                unsafe_allow_html=True
            )
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:flex;gap:1.5rem;margin-top:0.5rem;">
        <span>🟢 Present</span>
        <span>🔴 Absent</span>
        <span>🟡 Late</span>
        <span>⚪ No class</span>
    </div>
    """, unsafe_allow_html=True)
