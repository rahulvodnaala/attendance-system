import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import (
    get_student_profile, get_student_attendance_summary,
    get_student_detailed_attendance, get_subjects
)

C = {
    "text": "#1a1a1a", "text2": "#5a5652", "muted": "#8a8680",
    "success": "#2d6a4f", "success_bg": "#edf7f2",
    "warning": "#8b5e00", "warning_bg": "#fef9ee",
    "danger": "#922b21", "danger_bg": "#fdf2f1",
    "border": "#e5e2db", "bg2": "#f9f8f6", "bg3": "#f2f0ec",
}

def _pct_color(p):
    if p >= 75: return C["success"]
    if p >= 60: return C["warning"]
    return C["danger"]

def _badge(p):
    if p >= 75:
        return f'<span class="badge badge-success">Safe</span>'
    if p >= 60:
        return f'<span class="badge badge-warning">Warning</span>'
    return f'<span class="badge badge-danger">Critical</span>'


def render_student(user):
    profile = get_student_profile(user["id"])
    if not profile:
        st.error("Student profile not found.")
        return

    st.markdown(f"""
    <div class="page-header">
        <h1>{profile['name']}</h1>
        <p>{profile['roll_number']} &nbsp;&middot;&nbsp; {profile['dept_name']}
           &nbsp;&middot;&nbsp; Semester {profile['semester']} &nbsp;&middot;&nbsp;
           Section {profile['section']}</p>
    </div>
    """, unsafe_allow_html=True)

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
        axis=1
    )

    overall     = round(df["pct"].mean(), 1)
    below_75    = int((df["pct"] < 75).sum())
    safe        = int((df["pct"] >= 75).sum())
    tot_present = int(df["present"].sum())
    tot_classes = int(df["total_classes"].sum())

    # Overall % hero
    col = _pct_color(overall)
    st.markdown(f"""
    <div class="info-card" style="text-align:center;padding:2rem 1.5rem;margin-bottom:1.5rem;">
        <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;
                    color:{C['muted']};margin-bottom:0.5rem;font-weight:600;">
            Overall Attendance
        </div>
        <div style="font-size:3.5rem;font-weight:700;color:{col};
                    line-height:1;font-family:'DM Sans',sans-serif;letter-spacing:-0.03em;">
            {overall}%
        </div>
        <div style="margin-top:0.6rem">{_badge(overall)}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{C['success']}">{safe}</div>
            <div class="metric-label">Safe Subjects</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{C['danger']}">{below_75}</div>
            <div class="metric-label">Below 75%</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{tot_present}/{tot_classes}</div>
            <div class="metric-label">Classes Attended</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Subject-wise bars
    st.markdown("""<div class="section-header"><h3>Subject-wise Breakdown</h3></div>""",
                unsafe_allow_html=True)

    for _, row in df.iterrows():
        p    = row["pct"]
        col  = _pct_color(p)
        barw = max(0, min(100, p))
        st.markdown(f"""
        <div class="info-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem">
                <div>
                    <span style="font-size:0.85rem;font-weight:600;color:{C['text']}">{row['code']}</span>
                    <span style="font-size:0.8rem;color:{C['muted']};margin-left:0.5rem">{row['subject']}</span>
                </div>
                <span style="font-size:1rem;font-weight:700;color:{col};font-family:'DM Sans',sans-serif">{p}%</span>
            </div>
            <div class="att-progress-wrap">
                <div class="att-progress-bar" style="width:{barw}%;background:{col}"></div>
            </div>
            <div style="display:flex;gap:1.25rem;margin-top:0.5rem;font-size:0.72rem;color:{C['muted']}">
                <span>Present: {row['present']}</span>
                <span>Absent: {row['absent']}</span>
                <span>Late: {row['late']}</span>
                <span>Total: {row['total_classes']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Classes needed calculator
    needs = [(row["code"], row["subject"], row["pct"], row["present"], row["total_classes"])
             for _, row in df.iterrows() if row["pct"] < 75 and row["total_classes"] > 0]

    if needs:
        st.markdown("""<div class="section-header"><h3>Classes Required to Reach 75%</h3></div>""",
                    unsafe_allow_html=True)
        for code, name, pct, present, total in needs:
            needed = max(0, int((0.75 * total - present) / 0.25) + 1)
            st.markdown(f"""
            <div class="info-card" style="border-left:3px solid {C['warning']};">
                <span style="font-weight:600;color:{C['text']};font-size:0.85rem">{code}</span>
                <span style="color:{C['muted']};font-size:0.82rem;margin-left:0.5rem">{name}</span>
                <br>
                <span style="font-size:0.82rem;color:{C['text2']}">
                    Attend <b style="color:{C['warning']}">{needed} consecutive class(es)</b> to reach 75%
                </span>
            </div>
            """, unsafe_allow_html=True)


# ── Subject Detail ────────────────────────────
def _subject_tab(profile):
    st.markdown("""<div class="section-header"><h3>Subject Detail</h3></div>""",
                unsafe_allow_html=True)

    subjects = get_subjects(dept_id=profile["department_id"], semester=profile["semester"])
    if not subjects:
        st.info("No subjects found.")
        return

    opts = ["Select subject"] + [f"{s['code']} — {s['name']}" for s in subjects]
    sel  = st.selectbox("Subject", opts)
    if sel == "Select subject":
        return

    idx     = opts.index(sel) - 1
    subject = subjects[idx]
    records = get_student_detailed_attendance(profile["id"], subject["id"])

    if not records:
        st.info("No attendance records for this subject yet.")
        return

    df = pd.DataFrame(records)
    df["status"] = df["status"].fillna("not marked")

    total   = len(df)
    present = int((df["status"] == "present").sum())
    absent  = int((df["status"] == "absent").sum())
    late    = int((df["status"] == "late").sum())
    pct     = round(present / total * 100, 1) if total > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Classes", total)
    c2.metric("Present", present)
    c3.metric("Absent", absent)
    c4.metric("Attendance %", f"{pct}%")

    # Timeline scatter
    scmap = {"present": C["success"], "absent": C["danger"],
             "late": C["warning"], "not marked": C["muted"]}
    fig = go.Figure()
    for status, color in scmap.items():
        mask = df["status"] == status
        if mask.any():
            fig.add_trace(go.Scatter(
                x=df[mask]["date"], y=[status.capitalize()] * mask.sum(),
                mode="markers",
                marker=dict(size=12, color=color, symbol="square"),
                name=status.capitalize(),
                hovertemplate="%{x}<extra></extra>"
            ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=C["muted"]),
        margin=dict(l=10, r=10, t=36, b=10),
        height=180,
        title=dict(text="Attendance Timeline", font=dict(size=12, color=C["text"])),
        xaxis=dict(gridcolor="rgba(0,0,0,0.04)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0.04)"),
        showlegend=True,
        legend=dict(font=dict(color=C["muted"], size=11))
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Records table
    disp = df.rename(columns={"date": "Date", "status": "Status", "topic": "Topic"})
    disp["Status"] = disp["Status"].apply(
        lambda s: "Present" if s == "present" else (
            "Absent" if s == "absent" else ("Late" if s == "late" else "—"))
    )
    st.dataframe(disp[["Date", "Status", "Topic"]], use_container_width=True, hide_index=True)


# ── Calendar ──────────────────────────────────
def _calendar_tab(profile):
    st.markdown("""<div class="section-header"><h3>Monthly Calendar</h3></div>""",
                unsafe_allow_html=True)

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
        st.info("No data available.")
        return

    df = pd.DataFrame(rows, columns=["date", "subject", "status"])
    df["date"]   = pd.to_datetime(df["date"])
    df["status"] = df["status"].fillna("not marked")
    df["day"]    = df["date"].dt.day
    df["month"]  = df["date"].dt.strftime("%B %Y")

    months = df["month"].unique()[:3]

    for month in months:
        st.markdown(f"<p style='font-size:0.8rem;font-weight:600;color:{C['muted']};text-transform:uppercase;"
                    f"letter-spacing:0.07em;margin:1rem 0 0.5rem'>{month}</p>", unsafe_allow_html=True)
        mdf  = df[df["month"] == month]
        days = sorted(mdf["day"].unique())

        day_summary = {}
        for day in days:
            statuses = mdf[mdf["day"] == day]["status"].tolist()
            if "absent" in statuses:
                day_summary[day] = (C["danger"], "danger_bg", "A")
            elif "late" in statuses:
                day_summary[day] = (C["warning"], "warning_bg", "L")
            elif "present" in statuses:
                day_summary[day] = (C["success"], "success_bg", "P")
            else:
                day_summary[day] = (C["muted"], "bg3", "—")

        cols = st.columns(min(len(day_summary), 10))
        for i, (day, (color, bg, label)) in enumerate(day_summary.items()):
            with cols[i % 10]:
                st.markdown(
                    f"<div style='text-align:center;border:1px solid {color}44;"
                    f"border-radius:6px;padding:0.35rem 0.25rem;margin-bottom:0.3rem;background:{color}11'>"
                    f"<div style='font-size:0.65rem;color:{C['muted']}'>{day}</div>"
                    f"<div style='font-size:0.75rem;font-weight:600;color:{color}'>{label}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    st.markdown(f"""
    <div style="display:flex;gap:1.5rem;margin-top:1rem;font-size:0.78rem;color:{C['muted']}">
        <span style="color:{C['success']}">P — Present</span>
        <span style="color:{C['danger']}">A — Absent</span>
        <span style="color:{C['warning']}">L — Late</span>
        <span>— — No class</span>
    </div>
    """, unsafe_allow_html=True)
