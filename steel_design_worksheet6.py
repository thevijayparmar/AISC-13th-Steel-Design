"""
AISC 13th Edition – Wide-Flange Beam / Column Design (ASD)
Structured Design and Consulting  |  v6
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import io
import re
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AISC 13th – Steel Beam Design (ASD)",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
  --navy:#0F2340; --blue:#1E3A5F; --accent:#2563EB;
  --yellow-bg:#FFFDE7; --yellow-bdr:#F9A825;
  --pass-bg:#d1fae5; --pass-fg:#065f46; --pass-bdr:#6ee7b7;
  --fail-bg:#fee2e2; --fail-fg:#991b1b; --fail-bdr:#fca5a5;
  --warn-bg:#fef3c7; --warn-fg:#92400e; --warn-bdr:#fcd34d;
  --card-bg:#f8faff; --card-bdr:#c7d7ef; --muted:#6B7E9C;
  --mono:'IBM Plex Mono',monospace;
}
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif;}

/* Sidebar */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0F2340,#1E3A5F);border-right:1px solid #2a4a70;}
[data-testid="stSidebar"] *{color:#e0eaf8!important;}
[data-testid="stSidebar"] input,[data-testid="stSidebar"] select{background:rgba(255,255,255,.08)!important;color:white!important;border:1px solid rgba(255,255,255,.18)!important;}
[data-testid="stSidebar"] .stButton>button{background:rgba(37,99,235,.25)!important;color:white!important;border:1px solid rgba(37,99,235,.5)!important;border-radius:6px!important;font-size:.78rem!important;font-weight:600!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:#2563EB!important;}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.12)!important;}

/* Section header */
.sec-header{font-size:.72rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:var(--blue);border-bottom:2px solid var(--blue);padding-bottom:5px;margin:28px 0 14px;}

/* Properties display table (read-only) */
.prop-table{width:100%;border-collapse:collapse;margin-bottom:6px;}
.prop-table th{background:#1E3A5F;color:white;padding:7px 6px;text-align:center;font-size:.68rem;letter-spacing:.06em;text-transform:uppercase;border:1px solid #16304f;white-space:nowrap;}
.prop-table th small{display:block;font-size:.58rem;font-weight:400;color:#93C5FD;text-transform:none;margin-top:1px;}
.prop-table td{border:1px solid #c7d7ef;padding:6px 6px;text-align:center;font-family:var(--mono);font-size:.82rem;color:var(--blue);background:#f8faff;white-space:nowrap;}

/* Input grid — the key fix: pure CSS grid so headers and inputs are perfectly aligned */
.inp-grid{display:grid;grid-template-columns:repeat(11,1fr);border:1.5px solid #1E3A5F;border-radius:8px;overflow:hidden;margin:0 0 4px;}
.inp-cell{display:flex;flex-direction:column;border-right:1px solid #2a4a70;}
.inp-cell:last-child{border-right:none;}
.inp-hdr{background:#1E3A5F;color:white;padding:7px 4px 5px;text-align:center;font-size:.65rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;line-height:1.2;}
.inp-hdr sub{font-size:.58rem;color:#93C5FD;}
.inp-unit{background:#162d4a;color:#93C5FD;font-size:.58rem;text-align:center;padding:2px 0;}
.inp-note{background:#f8f9fa;color:#6B7E9C;font-size:.58rem;text-align:center;padding:4px 3px;line-height:1.3;border-top:1px solid #e2eaf5;min-height:42px;}

/* Streamlit widget overrides for the input row */
.inp-widget .stNumberInput>div>div>input,
.inp-widget .stSelectbox>div>div>div{
  border-radius:0!important; border:none!important;
  border-bottom:2px solid var(--yellow-bdr)!important;
  background:var(--yellow-bg)!important;
  font-family:var(--mono)!important;
  font-size:.85rem!important; font-weight:600!important;
  color:#1E3A5F!important; text-align:center!important;
  padding:6px 4px!important;
}
.inp-widget .stNumberInput>div>div,
.inp-widget .stSelectbox>div>div{background:var(--yellow-bg)!important;}
.inp-widget label{display:none!important;}
.inp-widget .stNumberInput button{background:var(--yellow-bg)!important;border:none!important;}
div[data-testid="stNumberInputContainer"]{background:var(--yellow-bg)!important;}

/* Metric cards */
.metric-card{background:linear-gradient(135deg,#f8faff,#eef3fb);border:1.5px solid var(--card-bdr);border-radius:14px;padding:18px 14px 14px;text-align:center;position:relative;overflow:hidden;box-shadow:0 2px 8px rgba(30,58,95,.07);transition:box-shadow .2s,transform .15s;}
.metric-card:hover{box-shadow:0 6px 20px rgba(30,58,95,.14);transform:translateY(-2px);}
.metric-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--accent);}
.mc-pass::before{background:#10B981;} .mc-fail::before{background:#EF4444;} .mc-warn::before{background:#F59E0B;}
.mc-pass{border-color:var(--pass-bdr);background:linear-gradient(135deg,#f0fdf4,#dcfce7);}
.mc-fail{border-color:var(--fail-bdr);background:linear-gradient(135deg,#fff5f5,#fee2e2);}
.mc-label{font-size:.65rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;}
.mc-value{font-size:1.9rem;font-weight:700;color:var(--blue);font-family:var(--mono);line-height:1.1;}
.mc-sub{font-size:.66rem;color:var(--muted);margin-top:4px;}
.mc-badge{display:inline-block;margin-top:8px;padding:3px 12px;border-radius:20px;font-size:.7rem;font-weight:700;}
.badge-pass{background:var(--pass-bg);color:var(--pass-fg);}
.badge-fail{background:var(--fail-bg);color:var(--fail-fg);}
.badge-warn{background:var(--warn-bg);color:var(--warn-fg);}
.gauge-track{height:6px;border-radius:3px;background:rgba(30,58,95,.1);overflow:hidden;margin:7px 0 3px;}
.gf-pass{height:100%;border-radius:3px;background:linear-gradient(90deg,#10B981,#34D399);}
.gf-warn{height:100%;border-radius:3px;background:linear-gradient(90deg,#F59E0B,#FCD34D);}
.gf-fail{height:100%;border-radius:3px;background:linear-gradient(90deg,#EF4444,#F87171);}

/* Banners */
.banner-pass{background:linear-gradient(90deg,#d1fae5,#ecfdf5);border-left:5px solid #059669;color:#064e3b;padding:16px 22px;border-radius:10px;font-size:1.05rem;font-weight:700;margin:14px 0;}
.banner-fail{background:linear-gradient(90deg,#fee2e2,#fff1f2);border-left:5px solid #dc2626;color:#7f1d1d;padding:16px 22px;border-radius:10px;font-size:1.05rem;font-weight:700;margin:14px 0;}

/* Calc steps */
.calc-step{display:flex;align-items:center;background:linear-gradient(90deg,#EEF4FF,transparent);border-left:3px solid var(--accent);padding:8px 14px;border-radius:0 8px 8px 0;margin:20px 0 10px;font-weight:700;color:var(--blue);font-size:.95rem;}
.step-num{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;background:var(--accent);color:white;font-size:.7rem;font-weight:700;margin-right:8px;flex-shrink:0;font-family:var(--mono);}

/* Example cases panel */
.ex-card{background:#f8faff;border:1.5px solid #c7d7ef;border-radius:10px;padding:12px 14px;cursor:pointer;transition:all .15s;}
.ex-card:hover{border-color:#2563EB;background:#EEF4FF;}
.ex-card .ec-name{font-weight:700;color:#1E3A5F;font-size:.88rem;font-family:var(--mono);}
.ex-card .ec-desc{font-size:.7rem;color:#6B7E9C;margin-top:2px;}
.ex-card .ec-tag{display:inline-block;font-size:.6rem;font-weight:700;padding:1px 6px;border-radius:3px;margin-top:4px;}
.tag-beam{background:#dbeafe;color:#1e3a8a;}
.tag-col{background:#fce7f3;color:#9d174d;}
.tag-combo{background:#fef3c7;color:#92400e;}

/* Chips */
.cg{background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:4px;font-size:.82rem;font-family:var(--mono);}
.cb{background:#dbeafe;color:#1e3a8a;padding:2px 8px;border-radius:4px;font-size:.82rem;font-weight:700;font-family:var(--mono);}
.cr{background:#f1f5f9;color:#64748b;padding:2px 7px;border-radius:4px;font-size:.68rem;font-style:italic;}

#sdc-credit{position:fixed;bottom:14px;left:14px;background:rgba(255,255,255,.92);color:#555;font-size:10.5px;padding:4px 11px;border-radius:20px;border:1px solid #ddd;z-index:9999;}
@media print{[data-testid="stSidebar"],.stButton,.stFileUploader,.stDownloadButton,#sdc-credit{display:none!important;}}
</style>
<div id="sdc-credit">© Structured Design and Consulting</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────
E_STEEL=29000.0; OMEGA_B=1.67; OMEGA_V=1.67; OMEGA_C=1.67

SECTION_TYPES={
    "W":("W-Shape (Wide Flange)","I-section"),"S":("S-Shape (American Standard)","I-section"),
    "M":("M-Shape (Misc. I)","I-section"),"HP":("HP-Shape (Bearing Pile)","I-section"),
    "C":("C-Shape (Channel)","C-section"),"MC":("MC-Shape (Misc. Channel)","C-section"),
    "L":("L-Shape (Angle)","L-section"),"HSS":("HSS (Hollow Structural)","HSS"),
    "P":("Pipe","Pipe"),"WT":("WT-Shape (Tee)","T-section"),
    "ST":("ST-Shape (Tee)","T-section"),"MT":("MT-Shape (Misc. Tee)","T-section"),
}

PROP_TIPS={"A":"Cross-sectional area (in²)","d":"Nominal depth (in)","tw":"Web thickness (in)",
           "bf":"Flange width (in)","tf":"Flange thickness (in)","Ix":"Moment of inertia X-X (in⁴)",
           "Iy":"Moment of inertia Y-Y (in⁴)","Sx":"Elastic section modulus X-X (in³)",
           "Sy":"Elastic section modulus Y-Y (in³)","Zx":"Plastic section modulus X-X (in³)",
           "Zy":"Plastic section modulus Y-Y (in³)"}

# ─────────────────────────────────────────────────────────────
#  10 PRELOADED EXAMPLE CASES  (validated against Excel PDF)
# ─────────────────────────────────────────────────────────────
EXAMPLE_CASES = [
    {   # Case 1 — exactly from the PDF (W21X50, elastic LTB → governs)
        "name":"W21X50 — Beam Only (Elastic LTB)",
        "desc":"Lb=54.5 ft exceeds Lr. Elastic LTB governs. Shear & bearing pass.",
        "tag":"tag-beam",
        "beam_designation":"W21X50",
        "Lb_y":54.5,"Lb_x":54.5,"Fy":50.0,"Cb":1.0,"K":1.0,
        "Pa":0.0,"Ma":141.31,"Va":7.20,"Ra":7.20,"N_bearing":1.0,"bending_dir":"strong",
    },
    {   # Case 2 — W18X35, short span, plastic zone, beam only
        "name":"W18X35 — Short Span (Plastic)",
        "desc":"Lb=8 ft < Lp. Full plastic moment. Shear controls utilization.",
        "tag":"tag-beam",
        "beam_designation":"W18X35",
        "Lb_y":8.0,"Lb_x":8.0,"Fy":50.0,"Cb":1.0,"K":1.0,
        "Pa":0.0,"Ma":110.0,"Va":25.0,"Ra":25.0,"N_bearing":3.0,"bending_dir":"strong",
    },
    {   # Case 3 — W14X48, inelastic LTB
        "name":"W14X48 — Inelastic LTB",
        "desc":"Lb between Lp and Lr. Inelastic lateral-torsional buckling zone.",
        "tag":"tag-beam",
        "beam_designation":"W14X48",
        "Lb_y":12.0,"Lb_x":12.0,"Fy":50.0,"Cb":1.0,"K":1.0,
        "Pa":0.0,"Ma":95.0,"Va":18.0,"Ra":18.0,"N_bearing":2.0,"bending_dir":"strong",
    },
    {   # Case 4 — W10X49, column buckling, high axial
        "name":"W10X49 — Column (High Axial)",
        "desc":"K=1.0, KL/r moderate. Axial compression governs. Inelastic Fcr.",
        "tag":"tag-col",
        "beam_designation":"W10X49",
        "Lb_y":14.0,"Lb_x":14.0,"Fy":50.0,"Cb":1.0,"K":1.0,
        "Pa":180.0,"Ma":20.0,"Va":5.0,"Ra":5.0,"N_bearing":2.0,"bending_dir":"strong",
    },
    {   # Case 5 — W12X65, beam-column combined
        "name":"W12X65 — Beam-Column (Combined)",
        "desc":"Pa/Pc ≥ 0.2. AISC H1-1a governs. Combined ratio near limit.",
        "tag":"tag-combo",
        "beam_designation":"W12X65",
        "Lb_y":16.0,"Lb_x":16.0,"Fy":50.0,"Cb":1.0,"K":1.0,
        "Pa":120.0,"Ma":80.0,"Va":15.0,"Ra":15.0,"N_bearing":2.5,"bending_dir":"strong",
    },
    {   # Case 6 — W24X76, heavy beam
        "name":"W24X76 — Heavy Floor Beam",
        "desc":"High moment demand. Inelastic LTB zone. Bearing check relevant.",
        "tag":"tag-beam",
        "beam_designation":"W24X76",
        "Lb_y":20.0,"Lb_x":20.0,"Fy":50.0,"Cb":1.0,"K":1.0,
        "Pa":0.0,"Ma":320.0,"Va":40.0,"Ra":40.0,"N_bearing":3.5,"bending_dir":"strong",
    },
    {   # Case 7 — W8X31, short col, fixed-fixed
        "name":"W8X31 — Short Column (Fixed-Fixed)",
        "desc":"K=0.5, short unbraced length. Very low KL/r. Axial passes easily.",
        "tag":"tag-col",
        "beam_designation":"W8X31",
        "Lb_y":10.0,"Lb_x":10.0,"Fy":36.0,"Cb":1.0,"K":0.5,
        "Pa":90.0,"Ma":5.0,"Va":2.0,"Ra":2.0,"N_bearing":1.5,"bending_dir":"strong",
    },
    {   # Case 8 — W16X40, A36 steel
        "name":"W16X40 — A36 Steel Beam",
        "desc":"Fy=36 ksi. Wider plastic/inelastic zones. Verify Lp and Lr shift.",
        "tag":"tag-beam",
        "beam_designation":"W16X40",
        "Lb_y":15.0,"Lb_x":15.0,"Fy":36.0,"Cb":1.0,"K":1.0,
        "Pa":0.0,"Ma":85.0,"Va":20.0,"Ra":20.0,"N_bearing":2.0,"bending_dir":"strong",
    },
    {   # Case 9 — W21X50, higher Cb, elastic LTB
        "name":"W21X50 — Cb=1.67 (Non-uniform Moment)",
        "desc":"Same as Case 1 but Cb=1.67. LTB capacity improves significantly.",
        "tag":"tag-beam",
        "beam_designation":"W21X50",
        "Lb_y":54.5,"Lb_x":54.5,"Fy":50.0,"Cb":1.67,"K":1.0,
        "Pa":0.0,"Ma":141.31,"Va":7.20,"Ra":7.20,"N_bearing":1.0,"bending_dir":"strong",
    },
    {   # Case 10 — W33X130, large girder beam-column
        "name":"W33X130 — Large Girder Beam-Column",
        "desc":"Large section, moderate axial + large moment. H1-1b governs (Pa/Pc<0.2).",
        "tag":"tag-combo",
        "beam_designation":"W33X130",
        "Lb_y":25.0,"Lb_x":25.0,"Fy":50.0,"Cb":1.0,"K":1.0,
        "Pa":50.0,"Ma":600.0,"Va":55.0,"Ra":55.0,"N_bearing":4.0,"bending_dir":"strong",
    },
]

# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────
def gchip(v,u=""): return f'<span class="cg">{v}{" "+u if u else ""}</span>'
def bchip(v,u=""): return f'<span class="cb">{v}{" "+u if u else ""}</span>'
def rbadge(t):     return f'<span class="cr">{t}</span>'
def pass_html(l):  return f'<b style="color:#059669">{l} ✅</b>'
def fail_html(l):  return f'<b style="color:#dc2626">{l} ❌</b>'
def gauge_cls(p):  return "gf-pass" if p<=70 else "gf-warn" if p<=90 else "gf-fail"

def section_svg(st_):
    s={"I-section":'<svg viewBox="0 0 100 120" width="72" height="86"><rect x="15" y="8" width="70" height="12" fill="#1E3A5F" rx="2"/><rect x="44" y="20" width="12" height="68" fill="#2563EB"/><rect x="15" y="88" width="70" height="12" fill="#1E3A5F" rx="2"/><text x="50" y="115" text-anchor="middle" font-size="9" fill="#6B7E9C" font-family="IBM Plex Sans">I/W/S</text></svg>',
       "C-section":'<svg viewBox="0 0 100 120" width="72" height="86"><rect x="20" y="8" width="55" height="12" fill="#1E3A5F" rx="2"/><rect x="20" y="20" width="12" height="68" fill="#2563EB"/><rect x="20" y="88" width="55" height="12" fill="#1E3A5F" rx="2"/><text x="50" y="115" text-anchor="middle" font-size="9" fill="#6B7E9C" font-family="IBM Plex Sans">Channel</text></svg>',
       "T-section":'<svg viewBox="0 0 100 120" width="72" height="86"><rect x="15" y="8" width="70" height="12" fill="#1E3A5F" rx="2"/><rect x="44" y="20" width="12" height="56" fill="#2563EB"/><text x="50" y="115" text-anchor="middle" font-size="9" fill="#6B7E9C" font-family="IBM Plex Sans">Tee</text></svg>',
       "HSS":'<svg viewBox="0 0 100 120" width="72" height="86"><rect x="15" y="15" width="70" height="70" fill="none" stroke="#1E3A5F" stroke-width="10" rx="3"/><text x="50" y="105" text-anchor="middle" font-size="9" fill="#6B7E9C" font-family="IBM Plex Sans">HSS</text></svg>',
       "Pipe":'<svg viewBox="0 0 100 120" width="72" height="86"><circle cx="50" cy="52" r="34" fill="none" stroke="#1E3A5F" stroke-width="10"/><text x="50" y="105" text-anchor="middle" font-size="9" fill="#6B7E9C" font-family="IBM Plex Sans">Pipe</text></svg>',
       "L-section":'<svg viewBox="0 0 100 120" width="72" height="86"><rect x="18" y="8" width="12" height="84" fill="#2563EB" rx="2"/><rect x="18" y="80" width="60" height="12" fill="#1E3A5F" rx="2"/><text x="50" y="115" text-anchor="middle" font-size="9" fill="#6B7E9C" font-family="IBM Plex Sans">Angle</text></svg>',}
    return s.get(st_,s["I-section"])

@st.cache_data
def load_beam_db(file_bytes):
    df_raw=pd.read_excel(io.BytesIO(file_bytes),sheet_name="Beam Properties",header=None)
    col_map={0:"Shape",1:"W",2:"A",3:"d",4:"tw",6:"bf",7:"tf",11:"T_dist",
             15:"Ix",16:"Zx",17:"Sx",18:"rx",21:"Iy",22:"Zy",23:"Sy",24:"ry",
             27:"rts",28:"hO",29:"J",30:"Cw"}
    data=df_raw.iloc[4:].reset_index(drop=True)
    sub=data[[c for c in col_map]].copy(); sub.columns=[col_map[c] for c in col_map]
    sub=sub[sub["Shape"].notna()]; sub["Shape"]=sub["Shape"].astype(str).str.strip()
    sub=sub[~sub["Shape"].isin(["nan","0",""])]
    for col in sub.columns[1:]: sub[col]=pd.to_numeric(sub[col],errors="coerce")
    sub=sub[sub["A"].notna()].reset_index(drop=True)
    def get_prefix(s):
        for p in ["HSS","MC","HP","WT","ST","MT","W","S","M","C","L","P"]:
            if s.startswith(p): return p
        return "OTHER"
    sub["Prefix"]=sub["Shape"].apply(get_prefix)
    return sub

# ─────────────────────────────────────────────────────────────
#  SESSION DEFAULTS
# ─────────────────────────────────────────────────────────────
DEFAULTS=dict(
    project_name="",designed_by="",checked_by="Dax Clapsaddle",
    Lb_y=54.5,Lb_x=54.5,Fy=50.0,Cb=1.0,K=1.0,
    Pa=0.0,Ma=141.31,Va=7.20,Ra=7.20,N_bearing=1.0,bending_dir="strong",
    beam_designation="W21X50",loaded_shape=None,
)
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v

# fallback section props (W21X50 from PDF)
A=14.7;d=20.83;tw=0.38;bf=6.53;tf=0.535
Ix=984.0;Sx=94.5;Zx=110.0;rx=8.18
Iy=24.9;Sy=7.64;Zy=12.2;ry=1.30
rts=1.64;hO=20.29;J=1.14;Cw=2110.0

# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:10px 0 16px;">
      <div style="color:#93C5FD;font-size:.62rem;letter-spacing:.18em;font-weight:700;text-transform:uppercase;">Structured Design & Consulting</div>
      <div style="color:white;font-size:1.1rem;font-weight:700;margin-top:3px;line-height:1.25;">
        🏗️ AISC 13th ASD<br><span style="font-size:.76rem;color:#BAD4F5;font-weight:400;">Steel Beam Calculator</span>
      </div>
    </div>""",unsafe_allow_html=True)
    st.markdown("""<div style="font-size:.7rem;color:#BAD4F5;margin-bottom:12px;line-height:1.8;">
      <b style="color:#93C5FD;">Workflow:</b><br>
      ① Upload AISC Database below<br>② Select section in main panel<br>
      ③ Fill yellow input cells<br>④ Scroll down for results
    </div><hr/>""",unsafe_allow_html=True)

    st.markdown('<p style="font-size:.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#93C5FD;margin-bottom:4px;">📂 AISC Database</p>',unsafe_allow_html=True)
    db_file=st.file_uploader("Upload AISC .xlsx",type=["xlsx","xls"],key="db_uploader",label_visibility="collapsed")
    beam_db=None
    if db_file:
        beam_db=load_beam_db(db_file.read())
        st.success(f"✅ {len(beam_db)} sections loaded")
    st.markdown("<hr/>",unsafe_allow_html=True)

    st.markdown('<p style="font-size:.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#93C5FD;margin-bottom:6px;">📋 Project Info</p>',unsafe_allow_html=True)
    st.session_state.project_name=st.text_input("Project Name",value=st.session_state.project_name,placeholder="e.g. Office Block – Grid B")
    st.session_state.designed_by=st.text_input("Designed By",value=st.session_state.designed_by,placeholder="Engineer name")
    checkers=["Dax Clapsaddle","Principal Engineer","Senior Engineer","Project Manager"]
    idx=checkers.index(st.session_state.checked_by) if st.session_state.checked_by in checkers else 0
    st.session_state.checked_by=st.selectbox("Checked By",checkers,index=idx)
    st.markdown("<hr/>",unsafe_allow_html=True)

    st.markdown('<p style="font-size:.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#93C5FD;margin-bottom:6px;">💾 Session</p>',unsafe_allow_html=True)
    cs1,cs2=st.columns(2)
    with cs1:
        if st.button("💾 Save",use_container_width=True):
            sd={k:st.session_state.get(k) for k in DEFAULTS if k!="loaded_shape"}
            st.download_button("⬇ JSON",data=json.dumps(sd,indent=2).encode(),
                file_name=f"beam_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",use_container_width=True)
    with cs2:
        uj=st.file_uploader("Load JSON",type="json",key="json_loader",label_visibility="collapsed")
        if uj:
            loaded=json.load(uj)
            for k,v in loaded.items():
                if k in DEFAULTS: st.session_state[k]=v
            st.success("✅ Loaded!")
    st.markdown("<hr/>",unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:.63rem;color:#3a5a7a;text-align:center;">E={E_STEEL} ksi · Ωb={OMEGA_B} · Ωv={OMEGA_V} · Ωc={OMEGA_C}<br>AISC 13th Ed. ASD</p>',unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  TITLE
# ═══════════════════════════════════════════════════════════════
proj_line=""
if st.session_state.project_name:
    proj_line=(f'<div style="margin-top:8px;color:#dbeafe;font-size:.78rem;font-weight:600;">'
               f'📋 {st.session_state.project_name}'
               f'{" &nbsp;|&nbsp; By: "+st.session_state.designed_by if st.session_state.designed_by else ""}'
               f' &nbsp;|&nbsp; Checked: {st.session_state.checked_by}</div>')
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0F2340,#1E3A5F,#2563EB);padding:22px 30px;border-radius:14px;margin-bottom:20px;position:relative;overflow:hidden;">
  <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;border-radius:50%;background:rgba(255,255,255,.03);"></div>
  <div style="color:#93C5FD;font-size:.63rem;letter-spacing:.18em;font-weight:700;text-transform:uppercase;">Structured Design and Consulting</div>
  <div style="color:white;font-size:1.55rem;font-weight:700;margin-top:5px;line-height:1.2;">🏗️ AISC 13th Edition — Steel Beam &amp; Column Design (ASD)</div>
  <div style="color:#BAD4F5;font-size:.82rem;margin-top:4px;">Allowable Strength Design · Wide-Flange Single-Span Calculator</div>
  {proj_line}
</div>""",unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  EXAMPLE CASES
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-header">📚 Preloaded Example Cases — Click to Load</div>',unsafe_allow_html=True)
st.caption("10 validation cases covering all design zones. Load any case, run calculations, and compare with the Excel reference sheet.")

ex_cols = st.columns(5)
for i,case in enumerate(EXAMPLE_CASES):
    col = ex_cols[i % 5]
    with col:
        tag_html=f'<span class="ec-tag {case["tag"]}">{case["tag"].replace("tag-","").upper()}</span>'
        st.markdown(
            f'<div class="ex-card"><div class="ec-name">{case["name"].split("—")[0].strip()}</div>'
            f'<div class="ec-desc">{case["desc"][:60]}…</div>{tag_html}</div>',
            unsafe_allow_html=True)
        if st.button(f"Load", key=f"ex_{i}", use_container_width=True):
            for k,v in case.items():
                if k in ("name","desc","tag"): continue
                st.session_state[k]=v
            st.rerun()

# ═══════════════════════════════════════════════════════════════
#  ① SECTION SELECTOR
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-header">① Enter Beam Designation</div>',unsafe_allow_html=True)

if beam_db is not None:
    sel_col,prev_col=st.columns([1.8,1])
    with sel_col:
        available_prefixes=sorted(beam_db["Prefix"].unique())
        type_labels={p:SECTION_TYPES.get(p,(p,"I-section"))[0] for p in available_prefixes}
        cat_options=[f"{p} — {type_labels[p]}" for p in available_prefixes]
        default_cat=next((i for i,p in enumerate(available_prefixes) if p=="W"),0)
        fc1,fc2=st.columns(2)
        with fc1:
            chosen_cat_str=st.selectbox("Section Family",cat_options,index=default_cat)
        chosen_prefix=available_prefixes[cat_options.index(chosen_cat_str)]
        cat_shapes=beam_db[beam_db["Prefix"]==chosen_prefix]["Shape"].tolist()
        def size_group(s,pfx):
            m=re.match(r'^'+pfx+r'(\d+)',s)
            return (pfx+m.group(1)) if m else pfx
        groups=sorted(set(size_group(s,chosen_prefix) for s in cat_shapes),
                      key=lambda x:int(re.search(r'\d+',x).group()) if re.search(r'\d+',x) else 0)
        with fc2:
            if len(groups)>1:
                chosen_group=st.selectbox("Nominal Size",["All"]+groups)
                if chosen_group!="All":
                    cat_shapes=[s for s in cat_shapes if size_group(s,chosen_prefix)==chosen_group]
        search_txt=st.text_input("🔍 Search designation",value="",placeholder="e.g. W21, W18x50…")
        if search_txt:
            cat_shapes=[s for s in cat_shapes if search_txt.upper() in s.upper()]
        if not cat_shapes:
            st.warning("No match — filter cleared.")
            cat_shapes=beam_db[beam_db["Prefix"]==chosen_prefix]["Shape"].tolist()
        tbl_rows=[]
        for s in cat_shapes[:60]:
            r2=beam_db[beam_db["Shape"]==s]
            if not r2.empty:
                r2=r2.iloc[0]
                tbl_rows.append({"Shape":s,
                    "W(plf)":f'{r2["W"]:.0f}' if pd.notna(r2.get("W",float("nan"))) else "—",
                    "d(in)":f'{r2["d"]:.2f}'   if pd.notna(r2.get("d",float("nan"))) else "—",
                    "Ix(in⁴)":f'{r2["Ix"]:.0f}'if pd.notna(r2.get("Ix",float("nan")))else "—",
                    "Zx(in³)":f'{r2["Zx"]:.0f}'if pd.notna(r2.get("Zx",float("nan")))else "—",})
        if tbl_rows:
            st.dataframe(pd.DataFrame(tbl_rows).set_index("Shape"),use_container_width=True,height=200)
        stored=st.session_state.beam_designation
        sel_idx=cat_shapes.index(stored) if stored in cat_shapes else 0
        highlighted=st.selectbox(f"📌 Select ({len(cat_shapes)} available)",cat_shapes,index=sel_idx)
        if st.button("✅ Load This Section",use_container_width=True,type="primary"):
            st.session_state.beam_designation=highlighted
            st.session_state.loaded_shape=highlighted
            st.success(f"✅ Loaded: **{highlighted}**")
    with prev_col:
        prow=beam_db[beam_db["Shape"]==highlighted] if "highlighted" in dir() else pd.DataFrame()
        shape_type=SECTION_TYPES.get(chosen_prefix,("","I-section"))[1]
        preview_name=highlighted if "highlighted" in dir() else st.session_state.beam_designation
        st.markdown(
            f'<div style="text-align:center;padding:10px 0 6px;">{section_svg(shape_type)}'
            f'<div style="font-weight:700;color:#1E3A5F;font-size:1rem;margin-top:4px;">{preview_name}</div>'
            f'<div style="color:#6B7E9C;font-size:.72rem;">{SECTION_TYPES.get(chosen_prefix,("",""))[0]}</div></div>',
            unsafe_allow_html=True)
        if not prow.empty:
            r=prow.iloc[0]
            def pv(k):
                v=r.get(k,None)
                return f"{v:.3g}" if (v is not None and pd.notna(v) and v!=0) else "—"
            rows_html="".join([
                f'<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #e2eaf5;">'
                f'<span style="color:#6B7E9C;font-size:.74rem;font-weight:500;" title="{PROP_TIPS.get(k,"")}">{k} ℹ</span>'
                f'<span style="color:#1E3A5F;font-weight:700;font-family:IBM Plex Mono,monospace;font-size:.74rem;">{pv(k)}</span></div>'
                for k in ["A","d","tw","bf","tf","Ix","Iy","Sx","Sy","Zx","Zy"]])
            st.markdown(f'<div style="background:#f0f4ff;border:1.5px solid #c7d7ef;border-radius:10px;padding:12px;">{rows_html}</div>',unsafe_allow_html=True)

    active=st.session_state.beam_designation
    arow=beam_db[beam_db["Shape"]==active]
    if arow.empty:
        active=beam_db["Shape"].iloc[0]; st.session_state.beam_designation=active
        arow=beam_db[beam_db["Shape"]==active]
    row=arow.iloc[0]
    A=float(row["A"]);d=float(row["d"]);tw=float(row["tw"])
    bf=float(row["bf"]);tf=float(row["tf"])
    Ix=float(row["Ix"]);Sx=float(row["Sx"]);Zx=float(row["Zx"]);rx=float(row["rx"])
    Iy=float(row["Iy"]);Sy=float(row["Sy"]);Zy=float(row["Zy"]);ry=float(row["ry"])
    rts=float(row["rts"]) if pd.notna(row["rts"]) else 1.64
    hO=float(row["hO"])   if pd.notna(row["hO"])  else 20.29
    J=float(row["J"])     if pd.notna(row["J"])   else 1.14
    Cw=float(row["Cw"])   if pd.notna(row["Cw"])  else 2110.0
else:
    st.info("⬆ Upload the AISC Excel database in the sidebar to enable section browser.")
    active=st.session_state.beam_designation

# ═══════════════════════════════════════════════════════════════
#  ② SECTION PROPERTIES TABLE
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-header">② Section Properties</div>',unsafe_allow_html=True)
st.markdown(f"""
<table class="prop-table">
<tr>
  <th>A<small>in²</small></th><th>d<small>in</small></th><th>t<sub>w</sub><small>in</small></th>
  <th>b<sub>f</sub><small>in</small></th><th>t<sub>f</sub><small>in</small></th>
  <th>I<sub>x</sub><small>in⁴</small></th><th>I<sub>y</sub><small>in⁴</small></th>
  <th>S<sub>x</sub><small>in³</small></th><th>S<sub>y</sub><small>in³</small></th>
  <th>Z<sub>x</sub><small>in³</small></th><th>Z<sub>y</sub><small>in³</small></th>
  <th>r<sub>x</sub><small>in</small></th><th>r<sub>y</sub><small>in</small></th>
  <th>h<sub>O</sub><small>in</small></th>
</tr>
<tr>
  <td>{A:.2f}</td><td>{d:.2f}</td><td>{tw:.3f}</td><td>{bf:.2f}</td><td>{tf:.3f}</td>
  <td>{Ix:.1f}</td><td>{Iy:.1f}</td><td>{Sx:.2f}</td><td>{Sy:.2f}</td>
  <td>{Zx:.2f}</td><td>{Zy:.2f}</td><td>{rx:.2f}</td><td>{ry:.2f}</td><td>{hO:.2f}</td>
</tr>
</table>
<p style="font-size:.68rem;color:#6B7E9C;font-style:italic;margin:-4px 0 14px;">
  ℹ Auto-populated from AISC database. Upload DB &amp; load section above to update.
</p>""",unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  ③ DESIGN INPUTS  — perfectly aligned using st.columns with
#     explicit labels rendered ABOVE each input via st.markdown
# ═══════════════════════════════════════════════════════════════
st.markdown(
    '<div class="sec-header">③ Design Parameters &amp; Applied Loads '
    '<span style="font-size:.65rem;font-weight:400;color:#92400e;background:#fef3c7;'
    'padding:2px 8px;border-radius:4px;margin-left:8px;">⚡ Enter highlighted values</span></div>',
    unsafe_allow_html=True)

# ── Header row (dark blue, matches columns exactly) ──
HDR = [
    ("L<sub>B</sub> Y-axis","feet"),
    ("L<sub>B</sub> X-axis","feet"),
    ("F<sub>y</sub>","ksi"),
    ("C<sub>b</sub>","—"),
    ("K","—"),
    ("P<sub>A</sub>","kip"),
    ("M<sub>A</sub>","kip·ft"),
    ("V<sub>A</sub>","kip"),
    ("R<sub>A</sub>","kip"),
    ("N","in."),
    ("Bending","—"),
]
NOTE = [
    "Unbraced length of compression flange (Lb)",
    "Unbraced length of compression flange (Lb)",
    "Grade of steel. Fy>65 ksi not supported.",
    "Cb=1.0 is conservative (uniform moment).",
    "K=1.0 pinned-pinned. See AISC Table C-C2.2",
    "Max axial load (ASD level)",
    "Max bending moment (ASD level)",
    "Max shear force (ASD level)",
    "Max bearing / end reaction",
    "Min bearing length of connection",
    "strong = X-X axis bending",
]

# Build header HTML
hdr_html = '<div style="display:grid;grid-template-columns:repeat(11,1fr);border:1.5px solid #1E3A5F;border-radius:8px 8px 0 0;overflow:hidden;margin-bottom:0;">'
for (name,unit) in HDR:
    hdr_html += (
        f'<div style="background:#1E3A5F;color:white;padding:7px 4px 5px;text-align:center;'
        f'font-size:.64rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;'
        f'border-right:1px solid #16304f;line-height:1.25;">'
        f'{name}<br><span style="font-size:.58rem;color:#93C5FD;font-weight:400;text-transform:none;">{unit}</span></div>'
    )
hdr_html += '</div>'
st.markdown(hdr_html, unsafe_allow_html=True)

# ── Input row (yellow cells, perfectly aligned via st.columns) ──
inp_style = """
<style>
/* Target all number inputs and selects in the input row only */
div[data-testid="stHorizontalBlock"] div[data-testid="stNumberInputContainer"] input,
div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"] select {
    border-radius: 0 !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
    border-bottom: 2px solid #F9A825 !important;
    background: #FFFDE7 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    color: #1E3A5F !important;
    text-align: center !important;
    box-shadow: none !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stNumberInputContainer"],
div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"] > div {
    background: #FFFDE7 !important;
    border: 1px solid #e8d98a !important;
    border-top: none !important;
    border-radius: 0 !important;
}
div[data-testid="stHorizontalBlock"] label { display: none !important; }
div[data-testid="stHorizontalBlock"] button[data-testid="stNumberInputStepDown"],
div[data-testid="stHorizontalBlock"] button[data-testid="stNumberInputStepUp"] {
    background: #FFFDE7 !important; border: none !important;
}
</style>
"""
st.markdown(inp_style, unsafe_allow_html=True)

ic = st.columns(11)
with ic[0]:
    Lb_y=st.number_input("LB Y",value=float(st.session_state.Lb_y),step=0.5,
        help="Unbraced length — weak axis (column buckling). AISC E3.",format="%.2f")
with ic[1]:
    Lb_x=st.number_input("LB X",value=float(st.session_state.Lb_x),step=0.5,
        help="Unbraced length of compression flange for LTB. AISC F2.",format="%.2f")
with ic[2]:
    fy_opts={"36":36.0,"50":50.0,"Cust":None}
    fy_pick=st.selectbox("Fy",list(fy_opts.keys()),
        index=1 if st.session_state.Fy==50 else (0 if st.session_state.Fy==36 else 2))
    Fy=fy_opts[fy_pick] if fy_opts[fy_pick] is not None else st.session_state.Fy
    if fy_pick=="Cust":
        Fy=ic[2].number_input("Fy val",value=float(st.session_state.Fy),step=1.0,label_visibility="collapsed")
with ic[3]:
    Cb=st.number_input("Cb",value=float(st.session_state.Cb),step=0.05,min_value=1.0,
        help="LTB modification factor. Cb=1.0 conservative.",format="%.2f")
with ic[4]:
    k_map={"0.5":0.5,"0.7":0.7,"1.0":1.0,"1.2":1.2,"2.0":2.0}
    k_default=min(k_map.keys(), key=lambda x: abs(k_map[x]-st.session_state.K))
    k_str=st.selectbox("K",list(k_map.keys()),index=list(k_map.keys()).index(k_default),
        help="Effective length factor. AISC E3.")
    K=k_map[k_str]
with ic[5]:
    Pa=st.number_input("PA",value=float(st.session_state.Pa),step=1.0,
        help="Applied axial compressive load (ASD). AISC Ch.H.",format="%.2f")
with ic[6]:
    Ma=st.number_input("MA",value=float(st.session_state.Ma),step=1.0,
        help="Applied strong-axis bending moment (ASD). AISC F2.",format="%.2f")
with ic[7]:
    Va=st.number_input("VA",value=float(st.session_state.Va),step=0.5,
        help="Applied vertical shear force (ASD). AISC G2.",format="%.2f")
with ic[8]:
    Ra=st.number_input("RA",value=float(st.session_state.Ra),step=0.5,
        help="Applied bearing / end reaction. AISC J10.",format="%.2f")
with ic[9]:
    N_bearing=st.number_input("N",value=float(st.session_state.N_bearing),step=0.25,min_value=0.1,
        help="Bearing length of connection plate. AISC J10.",format="%.2f")
with ic[10]:
    bd_idx=0 if st.session_state.bending_dir=="strong" else 1
    bending_dir=st.selectbox("Bending",["strong","weak"],index=bd_idx,
        help="strong = X-X axis; weak = Y-Y axis.")

# Save to session
for k in ("Lb_y","Lb_x","Fy","Cb","K","Pa","Ma","Va","Ra","N_bearing","bending_dir"):
    st.session_state[k]=locals()[k]

# ── Note row below inputs (aligned to same 11 columns) ──
note_html = '<div style="display:grid;grid-template-columns:repeat(11,1fr);border:1px solid #e2eaf5;border-top:none;border-radius:0 0 8px 8px;overflow:hidden;margin-bottom:16px;">'
for note in NOTE:
    note_html += (
        f'<div style="background:#f8f9fa;color:#6B7E9C;font-size:.59rem;text-align:center;'
        f'padding:5px 3px;border-right:1px solid #e2eaf5;line-height:1.35;">{note}</div>'
    )
note_html += '</div>'
st.markdown(note_html, unsafe_allow_html=True)

# Warnings
if Fy>65: st.warning("⚠️ Fy > 65 ksi — outside AISC W-shape range. Results may be unreliable.")
if Cb<1.0: st.warning("⚠️ Cb < 1.0 is unconservative. AISC requires Cb ≥ 1.0.")

# ═══════════════════════════════════════════════════════════════
#  CALCULATIONS
# ═══════════════════════════════════════════════════════════════
E=E_STEEL; Lb_in_y=Lb_y*12.0; Lb_in_x=Lb_x*12.0
Zb,Sb=(Zx,Sx) if bending_dir=="strong" else (Zy,Sy)

# Compactness
lam_f=bf/(2*tf); lam_w=(d-2*tf)/tw
lam_pf=0.38*np.sqrt(E/Fy); lam_pw=3.76*np.sqrt(E/Fy)
flange_compact=bool(lam_f<=lam_pf); web_compact=bool(lam_w<=lam_pw)

# Flexure
Mp=Fy*Zb; Mn_allow_yield=Mp/OMEGA_B/12.0
Lp=1.76*ry*np.sqrt(E/Fy)
Lr=1.95*rts*(E/(0.7*Fy))*np.sqrt(J/(Sx*hO)+np.sqrt((J/(Sx*hO))**2+6.76*((0.7*Fy)/E)**2))
Lp_ft=Lp/12.0; Lr_ft=Lr/12.0
if Lb_in_x<=Lp:
    ltb_zone="Lb ≤ Lp  (Plastic — No LTB)"; Mn_ltb=Mp
elif Lb_in_x<=Lr:
    ltb_zone="Lp < Lb ≤ Lr  (Inelastic LTB)"
    Mn_ltb=min(Cb*(Mp-(Mp-0.7*Fy*Sx)*((Lb_in_x-Lp)/(Lr-Lp))),Mp)
else:
    ltb_zone="Lb > Lr  (Elastic LTB)"
    Fcr_ltb=(Cb*np.pi**2*E)/((Lb_in_x/rts)**2)*np.sqrt(1+0.078*J/(Sx*hO)*(Lb_in_x/rts)**2)
    Mn_ltb=min(Fcr_ltb*Sx,Mp)
Mn_allow_ltb=Mn_ltb/OMEGA_B/12.0; Mn_allow=min(Mn_allow_yield,Mn_allow_ltb)

# Shear
h_tw=(d-2*tf)/tw; limit_shear=2.24*np.sqrt(E/Fy)
Cv=1.0 if h_tw<=limit_shear else max(1.51*5.34*E/(h_tw**2*Fy),0.0)
Vn=0.6*Fy*(d*tw)*Cv; Vn_allow=Vn/OMEGA_V

# Axial
KL_r=K*Lb_in_y/ry; Fe=np.pi**2*E/(KL_r**2); lim_c=4.71*np.sqrt(E/Fy)
Fcr_c=(0.658**(Fy/Fe))*Fy if KL_r<=lim_c else 0.877*Fe
Pn_allow=Fcr_c*A/OMEGA_C

# Combined
Mcy_allow=(Zy*Fy/OMEGA_B/12.0) if (Zy>0 and pd.notna(Zy)) else 1e6
Mry=0.0
ratio_p=(Pa/Pn_allow) if Pn_allow>0 else 0.0
if Pa>0 and ratio_p>=0.2:
    combined=ratio_p+(8.0/9.0)*(Ma/Mn_allow+(Mry/Mcy_allow if Mcy_allow>0 else 0))
elif Pa>0:
    combined=ratio_p/2.0+(Ma/Mn_allow+(Mry/Mcy_allow if Mcy_allow>0 else 0))
else:
    combined=Ma/Mn_allow if Mn_allow>0 else 0.0

# Bearing — AISC J10
k_des=tf+0.25
Rn_lwy=0.66*Fy*tw*(N_bearing+2.5*k_des); Ra_lwy_allow=Rn_lwy/OMEGA_V
Nd_ratio=N_bearing/d
Rn_wc_end=0.40*tw**2*(1+3*(N_bearing/d)*(tw/tf)**1.5)*np.sqrt(E*Fy*tf/tw)
Ra_wc_allow=Rn_wc_end/OMEGA_V

# Utilizations
flex_util =(Ma/Mn_allow*100)      if Mn_allow>0      else 0.0
shear_util=(Va/Vn_allow*100)      if Vn_allow>0      else 0.0
axial_util=(Pa/Pn_allow*100)      if Pn_allow>0      else 0.0
lwy_util  =(Ra/Ra_lwy_allow*100)  if Ra_lwy_allow>0  else 0.0
wc_util   =(Ra/Ra_wc_allow*100)   if Ra_wc_allow>0   else 0.0

kl_r_warn=KL_r>200
overall_pass=(flex_util<=100 and shear_util<=100 and axial_util<=100
              and combined<=1.0 and lwy_util<=100 and wc_util<=100)

# ═══════════════════════════════════════════════════════════════
#  ④ OVERALL STATUS
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-header">④ Design Status</div>',unsafe_allow_html=True)
if overall_pass:
    st.markdown('<div class="banner-pass">✅ OVERALL: PASS — All limit states satisfied</div>',unsafe_allow_html=True)
else:
    st.markdown('<div class="banner-fail">❌ OVERALL: FAIL — One or more limit states exceeded. Revise section or loads.</div>',unsafe_allow_html=True)
if kl_r_warn: st.warning(f"⚠️ KL/r = {KL_r:.1f} > 200 — AISC recommends ≤ 200 (AISC E2).")
if 90<flex_util<=100: st.warning(f"⚠️ Flexural utilization {flex_util:.1f}% — very close to limit.")
if 90<shear_util<=100: st.warning(f"⚠️ Shear utilization {shear_util:.1f}% — very close to limit.")

# ═══════════════════════════════════════════════════════════════
#  ⑤ DASHBOARD
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-header">⑤ Capacity Summary Dashboard</div>',unsafe_allow_html=True)

def metric_card(label,value_str,badge_txt,pct_raw,sub="",extra=""):
    pct_disp=min(pct_raw,100)
    if pct_raw>100:   cc,bc="mc-fail","badge-fail"
    elif pct_raw>90:  cc,bc="mc-warn","badge-warn"
    else:             cc,bc="mc-pass","badge-pass"
    gc=gauge_cls(pct_raw)
    return (f'<div class="metric-card {cc}">'
            f'<div class="mc-label">{label}</div>'
            f'<div class="mc-value">{value_str}</div>'
            f'<div class="gauge-track"><div class="{gc}" style="width:{pct_disp}%"></div></div>'
            f'{"<div class=mc-sub>"+sub+"</div>" if sub else ""}'
            f'<span class="mc-badge {bc}">{badge_txt}</span>{extra}</div>')

ltb_badge=(f'<div style="margin-top:5px;"><span style="background:#dbeafe;color:#1e3a8a;'
           f'padding:2px 7px;border-radius:4px;font-size:.6rem;font-family:IBM Plex Mono,monospace;">'
           f'{ltb_zone}</span></div>')
c1,c2,c3,c4=st.columns(4)
with c1: st.markdown(metric_card("Flexural Utilization",f"{flex_util:.1f}%","PASS" if flex_util<=100 else "FAIL",flex_util,f"Ma={Ma:.1f} / Mn/Ω={Mn_allow:.2f} k·ft",ltb_badge),unsafe_allow_html=True)
with c2: st.markdown(metric_card("Shear Utilization",f"{shear_util:.1f}%","PASS" if shear_util<=100 else "FAIL",shear_util,f"Va={Va:.1f} / Vn/Ω={Vn_allow:.2f} kip"),unsafe_allow_html=True)
with c3: st.markdown(metric_card("Axial Utilization",f"{axial_util:.1f}%","PASS" if axial_util<=100 else "FAIL",axial_util,f"Pa={Pa:.1f} / Pn/Ω={Pn_allow:.2f} kip"),unsafe_allow_html=True)
with c4: st.markdown(metric_card("Combined H1-1",f"{combined:.3f}","PASS (≤1.0)" if combined<=1.0 else "FAIL (>1.0)",combined*100,"AISC Sect. H1-1"),unsafe_allow_html=True)
st.markdown("<br>",unsafe_allow_html=True)
c5,c6,c7,_=st.columns(4)
with c5: st.markdown(metric_card("Local Web Yielding",f"{lwy_util:.1f}%","PASS" if lwy_util<=100 else "FAIL",lwy_util,f"Ra={Ra:.1f} / Rn/Ω={Ra_lwy_allow:.2f} kip"),unsafe_allow_html=True)
with c6: st.markdown(metric_card("Web Crippling (End)",f"{wc_util:.1f}%","PASS" if wc_util<=100 else "FAIL",wc_util,f"Ra={Ra:.1f} / Rn/Ω={Ra_wc_allow:.2f} kip"),unsafe_allow_html=True)
with c7:
    comp_col="#059669" if (flange_compact and web_compact) else "#d97706"
    st.markdown(f'<div class="metric-card" style="border-color:#c7d7ef;"><div class="mc-label">Section Compactness</div>'
        f'<div class="mc-value" style="font-size:1.05rem;margin-top:6px;color:{comp_col};">{"COMPACT ✅" if (flange_compact and web_compact) else "NON-COMPACT ⚠️"}</div>'
        f'<div class="mc-sub">λf={lam_f:.3f} vs λpf={lam_pf:.3f}</div>'
        f'<div class="mc-sub">λw={lam_w:.2f} vs λpw={lam_pw:.3f}</div></div>',unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)
st.markdown('<div class="sec-header">📋 Detailed Capacity Table</div>',unsafe_allow_html=True)
summary_df=pd.DataFrame({
    "Check":    ["Flexure (X-X)","Shear (Web)","Axial Compression","Combined H1-1","Local Web Yielding","Web Crippling (End)"],
    "Demand":   [f"{Ma:.2f} k·ft",f"{Va:.2f} kip",f"{Pa:.2f} kip",f"{combined:.4f}",f"{Ra:.2f} kip",f"{Ra:.2f} kip"],
    "Capacity": [f"{Mn_allow:.3f} k·ft",f"{Vn_allow:.3f} kip",f"{Pn_allow:.3f} kip","1.000",f"{Ra_lwy_allow:.3f} kip",f"{Ra_wc_allow:.3f} kip"],
    "Util %":   [f"{flex_util:.1f}%",f"{shear_util:.1f}%",f"{axial_util:.1f}%",f"{combined*100:.1f}%",f"{lwy_util:.1f}%",f"{wc_util:.1f}%"],
    "Status":   ["✅ PASS" if flex_util<=100 else "❌ FAIL","✅ PASS" if shear_util<=100 else "❌ FAIL",
                 "✅ PASS" if axial_util<=100 else "❌ FAIL","✅ PASS" if combined<=1.0 else "❌ FAIL",
                 "✅ PASS" if lwy_util<=100 else "❌ FAIL","✅ PASS" if wc_util<=100 else "❌ FAIL"],
    "Reference":["AISC F2","AISC G2.1","AISC E3","AISC H1-1","AISC J10.2","AISC J10.3"],
})
st.dataframe(summary_df,use_container_width=True,hide_index=True)

# ═══════════════════════════════════════════════════════════════
#  ⑥ CHART
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-header">⑥ Capacity vs. Demand Chart</div>',unsafe_allow_html=True)
categories=["Flexure (k·ft)","Shear (kip)","Axial (kip)","LWY Bearing (kip)","Web Crip. (kip)"]
demands=[Ma,Va,Pa,Ra,Ra]; capacities=[Mn_allow,Vn_allow,Pn_allow,Ra_lwy_allow,Ra_wc_allow]
utils=[flex_util,shear_util,axial_util,lwy_util,wc_util]
bar_cols=["#10B981" if u<=70 else "#F59E0B" if u<=90 else "#F97316" if u<=100 else "#EF4444" for u in utils]
fig=go.Figure()
fig.add_trace(go.Bar(name="Allowable Capacity",y=categories,x=capacities,orientation="h",
    marker_color="#1D4ED8",marker_opacity=0.5,
    text=[f"{v:.2f}" for v in capacities],textposition="inside",
    insidetextfont=dict(color="white",size=11),
    hovertemplate="<b>%{y}</b><br>Capacity: %{x:.3f}<extra></extra>"))
fig.add_trace(go.Bar(name="Applied Demand",y=categories,x=demands,orientation="h",
    marker_color=bar_cols,marker_opacity=0.92,
    text=[f"{v:.2f}" for v in demands],textposition="inside",
    insidetextfont=dict(color="white",size=11),
    hovertemplate="<b>%{y}</b><br>Demand: %{x:.3f}<extra></extra>"))
for i,(cap,util) in enumerate(zip(capacities,utils)):
    fig.add_annotation(x=cap*1.01,y=i,text=f"<b>{util:.1f}%</b>",showarrow=False,
        font=dict(size=11,color="#1E3A5F"),xanchor="left")
fig.update_layout(barmode="overlay",height=310,margin=dict(l=0,r=90,t=40,b=10),
    legend=dict(orientation="h",y=1.1,x=0,font=dict(size=11)),
    title=dict(text="<b>Capacity vs. Demand</b>",font=dict(size=13,color="#1E3A5F"),x=0),
    xaxis_title="Magnitude",font=dict(family="IBM Plex Sans",size=12),
    plot_bgcolor="#f8faff",paper_bgcolor="rgba(0,0,0,0)",xaxis=dict(gridcolor="#e2eaf5"))
st.plotly_chart(fig,use_container_width=True)

# LTB zone
st.markdown('<div class="sec-header" style="margin-top:4px;">📉 LTB Zone</div>',unsafe_allow_html=True)
lz1,lz2,lz3=st.columns(3)
zone_defs=[("Plastic (Lb ≤ Lp)","Plastic","#10B981"),("Inelastic LTB","Inelastic","#F59E0B"),("Elastic LTB","Elastic","#EF4444")]
for col,(label,key,c) in zip([lz1,lz2,lz3],zone_defs):
    az=key in ltb_zone
    col.markdown(f'<div style="background:{"linear-gradient(135deg,"+c+"22,"+c+"11)" if az else "#f8faff"};'
        f'border:{"3px solid "+c if az else "1.5px solid #e2eaf5"};border-radius:10px;padding:12px;text-align:center;">'
        f'<div style="font-size:.65rem;font-weight:700;color:{c};text-transform:uppercase;">{"● ACTIVE" if az else "○"}</div>'
        f'<div style="font-weight:700;color:#1E3A5F;margin-top:3px;font-size:.83rem;">{label}</div></div>',unsafe_allow_html=True)
st.markdown(f'<div style="background:#f0f4ff;border:1.5px solid #c7d7ef;border-radius:9px;padding:10px 16px;margin-top:6px;font-size:.81rem;">'
    f'<b style="color:#6B7E9C;">Lp =</b> <span style="font-family:IBM Plex Mono,monospace;color:#1E3A5F;">{Lp_ft:.3f} ft</span>'
    f' &nbsp;|&nbsp; <b style="color:#6B7E9C;">Lr =</b> <span style="font-family:IBM Plex Mono,monospace;color:#1E3A5F;">{Lr_ft:.3f} ft</span>'
    f' &nbsp;|&nbsp; <b style="color:#6B7E9C;">Lb =</b> <span style="font-family:IBM Plex Mono,monospace;color:#1E3A5F;">{Lb_x:.2f} ft</span>'
    f'</div>',unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  ⑦ HAND CALCULATIONS
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-header">⑦ Detailed Hand Calculations &amp; Verification</div>',unsafe_allow_html=True)
if not overall_pass: st.error("❌ One or more checks FAILED — review the steps below.")
st.markdown(f'<b style="color:#1E3A5F;font-size:1rem;">Section: {active}</b> &nbsp;'+rbadge("AISC 13th, Table 1-1"),unsafe_allow_html=True)
st.markdown(f"A={gchip(f'{A}','in²')} d={gchip(f'{d}','in')} tw={gchip(f'{tw}','in')} bf={gchip(f'{bf}','in')} tf={gchip(f'{tf}','in')} Zx={gchip(f'{Zx}','in³')} Sx={gchip(f'{Sx}','in³')} ry={gchip(f'{ry}','in')} rts={gchip(f'{rts:.4f}','in')} J={gchip(f'{J}','in⁴')} hO={gchip(f'{hO}','in')}",unsafe_allow_html=True)
st.markdown("---")

with st.expander("① Compactness Check — AISC Table B4.1b",expanded=True):
    st.markdown('<div class="calc-step"><span class="step-num">1</span>Compactness Check</div>',unsafe_allow_html=True)
    st.markdown("**Flange slenderness:**"); st.latex(r"\lambda_f = b_f / (2\,t_f)")
    st.markdown(f"= {gchip(f'{bf}','in')} / (2×{gchip(f'{tf}','in')}) = {bchip(f'{lam_f:.3f}')} vs λpf={bchip(f'{lam_pf:.3f}')} → {pass_html('Flange COMPACT') if flange_compact else fail_html('Flange NON-COMPACT')}",unsafe_allow_html=True)
    st.markdown("**Web slenderness:**"); st.latex(r"\lambda_w = (d - 2\,t_f) / t_w")
    st.markdown(f"= {bchip(f'{lam_w:.2f}')} vs λpw={bchip(f'{lam_pw:.3f}')} → {pass_html('Web COMPACT') if web_compact else fail_html('Web NON-COMPACT')}",unsafe_allow_html=True)

with st.expander("② Flexural Design — AISC Ch.16, Sect F2",expanded=not overall_pass):
    st.markdown('<div class="calc-step"><span class="step-num">2</span>Flexural Design</div>',unsafe_allow_html=True)
    st.markdown("#### 2a) Yielding"); st.latex(r"M_p = F_y \cdot Z_x \quad M_n/\Omega_b = M_p/(\Omega_b \times 12)")
    st.markdown(f"Mp = {gchip(f'{Fy}','ksi')} × {gchip(f'{Zb}','in³')} = {bchip(f'{Mp:.0f}','k·in')} = {bchip(f'{Mp/12:.2f}','k·ft')} → Mn/Ωb(yield) = {bchip(f'{Mn_allow_yield:.3f}','k·ft')}",unsafe_allow_html=True)
    st.markdown("#### 2b) Lateral-Torsional Buckling")
    st.latex(r"L_p=1.76\,r_y\sqrt{E/F_y} \qquad L_r=1.95\,r_{ts}\frac{E}{0.7F_y}\sqrt{\frac{Jc}{S_x h_o}+\sqrt{(\frac{Jc}{S_x h_o})^2+6.76(\frac{0.7F_y}{E})^2}}")
    st.markdown(f"Lp={bchip(f'{Lp_ft:.3f}','ft')} &nbsp; Lr={bchip(f'{Lr_ft:.3f}','ft')} &nbsp; Lb={gchip(f'{Lb_x:.2f}','ft')} → Zone: {bchip(ltb_zone)}",unsafe_allow_html=True)
    if "Plastic" in ltb_zone: st.latex(r"M_n = M_p \text{ (No LTB)}")
    elif "Inelastic" in ltb_zone: st.latex(r"M_n=C_b[M_p-(M_p-0.7F_yS_x)\frac{L_b-L_p}{L_r-L_p}]\leq M_p")
    else:
        st.latex(r"F_{cr}=\frac{C_b\pi^2E}{(L_b/r_{ts})^2}\sqrt{1+0.078\frac{J}{S_xh_o}(\frac{L_b}{r_{ts}})^2}")
        st.latex(r"M_n=F_{cr}S_x\leq M_p")
    st.markdown(f"Mn(LTB)={bchip(f'{Mn_ltb/12:.3f}','k·ft')} → Mn/Ωb(LTB)={bchip(f'{Mn_allow_ltb:.3f}','k·ft')}",unsafe_allow_html=True)
    st.markdown(f"**Governing Mn/Ωb = min(Yield,LTB) = {bchip(f'{Mn_allow:.3f}','k·ft')}**",unsafe_allow_html=True)
    fc="#059669" if flex_util<=100 else "#dc2626"
    st.markdown(f'<div style="padding:8px 14px;background:#f0f4ff;border-radius:8px;font-weight:700;color:{fc};margin-top:8px;">Utilization = {Ma:.2f}/{Mn_allow:.3f} = {flex_util:.1f}% {"✅ PASS" if flex_util<=100 else "❌ FAIL"}</div>',unsafe_allow_html=True)

with st.expander("③ Shear Design — AISC Sect G2.1",expanded=not overall_pass):
    st.markdown('<div class="calc-step"><span class="step-num">3</span>Shear Design</div>',unsafe_allow_html=True)
    st.latex(r"V_n=0.6F_y(d\cdot t_w)C_v \quad V_n/\Omega_v")
    st.markdown(f"h/tw={bchip(f'{h_tw:.3f}')} &nbsp; 2.24√(E/Fy)={bchip(f'{limit_shear:.3f}')} &nbsp; Cv={bchip(f'{Cv:.3f}')}",unsafe_allow_html=True)
    st.markdown(f"Vn={bchip(f'{Vn:.3f}','kip')} → Vn/Ωv={bchip(f'{Vn_allow:.3f}','kip')}",unsafe_allow_html=True)
    sc="#059669" if shear_util<=100 else "#dc2626"
    st.markdown(f'<div style="padding:8px 14px;background:#f0f4ff;border-radius:8px;font-weight:700;color:{sc};margin-top:8px;">Utilization = {Va:.2f}/{Vn_allow:.3f} = {shear_util:.1f}% {"✅ PASS" if shear_util<=100 else "❌ FAIL"}</div>',unsafe_allow_html=True)

with st.expander("④ Axial Compression — AISC Ch.E, Sect E3",expanded=not overall_pass):
    st.markdown('<div class="calc-step"><span class="step-num">4</span>Axial Compression</div>',unsafe_allow_html=True)
    st.latex(r"KL/r = K\cdot L_{by}\cdot 12/r_y \qquad F_e=\pi^2E/(KL/r)^2")
    st.markdown(f"KL/r={bchip(f'{KL_r:.2f}')}{'  ⚠️ >200' if kl_r_warn else ''} &nbsp; Fe={bchip(f'{Fe:.2f}','ksi')} &nbsp; 4.71√(E/Fy)={bchip(f'{lim_c:.2f}')}",unsafe_allow_html=True)
    if KL_r<=lim_c: st.latex(r"F_{cr}=0.658^{F_y/F_e}F_y \quad (KL/r\leq4.71\sqrt{E/F_y})")
    else: st.latex(r"F_{cr}=0.877F_e \quad (KL/r>4.71\sqrt{E/F_y})")
    st.markdown(f"Fcr={bchip(f'{Fcr_c:.3f}','ksi')} → Pn=Fcr×A={bchip(f'{Fcr_c*A:.2f}','kip')} → Pn/Ωc={bchip(f'{Pn_allow:.2f}','kip')}",unsafe_allow_html=True)
    ac="#059669" if axial_util<=100 else "#dc2626"
    st.markdown(f'<div style="padding:8px 14px;background:#f0f4ff;border-radius:8px;font-weight:700;color:{ac};margin-top:8px;">Utilization = {Pa:.2f}/{Pn_allow:.2f} = {axial_util:.1f}% {"✅ PASS" if axial_util<=100 else "❌ FAIL"}</div>',unsafe_allow_html=True)

with st.expander("⑤ Combined Forces — AISC Sect H1-1",expanded=not overall_pass):
    st.markdown('<div class="calc-step"><span class="step-num">5</span>Combined Forces</div>',unsafe_allow_html=True)
    if ratio_p>=0.2: st.latex(r"\frac{P_a}{P_c}+\frac{8}{9}(\frac{M_{rx}}{M_{cx}}+\frac{M_{ry}}{M_{cy}})\leq1.0\quad\text{(H1-1a, Pa/Pc}\geq0.2)")
    else: st.latex(r"\frac{P_a}{2P_c}+(\frac{M_{rx}}{M_{cx}}+\frac{M_{ry}}{M_{cy}})\leq1.0\quad\text{(H1-1b, Pa/Pc}<0.2)")
    cc2="#059669" if combined<=1.0 else "#dc2626"
    st.markdown(f'<div style="padding:10px 16px;background:#f0f4ff;border-radius:8px;font-size:1.05rem;font-weight:700;color:{cc2};margin-top:8px;">Combined Ratio = {bchip(f"{combined:.4f}")} → {"✅ PASS (≤1.0)" if combined<=1.0 else "❌ FAIL (>1.0)"}</div>',unsafe_allow_html=True)

with st.expander("⑥ Web Crippling & Local Web Yielding — AISC J10",expanded=not overall_pass):
    st.markdown('<div class="calc-step"><span class="step-num">6</span>Web Crippling &amp; Local Web Yielding</div>',unsafe_allow_html=True)
    st.markdown(f"**Inputs:** Ra={gchip(f'{Ra}','kip')} &nbsp; N={gchip(f'{N_bearing}','in')} &nbsp; k_des≈{gchip(f'{k_des:.3f}','in')}",unsafe_allow_html=True)
    st.markdown("#### Local Web Yielding — End Reaction (AISC J10.2, Eq J10-3)")
    st.latex(r"R_n=0.66F_y t_w(N+2.5\,k_{des})")
    st.markdown(f"= 0.66×{gchip(f'{Fy}','ksi')}×{gchip(f'{tw}','in')}×({gchip(f'{N_bearing}','in')}+2.5×{gchip(f'{k_des:.3f}','in')}) = {bchip(f'{Rn_lwy:.3f}','kip')} → Rn/Ω={bchip(f'{Ra_lwy_allow:.3f}','kip')}",unsafe_allow_html=True)
    lwc="#059669" if lwy_util<=100 else "#dc2626"
    st.markdown(f'<div style="padding:8px 14px;background:#f0f4ff;border-radius:8px;font-weight:700;color:{lwc};margin-top:6px;">LWY Util = {Ra:.2f}/{Ra_lwy_allow:.3f} = {lwy_util:.1f}% {"✅ PASS" if lwy_util<=100 else "❌ FAIL"}</div>',unsafe_allow_html=True)
    st.markdown("#### Web Crippling — End Reaction (AISC J10.3, Eq J10-4)")
    st.latex(r"R_n=0.40\,t_w^2[1+3\frac{N}{d}(\frac{t_w}{t_f})^{1.5}]\sqrt{\frac{EF_yt_f}{t_w}}")
    st.markdown(f"N/d={gchip(f'{Nd_ratio:.4f}')} &nbsp; Rn={bchip(f'{Rn_wc_end:.3f}','kip')} → Rn/Ω={bchip(f'{Ra_wc_allow:.3f}','kip')}",unsafe_allow_html=True)
    wcc="#059669" if wc_util<=100 else "#dc2626"
    st.markdown(f'<div style="padding:8px 14px;background:#f0f4ff;border-radius:8px;font-weight:700;color:{wcc};margin-top:6px;">WC Util = {Ra:.2f}/{Ra_wc_allow:.3f} = {wc_util:.1f}% {"✅ PASS" if wc_util<=100 else "❌ FAIL"}</div>',unsafe_allow_html=True)
    st.info("ℹ️ k_des ≈ tf + 0.25 in (conservative). For precise k_des refer to AISC Table 1-1.")

st.markdown("---")
st.caption(f"E={E_STEEL} ksi · Ωb={OMEGA_B} · Ωv={OMEGA_V} · Ωc={OMEGA_C} · AISC Steel Construction Manual, 13th Edition (ASD)")

# ═══════════════════════════════════════════════════════════════
#  ⑧ EXPORT
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-header">⑧ Export &amp; Reports</div>',unsafe_allow_html=True)
ex1,ex2,ex3=st.columns(3)
with ex1:
    st.markdown("**💾 Session (JSON)**"); st.caption("Save all inputs to reload later.")
    sd={k:st.session_state.get(k) for k in DEFAULTS if k!="loaded_shape"}
    st.download_button("⬇ Download JSON",data=json.dumps(sd,indent=2).encode(),
        file_name=f"beam_{st.session_state.beam_designation}_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",use_container_width=True)
with ex2:
    st.markdown("**📋 Calculation Sheet (CSV)**"); st.caption("All inputs + results in one flat file.")
    export_df=pd.DataFrame({"Parameter":["Project","Designer","Checker","Section","Fy (ksi)","E (ksi)",
        "Lb_x (ft)","Lb_y (ft)","Cb","K","Pa (kip)","Ma (k-ft)","Va (kip)","Ra (kip)","N (in)",
        "Mn_allow (k-ft)","Vn_allow (kip)","Pn_allow (kip)","LWY_allow (kip)","WC_allow (kip)",
        "Flex Util (%)","Shear Util (%)","Axial Util (%)","LWY Util (%)","WC Util (%)","Combined H1-1","Overall"],
        "Value":[st.session_state.project_name,st.session_state.designed_by,st.session_state.checked_by,
        st.session_state.beam_designation,Fy,E_STEEL,Lb_x,Lb_y,Cb,K,Pa,Ma,Va,Ra,N_bearing,
        f"{Mn_allow:.3f}",f"{Vn_allow:.3f}",f"{Pn_allow:.3f}",f"{Ra_lwy_allow:.3f}",f"{Ra_wc_allow:.3f}",
        f"{flex_util:.2f}",f"{shear_util:.2f}",f"{axial_util:.2f}",f"{lwy_util:.2f}",f"{wc_util:.2f}",
        f"{combined:.4f}","PASS" if overall_pass else "FAIL"]})
    st.download_button("⬇ Download CSV",data=export_df.to_csv(index=False).encode(),
        file_name=f"calc_{st.session_state.beam_designation}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",use_container_width=True)
with ex3:
    st.markdown("**🖨️ Print to PDF**"); st.caption("Ctrl+P / ⌘+P → Save as PDF. Sidebar hidden automatically.")
    st.markdown('<div style="background:#fef3c7;border:1.5px solid #fcd34d;border-radius:8px;padding:10px 14px;font-size:.75rem;color:#78350f;">Expand all hand-calculation sections before printing for a complete calc sheet.</div>',unsafe_allow_html=True)
