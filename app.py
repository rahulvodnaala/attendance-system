import streamlit as st
from database import init_db, authenticate
from styles import CUSTOM_CSS

st.set_page_config(
    page_title="Online Student Attendance Management System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
init_db()

if "user" not in st.session_state:
    st.session_state.user = None
if "login_role" not in st.session_state:
    st.session_state.login_role = "admin"


# ══════════════════════════════════════════════
# TOP NAV BAR (shown when logged in)
# ══════════════════════════════════════════════
def render_topnav(user):
    role_label = user["role"].capitalize()
    col_brand, col_right = st.columns([6, 1])
    with col_brand:
        st.markdown(f"""
        <div class="top-nav">
            <span class="top-nav-brand">Online Student Attendance Management System</span>
            <div class="top-nav-right">
                <span class="top-nav-user">{user['name']}</span>
                <span class="top-nav-role">{role_label}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_right:
        st.markdown("<div style='padding-top:0.6rem'>", unsafe_allow_html=True)
        if st.button("Sign Out", key="topnav_logout"):
            st.session_state.user = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════
def show_login():
    role = st.session_state.login_role

    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown('<div class="login-outer">', unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        st.markdown('<span class="login-brand">Online Student Attendance Management System</span>',
                    unsafe_allow_html=True)

        # Role selector tabs
        r1, r2, r3 = st.columns(3)
        with r1:
            if st.button("Admin", use_container_width=True,
                         type="primary" if role == "admin" else "secondary"):
                st.session_state.login_role = "admin"
                st.rerun()
        with r2:
            if st.button("Faculty", use_container_width=True,
                         type="primary" if role == "faculty" else "secondary"):
                st.session_state.login_role = "faculty"
                st.rerun()
        with r3:
            if st.button("Student", use_container_width=True,
                         type="primary" if role == "student" else "secondary"):
                st.session_state.login_role = "student"
                st.rerun()

        st.markdown("<div style='margin-top:1.5rem'>", unsafe_allow_html=True)
        st.markdown(f'<p class="login-title">{role.capitalize()} Login</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="login-sub">Sign in to your {role} account</p>', unsafe_allow_html=True)

        with st.form(f"login_{role}"):
            email    = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                user = authenticate(email, password)
                if user and user["role"] == role:
                    st.session_state.user = user
                    st.rerun()
                elif user and user["role"] != role:
                    st.error(f"This account is not a {role} account.")
                else:
                    st.error("Invalid email or password.")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
def main():
    user = st.session_state.user

    if user is None:
        show_login()
        return

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

if __name__ == "__main__":
    main()
