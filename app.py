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
# ==================================================
# DATABASE
# ==================================================

def get_connection():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn


# ==================================================
# INITIALIZE DATABASE
# ==================================================

def initialize_database():

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS family_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                relationship TEXT NOT NULL,
                photo_path TEXT
            )
        """)

        columns = [
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(family_members)"
            ).fetchall()
        ]

        if "user_id" not in columns:

            conn.execute(
                "ALTER TABLE family_members "
                "ADD COLUMN user_id INTEGER"
            )

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        """)

        user_count = conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        if user_count == 0:

            salt = secrets.token_hex(16)

            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                "Yaadein@123".encode("utf-8"),
                salt.encode("utf-8"),
                200000
            ).hex()

            conn.execute("""
                INSERT INTO users
                (username, password_hash, salt)
                VALUES (?, ?, ?)
            """, (
                "admin",
                password_hash,
                salt
            ))

        admin_user = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            ("admin",)
        ).fetchone()

        if admin_user:

            conn.execute(
                """
                UPDATE family_members
                SET user_id = ?
                WHERE user_id IS NULL
                """,
                (admin_user["id"],)
            )


initialize_database()


# ==================================================
# ACCOUNT FUNCTIONS
# ==================================================

def verify_login(username, password):

    with get_connection() as conn:

        user = conn.execute(
            """
            SELECT username, password_hash, salt
            FROM users
            WHERE username = ?
            """,
            (username.strip(),)
        ).fetchone()

    if user is None:
        return False

    entered_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        user["salt"].encode("utf-8"),
        200000
    ).hex()

    return hmac.compare_digest(
        entered_hash,
        user["password_hash"]
    )


