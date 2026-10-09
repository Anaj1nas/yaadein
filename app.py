import hashlib
import hmac
import secrets
import sqlite3
import textwrap
import time
import uuid
import random
from pathlib import Path

import streamlit as st


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Yaadein - Family Memories",
    page_icon="\U0001F499",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "yaadein.db"
PHOTO_DIR = BASE_DIR / "family_photos"

PHOTO_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>
/* =========================================================
   YAadein VISUAL THEME — Lavender Garden
   Warm, calm, accessible, and intentionally low-contrast
   enough for older users while still feeling premium.
   ========================================================= */

:root {
    --plum-950: #1d1224;
    --plum-900: #28152f;
    --plum-800: #392043;
    --plum-700: #4c2a55;
    --lavender: #d9c4ee;
    --lavender-soft: #eee4f8;
    --rose: #e7a6b8;
    --peach: #f2c2ad;
    --sage: #bfd8c3;
    --cream: #fff8ef;
    --text: #fff9f5;
    --muted: #e1d5e6;
}

.stApp {
    background:
        radial-gradient(circle at 8% 8%, rgba(242,194,173,.18), transparent 24%),
        radial-gradient(circle at 92% 14%, rgba(217,196,238,.18), transparent 26%),
        radial-gradient(circle at 70% 88%, rgba(191,216,195,.11), transparent 24%),
        linear-gradient(135deg, #1d1224 0%, #35203e 46%, #24162f 100%);
    color: var(--text);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 20% 10%, rgba(242,194,173,.10), transparent 28%),
        linear-gradient(180deg, #1b1022 0%, #2e1938 55%, #3b2243 100%);
    border-right: 1px solid rgba(231,166,184,.22);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--cream) !important;
}

h1, h2, h3 {
    color: var(--cream) !important;
}

p, li, label, .stMarkdown {
    color: #f6edf5;
}

/* Main buttons: soft garden gradient rather than cold blue */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #7b4b82 0%, #a86483 52%, #c98d83 100%);
    color: #fffaf7;
    border: 1px solid rgba(242,194,173,.52);
    border-radius: 14px;
    padding: .68rem 1rem;
    font-weight: 800;
    box-shadow: 0 8px 20px rgba(29,18,36,.28);
    transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    filter: brightness(1.08);
    transform: translateY(-2px);
    box-shadow: 0 12px 26px rgba(29,18,36,.38);
    border-color: rgba(255,248,239,.75);
}

.stButton > button:focus-visible,
.stFormSubmitButton > button:focus-visible {
    outline: 3px solid rgba(242,194,173,.65);
    outline-offset: 2px;
}

/* Photo Quiz: big, clear name buttons for older users */
.yaadein-quiz-option button {
    min-height: 64px;
    font-size: 18px !important;
    font-weight: 900 !important;
    border-radius: 16px !important;
    background: linear-gradient(135deg, #765080, #a96983) !important;
}

/* Cards / containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, rgba(67,38,76,.82), rgba(44,25,52,.86));
    border: 1px solid rgba(231,166,184,.22);
    border-radius: 20px;
    box-shadow: 0 12px 30px rgba(17,8,23,.24);
    transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-3px);
    border-color: rgba(242,194,173,.52);
    box-shadow: 0 18px 38px rgba(17,8,23,.34);
}

/* Login / signup container: warm, calm and centered */
[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stForm"]) {
    background:
        radial-gradient(circle at 90% 0%, rgba(217,196,238,.13), transparent 34%),
        linear-gradient(145deg, rgba(59,34,67,.94), rgba(37,20,46,.96));
    border-color: rgba(242,194,173,.28);
    box-shadow: 0 24px 60px rgba(11,5,15,.35);
}

.stTextInput input,
.stTextArea textarea {
    background: rgba(255,248,239,.96);
    color: #35243a;
    border: 1px solid rgba(231,166,184,.55);
    border-radius: 13px;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #8f8291;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #e7a6b8;
    box-shadow: 0 0 0 3px rgba(231,166,184,.16);
}

.stSelectbox label,
.stRadio label,
.stTextInput label,
.stFileUploader label {
    color: #fff4f7 !important;
    font-weight: 700;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(69,40,78,.86), rgba(43,25,51,.90));
    padding: 18px;
    border: 1px solid rgba(231,166,184,.22);
    border-radius: 17px;
    transition: transform .2s ease, border-color .2s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: rgba(242,194,173,.58);
}

hr {
    border-color: rgba(231,166,184,.20);
}

[data-testid="stImage"] img {
    border-radius: 16px;
    box-shadow: 0 10px 24px rgba(15,7,20,.22);
    transition: transform .22s ease, box-shadow .22s ease;
}

