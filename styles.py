CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root Tokens ── */
:root {
    --bg-primary: #0a0f1e;
    --bg-card: #111827;
    --bg-card2: #1a2236;
    --accent: #6366f1;
    --accent2: #8b5cf6;
    --accent3: #06b6d4;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --border: rgba(99,102,241,0.2);
    --glow: 0 0 20px rgba(99,102,241,0.3);
}

/* ── Global ── */
.stApp {
    background: var(--bg-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

.main .block-container {
    padding: 1.5rem 2.5rem 3rem !important;
    max-width: 1400px !important;
}

/* ── Hide Streamlit Branding ── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0d1424 0%, #111827 100%) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

/* ── Typography ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-primary) !important;
}

p, label, span, div {
    color: var(--text-secondary);
}

/* ── Metric Cards ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    border-radius: 16px 16px 0 0;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--glow);
}
.metric-value {
    font-size: 2.4rem;
    font-weight: 700;
    color: var(--text-primary) !important;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.metric-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-secondary) !important;
    font-weight: 500;
}
.metric-icon {
    font-size: 2rem;
    margin-bottom: 0.75rem;
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1a1f3a 0%, #0d1424 50%, #1a1f3a 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary) !important;
    margin: 0 0 0.3rem 0;
}
.hero-subtitle {
    font-size: 1rem;
    color: var(--text-secondary) !important;
    margin: 0;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    color: #a5b4fc !important;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
    text-transform: uppercase;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
}
.section-header h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary) !important;
    margin: 0;
}

/* ── Attendance Badge ── */
.att-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
}
.att-high { background: rgba(16,185,129,0.15); color: #34d399 !important; border: 1px solid rgba(16,185,129,0.3); }
.att-mid  { background: rgba(245,158,11,0.15); color: #fbbf24 !important; border: 1px solid rgba(245,158,11,0.3); }
.att-low  { background: rgba(239,68,68,0.15);  color: #f87171 !important; border: 1px solid rgba(239,68,68,0.3); }

/* ── Streamlit components overrides ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    padding: 0.55rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
}

.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

/* ── DataFrames ── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 0.25rem !important;
    border: 1px solid var(--border) !important;
    gap: 0.25rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--text-secondary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
}

/* ── Alerts ── */
.stAlert {
    border-radius: 12px !important;
    border-left: 4px solid !important;
}

/* ── Radio ── */
.stRadio > div {
    gap: 0.5rem !important;
}
.stRadio label {
    color: var(--text-primary) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

/* ── Sidebar Radio Nav ── */
.sidebar-nav-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.65rem 1rem;
    border-radius: 10px;
    cursor: pointer;
    color: var(--text-secondary) !important;
    font-weight: 500;
    font-size: 0.9rem;
    transition: all 0.15s;
    margin-bottom: 0.25rem;
}
.sidebar-nav-item:hover, .sidebar-nav-item.active {
    background: rgba(99,102,241,0.12);
    color: var(--text-primary) !important;
    border-left: 2px solid var(--accent);
    padding-left: calc(1rem - 2px);
}

/* ── Login Page ── */
.login-container {
    max-width: 440px;
    margin: 3rem auto;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 3rem 2.5rem;
    box-shadow: 0 25px 60px rgba(0,0,0,0.5), var(--glow);
}
.login-logo {
    text-align: center;
    margin-bottom: 2rem;
}
.login-logo-icon {
    font-size: 3rem;
    margin-bottom: 0.5rem;
}
.login-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-primary) !important;
    margin: 0;
}
.login-subtitle {
    font-size: 0.85rem;
    color: var(--text-secondary) !important;
    margin: 0.25rem 0 0;
}

/* ── Status Dots ── */
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}
.dot-present { background: var(--success); }
.dot-absent  { background: var(--danger); }
.dot-late    { background: var(--warning); }

/* ── Info Cards ── */
.info-card {
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
}

/* ── Progress Bar ── */
.att-progress-wrap {
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
    margin-top: 0.4rem;
}
.att-progress-bar {
    height: 100%;
    border-radius: 999px;
    transition: width 0.5s ease;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Checkbox group for attendance marking ── */
.att-mark-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 1rem;
    background: var(--bg-card2);
    border-radius: 10px;
    margin-bottom: 0.4rem;
    border: 1px solid var(--border);
}
</style>
"""
