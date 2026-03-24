CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@600;700;800&display=swap');

:root {
    --bg:            #f4f6fb;
    --bg2:           #eaecf4;
    --card:          #ffffff;
    --border:        #e2e6f0;
    --border2:       #cdd3e8;

    --admin:         #4f46e5;
    --admin-dark:    #3730a3;
    --admin-light:   #eef2ff;
    --admin-mid:     #c7d2fe;
    --admin-grad:    linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%);

    --faculty:       #0284c7;
    --faculty-dark:  #0369a1;
    --faculty-light: #e0f2fe;
    --faculty-mid:   #bae6fd;
    --faculty-grad:  linear-gradient(135deg,#0284c7 0%,#0891b2 100%);

    --student:       #059669;
    --student-dark:  #047857;
    --student-light: #ecfdf5;
    --student-mid:   #a7f3d0;
    --student-grad:  linear-gradient(135deg,#059669 0%,#0d9488 100%);

    --text:          #0f172a;
    --text2:         #475569;
    --muted:         #94a3b8;

    --success:       #059669;
    --success-bg:    #ecfdf5;
    --success-border:#a7f3d0;
    --warning:       #d97706;
    --warning-bg:    #fffbeb;
    --warning-border:#fde68a;
    --danger:        #dc2626;
    --danger-bg:     #fef2f2;
    --danger-border: #fecaca;

    --shadow-sm: 0 1px 3px rgba(15,23,42,0.07),0 1px 2px rgba(15,23,42,0.04);
    --shadow:    0 4px 16px rgba(15,23,42,0.09);
    --shadow-lg: 0 12px 40px rgba(15,23,42,0.14);
}

* { box-sizing: border-box; }
.stApp { background: var(--bg) !important; font-family: 'Inter', sans-serif !important; }
.main .block-container { padding: 0.5rem 2rem 1.25rem !important; max-width: 1350px !important; }
#MainMenu, footer { visibility: hidden !important; }
.stDeployButton { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
h1,h2,h3,h4,h5,h6 { font-family:'Sora',sans-serif !important; color:var(--text) !important; }

/* ── Landing ── */
.landing-outer {
    position: fixed;
    inset: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0.4rem 1rem;
    overflow: hidden;
}
.landing-logo-box { width:52px; height:52px; background:var(--admin-grad); border-radius:15px; display:flex; align-items:center; justify-content:center; margin:0 auto 1.5rem; box-shadow:0 8px 24px rgba(79,70,229,0.3); }
.landing-title { font-family:'Sora',sans-serif; font-size:1.9rem; font-weight:800; color:var(--text) !important; text-align:center; margin:0 0 0.45rem; letter-spacing:-0.04em; line-height:1.2; }
.landing-sub { font-size:0.9rem; color:var(--muted) !important; text-align:center; margin:0 0 2.75rem; }

.role-card { background:var(--card); border:1.5px solid var(--border); border-radius:20px; padding:2rem 1.5rem; text-align:center; cursor:pointer; transition:transform 0.22s,box-shadow 0.22s; box-shadow:var(--shadow-sm); height:100%; }
.role-card:hover { transform:translateY(-5px); box-shadow:var(--shadow-lg); }
.role-card-admin   { border-top:4px solid var(--admin); }
.role-card-faculty { border-top:4px solid var(--faculty); }
.role-card-student { border-top:4px solid var(--student); }

.role-icon-wrap { width:60px; height:60px; border-radius:18px; display:flex; align-items:center; justify-content:center; margin:0 auto 1rem; font-size:1.6rem; }
.role-icon-admin   { background:var(--admin-light); }
.role-icon-faculty { background:var(--faculty-light); }
.role-icon-student { background:var(--student-light); }

.role-card-title { font-family:'Sora',sans-serif; font-size:1.1rem; font-weight:700; margin:0 0 0.4rem; }
.role-title-admin   { color:var(--admin)   !important; }
.role-title-faculty { color:var(--faculty) !important; }
.role-title-student { color:var(--student) !important; }

.role-card-desc { font-size:0.79rem; color:var(--muted) !important; margin:0 0 1.5rem; line-height:1.55; }

.role-btn { display:block; width:100%; padding:0.65rem; border-radius:11px; font-size:0.82rem; font-weight:700; letter-spacing:0.02em; color:#fff !important; border:none; cursor:pointer; transition:opacity 0.15s,transform 0.1s; }
.role-btn:hover { opacity:0.88; transform:translateY(-1px); }
.role-btn-admin   { background:var(--admin-grad);   box-shadow:0 4px 16px rgba(79,70,229,0.38); }
.role-btn-faculty { background:var(--faculty-grad); box-shadow:0 4px 16px rgba(2,132,199,0.38); }
.role-btn-student { background:var(--student-grad); box-shadow:0 4px 16px rgba(5,150,105,0.38); }

/* ── Login ── */
.login-outer {
    position: fixed;
    inset: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: 0.5rem 0.9rem;
}
.login-card { background:var(--card); border:1px solid var(--border); border-radius:20px; padding:2.75rem 2.5rem; width:100%; box-shadow:var(--shadow-lg); }
.login-role-banner { border-radius:14px; padding:1.1rem 1.4rem; margin-bottom:1.75rem; display:flex; align-items:center; gap:1rem; }
.login-banner-admin   { background:var(--admin-light);   border:1px solid var(--admin-mid); }
.login-banner-faculty { background:var(--faculty-light); border:1px solid var(--faculty-mid); }
.login-banner-student { background:var(--student-light); border:1px solid var(--student-mid); }
.banner-icon { width:44px; height:44px; border-radius:13px; display:flex; align-items:center; justify-content:center; font-size:1.25rem; flex-shrink:0; }
.banner-icon-admin   { background:var(--admin);   }
.banner-icon-faculty { background:var(--faculty); }
.banner-icon-student { background:var(--student); }
.banner-title { font-family:'Sora',sans-serif; font-size:0.98rem; font-weight:700; margin:0 0 0.1rem; }
.banner-sub { font-size:0.76rem; color:var(--text2) !important; margin:0; }
.c-admin   { color:var(--admin)   !important; }
.c-faculty { color:var(--faculty) !important; }
.c-student { color:var(--student) !important; }

/* ── Top Nav ── */
.topnav { display:flex; align-items:center; justify-content:space-between; padding:0.9rem 0; border-bottom:1px solid var(--border); margin-bottom:2rem; }
.topnav-brand { font-family:'Sora',sans-serif; font-size:0.92rem; font-weight:700; color:var(--text) !important; }
.topnav-right { display:flex; align-items:center; gap:0.75rem; }
.topnav-name { font-size:0.82rem; font-weight:500; color:var(--text2) !important; }
.role-pill { padding:0.22rem 0.75rem; border-radius:999px; font-size:0.67rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; }
.role-pill-admin   { background:var(--admin-light);   color:var(--admin)   !important; border:1px solid var(--admin-mid);   }
.role-pill-faculty { background:var(--faculty-light); color:var(--faculty) !important; border:1px solid var(--faculty-mid); }
.role-pill-student { background:var(--student-light); color:var(--student) !important; border:1px solid var(--student-mid); }

/* ── Page Header ── */
.page-header { margin-bottom:1.75rem; padding-bottom:1.25rem; border-bottom:1px solid var(--border); }
.page-header h1 { font-size:1.55rem !important; font-weight:800 !important; color:var(--text) !important; margin:0 0 0.2rem !important; letter-spacing:-0.03em; }
.page-header p { font-size:0.83rem; color:var(--muted) !important; margin:0; }

/* ── Metric Cards ── */
.metric-card { background:var(--card); border:1px solid var(--border); border-radius:14px; padding:1.4rem 1.5rem; box-shadow:var(--shadow-sm); position:relative; overflow:hidden; }
.metric-bar { position:absolute; top:0; left:0; right:0; height:3px; border-radius:14px 14px 0 0; }
.metric-value { font-family:'Sora',sans-serif; font-size:2rem; font-weight:800; color:var(--text) !important; line-height:1; margin-bottom:0.2rem; letter-spacing:-0.03em; }
.metric-label { font-size:0.7rem; text-transform:uppercase; letter-spacing:0.08em; color:var(--muted) !important; font-weight:600; }

/* ── Section Header ── */
.section-header { margin:1.75rem 0 1rem; padding-bottom:0.6rem; border-bottom:1px solid var(--border); display:flex; align-items:center; gap:0.5rem; }
.section-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; display:inline-block; }
.section-header h3 { font-size:0.73rem !important; font-weight:700 !important; color:var(--text2) !important; margin:0 !important; text-transform:uppercase; letter-spacing:0.09em; }

/* ── Info Cards ── */
.info-card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:1.1rem 1.25rem; margin-bottom:0.6rem; box-shadow:var(--shadow-sm); }

/* ── Badges ── */
.badge { display:inline-block; padding:0.22rem 0.65rem; border-radius:6px; font-size:0.67rem; font-weight:700; letter-spacing:0.04em; text-transform:uppercase; }
.badge-success { background:var(--success-bg); color:var(--success) !important; border:1px solid var(--success-border); }
.badge-warning { background:var(--warning-bg); color:var(--warning) !important; border:1px solid var(--warning-border); }
.badge-danger  { background:var(--danger-bg);  color:var(--danger)  !important; border:1px solid var(--danger-border); }

/* ── Progress ── */
.att-progress-wrap { background:var(--bg2); border-radius:99px; height:5px; overflow:hidden; margin-top:0.5rem; }
.att-progress-bar  { height:100%; border-radius:99px; transition:width 0.4s ease; }

/* ── Streamlit overrides ── */
.stButton > button { background:var(--admin-grad) !important; color:#fff !important; border:none !important; border-radius:9px !important; font-family:'Inter',sans-serif !important; font-weight:600 !important; font-size:0.83rem !important; padding:0.52rem 1.25rem !important; transition:opacity 0.15s,transform 0.1s !important; box-shadow:0 2px 8px rgba(79,70,229,0.22) !important; }
.stButton > button:hover { opacity:0.88 !important; transform:translateY(-1px) !important; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input { background:var(--card) !important; border:1.5px solid var(--border2) !important; border-radius:9px !important; color:var(--text) !important; font-family:'Inter',sans-serif !important; font-size:0.875rem !important; padding:0.6rem 0.9rem !important; }
.stTextInput > div > div > input:focus { border-color:var(--admin) !important; box-shadow:0 0 0 3px rgba(79,70,229,0.1) !important; }
.stSelectbox > div > div { background:var(--card) !important; border:1.5px solid var(--border2) !important; border-radius:9px !important; color:var(--text) !important; font-family:'Inter',sans-serif !important; }
label { color:var(--text2) !important; font-size:0.8rem !important; font-weight:600 !important; }

.stTabs [data-baseweb="tab-list"] { background:var(--bg2) !important; border-radius:12px !important; padding:0.3rem !important; border:1px solid var(--border) !important; gap:0.2rem !important; margin-bottom:1.75rem !important; border-bottom:none !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:var(--muted) !important; font-family:'Inter',sans-serif !important; font-weight:500 !important; font-size:0.82rem !important; padding:0.5rem 1.1rem !important; border-radius:9px !important; border-bottom:none !important; }
.stTabs [aria-selected="true"] { background:var(--card) !important; color:var(--admin) !important; font-weight:700 !important; box-shadow:var(--shadow-sm) !important; border-bottom:none !important; }

.stDataFrame { border:1px solid var(--border) !important; border-radius:12px !important; overflow:hidden; box-shadow:var(--shadow-sm); }
.stRadio label { color:var(--text) !important; font-size:0.85rem !important; }
.stAlert { border-radius:10px !important; font-size:0.85rem !important; }
hr { border-color:var(--border) !important; margin:1.25rem 0 !important; }
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--border2); border-radius:3px; }
</style>
"""