[data-testid="stImage"] img:hover {
    transform: scale(1.012);
    box-shadow: 0 15px 30px rgba(15,7,20,.30);
}

[data-testid="stAlert"] {
    border-radius: 15px;
}

/* Sidebar navigation */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 7px;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 13px;
    padding: 9px 11px;
    color: #fff4f7 !important;
    transition: background .18s ease, transform .18s ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(242,194,173,.10);
    transform: translateX(3px);
}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(231,166,184,.24), rgba(217,196,238,.10));
    border: 1px solid rgba(242,194,173,.30);
}

button[data-baseweb="tab"] {
    border-radius: 12px 12px 0 0;
    color: #f8edf5 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: rgba(231,166,184,.13);
}

/* Hero */
.yaadein-hero {
    position: relative;
    overflow: hidden;
    padding: 32px 34px;
    margin: 4px 0 24px 0;
    border-radius: 26px;
    border: 1px solid rgba(242,194,173,.28);
    background:
        radial-gradient(circle at 88% 18%, rgba(242,194,173,.22), transparent 25%),
        radial-gradient(circle at 15% 110%, rgba(191,216,195,.13), transparent 28%),
        linear-gradient(125deg, rgba(29,18,36,.94), rgba(76,42,85,.92), rgba(54,31,64,.96));
    box-shadow: 0 18px 44px rgba(12,5,17,.28);
}

.yaadein-hero::after {
    content: "";
    position: absolute;
    width: 170px;
    height: 170px;
    right: -55px;
    bottom: -75px;
    border-radius: 50%;
    background: rgba(231,166,184,.10);
    filter: blur(2px);
}

.yaadein-hero h1 {
    font-size: clamp(30px, 4vw, 46px);
    letter-spacing: -1px;
    line-height: 1.15;
    margin: 0 0 8px 0;
    background: linear-gradient(90deg, #fff8ef, #eadcf6 55%, #f2c2ad);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.yaadein-hero p {
    margin: 0;
    color: #eadcf2 !important;
    font-size: 15px;
    line-height: 1.65;
}

[data-testid="stAppViewContainer"] .main .block-container {
    animation: yaadeinFadeUp 420ms ease-out both;
}

@keyframes yaadeinFadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Soft celebration */
@keyframes yaadeinShimmerSweep {
    0% { background-position: -180% 0; }
    100% { background-position: 180% 0; }
}

.yaadein-shimmer {
    position: relative;
    overflow: hidden;
    margin: 10px 0 18px 0;
    padding: 16px 20px;
    border-radius: 17px;
    border: 1px solid rgba(242,194,173,.36);
    background:
        linear-gradient(110deg, rgba(231,166,184,.15) 8%, rgba(242,194,173,.36) 18%, rgba(231,166,184,.15) 33%),
        linear-gradient(120deg, rgba(76,42,85,.72), rgba(42,23,50,.92));
    background-size: 250% 100%, 100% 100%;
    animation: yaadeinShimmerSweep 3.2s ease-in-out infinite;
    text-align: center;
    font-size: 17px;
    font-weight: 800;
    color: #fff7f1;
    box-shadow: 0 10px 26px rgba(52,25,53,.22);
}

.yaadein-tagline {
    text-align: center;
    font-size: 15px;
    letter-spacing: .2px;
    color: #f1dbe5 !important;
    margin: -6px 0 18px 0;
}

.yaadein-footer {
    padding: 16px 18px;
    border: 1px solid rgba(242,194,173,.20);
    border-radius: 16px;
    background: rgba(29,18,36,.46);
    color: #eadcf2;
    text-align: center;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# HERO FUNCTION
# ==================================================

def render_hero(title, subtitle, eyebrow="YADEIN • FAMILY MEMORY SPACE"):

    html_content = f"""<section class="yaadein-hero">
<div style="font-size:11px; letter-spacing:2.2px; font-weight:800; color:#D8B4FE; margin-bottom:10px;">{eyebrow}</div>
<h1>{title}</h1>
<p>{subtitle}</p>
</section>"""

    st.markdown(html_content, unsafe_allow_html=True)


def render_shimmer_banner(message):
    """A celebratory banner with a soft shimmer sweep --
    used for correct quiz answers and matched pairs, so
    the good moments feel a little more alive than a
    plain st.success() box."""

    st.markdown(
        f'<div class="yaadein-shimmer">{message}</div>',
        unsafe_allow_html=True
    )


def render_tagline(text):
    """A small centered tagline shown under a page's hero --
    this is where your PPT taglines go once you share them."""

    st.markdown(
        f'<p class="yaadein-tagline">{text}</p>',
        unsafe_allow_html=True
    )
