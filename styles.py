CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --bg:         #ffffff;
    --bg2:        #f9f8f6;
    --bg3:        #f2f0ec;
    --card:       #ffffff;
    --border:     #e5e2db;
    --border2:    #d4d0c8;
    --accent:     #1a1a1a;
    --accent2:    #3d3d3d;
    --muted:      #8a8680;
    --muted2:     #b5b1a8;
    --text:       #1a1a1a;
    --text2:      #5a5652;
    --success:    #2d6a4f;
    --success-bg: #edf7f2;
    --warning:    #8b5e00;
    --warning-bg: #fef9ee;
    --danger:     #922b21;
    --danger-bg:  #fdf2f1;
    --shadow:     0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:  0 4px 12px rgba(0,0,0,0.08);
}

* { box-sizing: border-box; }

.stApp {
    background: var(--bg2) !important;
    font-family: 'Inter', sans-serif !important;
}

.main .block-container {
    padding: 0 2.5rem 4rem !important;
    max-width: 1300px !important;
}

#MainMenu, footer { visibility: hidden !important; }
.stDeployButton { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

h1, h2, h3, h4, h5, h6 {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
    font-weight: 600 !important;
}

/* ── Top Nav ── */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.25rem;
    background: var(--bg);
}
.top-nav-brand {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text) !important;
    letter-spacing: -0.01em;
}
.top-nav-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.top-nav-user {
    font-size: 0.82rem;
    color: var(--text2) !important;
    font-weight: 500;
}
.top-nav-role {
    background: var(--bg3);
    border: 1px solid var(--border);
    color: var(--muted) !important;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Page Header ── */
.page-header {
    margin-bottom: 1.75rem;
}
.page-header h1 {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    margin: 0 0 0.2rem 0 !important;
    letter-spacing: -0.03em;
}
.page-header p {
    font-size: 0.85rem;
    color: var(--muted) !important;
    margin: 0;
}

/* ── Metric Cards ── */
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.4rem 1.5rem;
    box-shadow: var(--shadow);
}
.metric-value {
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--text) !important;
    line-height: 1;
    margin-bottom: 0.2rem;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: -0.03em;
}
.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted) !important;
    font-weight: 500;
}

/* ── Section Header ── */
.section-header {
    margin: 1.75rem 0 1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}
.section-header h3 {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    margin: 0 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Info Cards ── */
.info-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.6rem;
    box-shadow: var(--shadow);
}

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.18rem 0.55rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-success { background: var(--success-bg); color: var(--success) !important; }
.badge-warning { background: var(--warning-bg); color: var(--warning) !important; }
.badge-danger  { background: var(--danger-bg);  color: var(--danger)  !important; }
.badge-neutral { background: var(--bg3); color: var(--text2) !important; }

/* ── Progress ── */
.att-progress-wrap {
    background: var(--bg3);
    border-radius: 2px;
    height: 3px;
    overflow: hidden;
    margin-top: 0.5rem;
}
.att-progress-bar { height: 100%; border-radius: 2px; transition: width 0.4s ease; }

/* ── Login ── */
.login-outer {
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 5vh;
}
.login-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 2.75rem 2.5rem;
    width: 100%;
    box-shadow: var(--shadow-md);
}
.login-brand {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text) !important;
    letter-spacing: -0.01em;
    margin-bottom: 2rem;
    display: block;
}
.login-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text) !important;
    margin: 0 0 0.2rem 0;
    letter-spacing: -0.02em;
}
.login-sub {
    font-size: 0.82rem;
    color: var(--muted) !important;
    margin: 0 0 1.75rem 0;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--accent) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.2rem !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.82 !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(26,26,26,0.07) !important;
}
label { color: var(--text2) !important; font-size: 0.82rem !important; font-weight: 500 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 0 !important;
    gap: 0 !important;
    margin-bottom: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.83rem !important;
    padding: 0.6rem 1.1rem !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--text) !important;
    border-bottom: 2px solid var(--accent) !important;
    font-weight: 600 !important;
    background: transparent !important;
}

/* ── DataFrames ── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden;
}

/* ── Radio ── */
.stRadio label { color: var(--text) !important; font-size: 0.85rem !important; }

/* ── Alerts ── */
.stAlert { border-radius: 6px !important; font-size: 0.85rem !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.25rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
</style>
"""
