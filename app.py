import streamlit as st
from database import init_db, authenticate
from styles import CUSTOM_CSS

st.set_page_config(
    page_title="Online Student Attendance Management System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
init_db()

if "user"       not in st.session_state: st.session_state.user       = None
if "login_role" not in st.session_state: st.session_state.login_role = None   # None = show landing


# ══════════════════════════════════════════════
# LANDING — 3 role cards
# ══════════════════════════════════════════════
def show_landing():
    st.markdown('<div class="landing-outer">', unsafe_allow_html=True)

    # Logo + heading
    st.markdown("""
    <div class="landing-logo-box">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2"
             stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
        </svg>
    </div>
    <h1 class="landing-title">Online Student Attendance<br>Management System</h1>
    <p class="landing-sub">Select your role to continue</p>
    """, unsafe_allow_html=True)

    # Role cards using columns + Streamlit buttons
    _, c1, c2, c3, _ = st.columns([0.5, 1, 1, 1, 0.5])

    with c1:
        st.markdown("""
        <div class="role-card role-card-admin">
            <div class="role-icon-wrap role-icon-admin">🏛️</div>
            <div class="role-card-title role-title-admin">Admin</div>
            <div class="role-card-desc">Manage students, faculty, subjects and view system-wide reports.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Admin Login", key="go_admin", use_container_width=True):
            st.session_state.login_role = "admin"
            st.rerun()

    with c2:
        st.markdown("""
        <div class="role-card role-card-faculty">
            <div class="role-icon-wrap role-icon-faculty">👩‍🏫</div>
            <div class="role-card-title role-title-faculty">Faculty</div>
            <div class="role-card-desc">Mark subject-wise attendance, edit records and generate reports.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Faculty Login", key="go_faculty", use_container_width=True):
            st.session_state.login_role = "faculty"
            st.rerun()

    with c3:
        st.markdown("""
        <div class="role-card role-card-student">
            <div class="role-icon-wrap role-icon-student">🎓</div>
            <div class="role-card-title role-title-student">Student</div>
            <div class="role-card-desc">View your attendance subject-wise, track progress and calendar.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Student Login", key="go_student", use_container_width=True):
            st.session_state.login_role = "student"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# LOGIN PAGE  (per role, with colored banner)
# ══════════════════════════════════════════════
ROLE_META = {
    "admin":   {"icon": "🏛️", "label": "Admin",   "sub": "System administrator access",      "c": "admin",   "banner": "login-banner-admin",   "bicon": "banner-icon-admin"},
    "faculty": {"icon": "👩‍🏫", "label": "Faculty", "sub": "Faculty member access",            "c": "faculty", "banner": "login-banner-faculty", "bicon": "banner-icon-faculty"},
    "student": {"icon": "🎓", "label": "Student", "sub": "Student portal access",             "c": "student", "banner": "login-banner-student", "bicon": "banner-icon-student"},
}

def show_login(role: str):
    m = ROLE_META[role]
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown('<div class="login-outer">', unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        # Back button
        if st.button("← Back", key="back_btn"):
            st.session_state.login_role = None
            st.rerun()

        # Colored role banner
        st.markdown(f"""
        <div class="login-role-banner {m['banner']}">
            <div class="banner-icon {m['bicon']}">{m['icon']}</div>
            <div>
                <div class="banner-title c-{m['c']}">{m['label']} Login</div>
                <div class="banner-sub">{m['sub']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form(f"login_form_{role}"):
            email    = st.text_input("Email Address", placeholder="your@college.edu")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                user = authenticate(email, password)
                if user and user["role"] == role:
                    st.session_state.user = user
                    st.session_state.login_role = None
                    st.rerun()
                elif user and user["role"] != role:
                    st.error(f"This account does not have {role} access.")
                else:
                    st.error("Invalid email or password. Please try again.")

        st.markdown('</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TOP NAV (when logged in)
# ══════════════════════════════════════════════
def render_topnav(user):
    role = user["role"]
    col_left, col_right = st.columns([5, 1])
    with col_left:
        st.markdown(f"""
        <div class="topnav">
            <span class="topnav-brand">Online Student Attendance Management System</span>
            <div class="topnav-right">
                <span class="topnav-name">{user['name']}</span>
                <span class="role-pill role-pill-{role}">{role}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_right:
        st.markdown("<div style='padding-top:0.75rem'>", unsafe_allow_html=True)
        if st.button("Sign Out", key="signout_top"):
            st.session_state.user = None
            st.session_state.login_role = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════
def main():
    user = st.session_state.user

    # Logged in → show dashboard
    if user:
        render_topnav(user)
        if user["role"] == "admin":
            from admin_panel import render_admin
            render_admin()
        elif user["role"] == "faculty":
            from faculty_panel import render_faculty
            render_faculty(user)
        elif user["role"] == "student":
            from student_panel import render_student
            render_student(user)
        return

    # Not logged in
    role = st.session_state.login_role
    if role is None:
        show_landing()
    else:
        show_login(role)

if __name__ == "__main__":
    main()
