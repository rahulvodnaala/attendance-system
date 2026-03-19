import streamlit as st
from database import init_db, authenticate
from styles import CUSTOM_CSS
from admin_panel import render_admin
from faculty_panel import render_faculty
from student_panel import render_student

# ── Page Config ──
st.set_page_config(
    page_title="AttendAI — Smart Attendance System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Inject CSS ──
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Init DB ──
init_db()

# ── Session State ──
if "user" not in st.session_state:
    st.session_state.user = None

# ══════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════
def show_login():
    # Center the login form
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("""
        <div class="login-container">
            <div class="login-logo">
                <div class="login-logo-icon">📊</div>
                <h1 class="login-title">AttendAI</h1>
                <p class="login-subtitle">Smart Attendance Management System</p>
                <p style="font-size:0.75rem;color:#6366f1;margin-top:0.25rem;font-weight:600;">
                    BTech Minor Project — AI Powered
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("📧 Email Address", placeholder="your@college.edu")
            password = st.text_input("🔑 Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter email and password.")
            else:
                user = authenticate(email, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome, {user['name']}! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")

        st.markdown("""
        <div style="margin-top:1.5rem;padding:1rem;background:rgba(99,102,241,0.07);
                    border-radius:10px;border:1px solid rgba(99,102,241,0.15);">
            <p style="font-size:0.8rem;color:#94a3b8;margin:0 0 0.5rem 0;font-weight:600;
                      text-transform:uppercase;letter-spacing:0.05em;">Demo Credentials</p>
            <p style="font-size:0.78rem;color:#94a3b8;margin:0;">
                👨‍💼 <b style="color:#a5b4fc">Admin:</b> admin@college.edu / admin123<br>
                👩‍🏫 <b style="color:#a5b4fc">Faculty:</b> priya@college.edu / faculty123<br>
                🎓 <b style="color:#a5b4fc">Student:</b> arjun@student.edu / student123
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
def show_sidebar(user):
    with st.sidebar:
        # Profile
        role_icon = {"admin": "👨‍💼", "faculty": "👩‍🏫", "student": "🎓"}.get(user["role"], "👤")
        role_label = user["role"].capitalize()
        st.markdown(f"""
        <div style="padding:1.25rem;background:rgba(99,102,241,0.08);border-radius:14px;
                    border:1px solid rgba(99,102,241,0.2);margin-bottom:1.5rem;">
            <div style="font-size:2rem;margin-bottom:0.25rem">{role_icon}</div>
            <div style="color:#f1f5f9;font-weight:700;font-size:1rem">{user['name']}</div>
            <div style="display:inline-block;background:rgba(99,102,241,0.2);color:#a5b4fc;
                        padding:0.15rem 0.6rem;border-radius:999px;font-size:0.7rem;
                        font-weight:600;margin-top:0.3rem;text-transform:uppercase;">
                {role_label}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # App branding
        st.markdown("""
        <div style="text-align:center;margin-bottom:1.5rem;">
            <span style="font-size:1.3rem;font-weight:800;
                         background:linear-gradient(135deg,#6366f1,#8b5cf6);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                📊 AttendAI
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Logout
        st.markdown("<div style='flex-grow:1'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

        st.markdown("""
        <div style="margin-top:2rem;padding:0.75rem;background:rgba(6,182,212,0.05);
                    border:1px solid rgba(6,182,212,0.15);border-radius:10px;">
            <p style="font-size:0.72rem;color:#67e8f9;margin:0;font-weight:600;">
                🤖 AI Features Active
            </p>
            <p style="font-size:0.68rem;color:#94a3b8;margin:0.25rem 0 0;">
                Smart insights & predictions enabled
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top:1rem;font-size:0.65rem;color:#4b5563;text-align:center;">
            AttendAI v1.0 · BTech Minor Project<br>
            Built with Streamlit + SQLite
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════
def main():
    user = st.session_state.user

    if user is None:
        show_login()
        return

    show_sidebar(user)

    if user["role"] == "admin":
        render_admin()
    elif user["role"] == "faculty":
        render_faculty(user)
    elif user["role"] == "student":
        render_student(user)
    else:
        st.error("Unknown role.")


if __name__ == "__main__":
    main()