def create_account(username, password):

    username = username.strip()

    if len(username) < 3:

        return (
            False,
            "Username must contain at least 3 characters."
        )

    if len(username) > 30:

        return (
            False,
            "Username cannot exceed 30 characters."
        )

    if not username.replace("_", "").isalnum():

        return (
            False,
            "Use only letters, numbers, and underscores."
        )

    if len(password) < 4:

        return (
            False,
            "Password must contain at least 4 characters."
        )

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000
    ).hex()

    try:

        with get_connection() as conn:

            conn.execute(
                """
                INSERT INTO users
                (username, password_hash, salt)
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    password_hash,
                    salt
                )
            )

        return (
            True,
            "Account created successfully!"
        )

    except sqlite3.IntegrityError:

        return (
            False,
            "This username already exists."
        )


# ==================================================
# USER FUNCTIONS
# ==================================================

def get_current_user_id():

    username = st.session_state.get(
        "current_username"
    )

    if not username:
        return None

    with get_connection() as conn:

        user = conn.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

    if user:
        return user["id"]

    return None


# ==================================================
# FAMILY MEMBER FUNCTIONS
# ==================================================

def get_all_members():

    user_id = get_current_user_id()

    if user_id is None:
        return []

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT id, name, relationship, photo_path
            FROM family_members
            WHERE user_id = ?
            ORDER BY name COLLATE NOCASE
            """,
            (user_id,)
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def add_family_member(
    name,
    relationship,
    uploaded_photo
):

    user_id = get_current_user_id()

    if user_id is None:
        return False

    extension = Path(
        uploaded_photo.name
    ).suffix.lower()

    if extension not in [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    ]:
        extension = ".jpg"

    filename = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    photo_path = PHOTO_DIR / filename

    with open(
        photo_path,
        "wb"
    ) as file:

        file.write(
            uploaded_photo.getbuffer()
        )

    with get_connection() as conn:

        conn.execute(
            """
            INSERT INTO family_members
            (
                user_id,
                name,
                relationship,
                photo_path
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                name.strip(),
                relationship,
                str(photo_path)
            )
        )

    return True


def delete_family_member(member_id):

    user_id = get_current_user_id()

    if user_id is None:
        return

    with get_connection() as conn:

        member = conn.execute(
            """
            SELECT photo_path
            FROM family_members
            WHERE id = ?
            AND user_id = ?
            """,
            (
                member_id,
                user_id
            )
        ).fetchone()

        conn.execute(
            """
            DELETE FROM family_members
            WHERE id = ?
            AND user_id = ?
            """,
            (
                member_id,
                user_id
            )
        )

    if member and member["photo_path"]:

        photo_path = Path(
            member["photo_path"]
        )

        try:

            photo_path.resolve().relative_to(
                PHOTO_DIR.resolve()
            )

            if photo_path.is_file():
                photo_path.unlink()

        except (
            ValueError,
            OSError
        ):
            pass
# ==================================================
# SESSION STATE
# ==================================================

DEFAULT_STATE = {

    "authenticated": False,

    "current_username": None,

    "navigation": "Home",

    "requested_page": None,

    # Quiz
    "quiz_target": None,
    "quiz_options": [],
    "quiz_answered": False,
    "quiz_score": 0,
    "quiz_questions": 0,
    "quiz_result": None,
    "quiz_streak": 0,
    "quiz_best_streak": 0,

    # Memory Match
    "match_board": [],
    "match_selected": [],
    "match_attempts": 0,
    "match_message": "",
    "match_start_time": None,
    "match_best_attempts": None,
    "match_just_finished": False,

    # Shared game activity feed (powers the Family Dashboard)
    "game_history": [],

    # Delete
    "delete_confirm_id": None,

    # Walking Reminder
    "walking_reminder_time": None,
    "walking_duration": 20,
    "walking_reminder_set": False,
}


for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value


PAGES = [
    "Home",
    "Family Photos",
    "Family Photo Quiz",
    "Memory Match",
    "Walking Reminder",
    "Family Dashboard",
]


def go_to_page(page_name):

    st.session_state.requested_page = page_name

    st.rerun()


# ==================================================
# LOGIN PAGE
# ==================================================

if not st.session_state.authenticated:

    st.markdown(
        "<h1 style='text-align: center; font-size: 48px;'>♥ Yaadein ♥</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; font-size: 20px; color: #E2E8F0;'>"
        "Your Family. Your Memories. Your Companion. 🌷</p>",
        unsafe_allow_html=True
    )

    render_tagline(
        "\U0001F4F8 Instead of asking an elder to remember random pictures, "
        "Yaadein turns their own family memories into personalized practice."
    )

    st.divider()

    _, account_column, _ = st.columns(
        [1, 1.2, 1]
    )

    with account_column:

        with st.container(border=True):

            login_tab, signup_tab = st.tabs(
                [
                    "♥ Login",
                    "🌷 Create Account"
                ]
            )

            # ------------------------------
            # LOGIN
            # ------------------------------

            with login_tab:

                st.subheader(
                    "Welcome Back! 🌷"
                )

                with st.form(
                    "login_form"
                ):

                    username_input = st.text_input(
                        "Username",
                        placeholder="Enter your username"
                    )

                    password_input = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password"
                    )

                    login_button = st.form_submit_button(
                        "Login",
                        use_container_width=True
                    )

                    if login_button:

                        if verify_login(
                            username_input,
                            password_input
                        ):

                            st.session_state.authenticated = True

                            st.session_state.current_username = (
                                username_input.strip()
                            )

                            st.session_state.navigation = "Home"

                            st.session_state.requested_page = None

                            st.rerun()

                        else:

                            st.error(
                                "Incorrect username or password."
                            )

            # ------------------------------
            # SIGNUP
            # ------------------------------

            with signup_tab:

                st.subheader(
                    "Join Yaadein ♥"
                )

                st.write(
                    "Create an account to access "
                    "your family memories. 🌷"
                )

                with st.form(
                    "signup_form"
                ):

                    new_username = st.text_input(
                        "Choose Username",
                        placeholder="At least 3 characters"
                    )

                    new_password = st.text_input(
                        "Create Password",
                        type="password",
                        placeholder="At least 4 characters"
                    )

                    confirm_password = st.text_input(
                        "Confirm Password",
                        type="password",
                        placeholder="Enter password again"
                    )

                    signup_button = st.form_submit_button(
                        "Create Account",
                        use_container_width=True
                    )

                    if signup_button:

                        if not new_username.strip():

                            st.error(
                                "Please enter a username."
                            )

                        elif not new_password:

                            st.error(
                                "Please enter a password."
                            )

                        elif new_password != confirm_password:

                            st.error(
                                "Passwords do not match."
                            )

                        else:

                            success, message = create_account(
                                new_username,
                                new_password
                            )

                            if success:

                                st.success(
                                    message
                                )

                                st.info(
                                    "Open the Login tab "
                                    "and sign in."
                                )

                            else:

                                st.error(
                                    message
                                )

    st.stop()
