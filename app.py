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
# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title("♥ Yaadein")

    st.caption("YOUR FAMILY • YOUR MEMORIES • YOUR COMPANION 🌷")

    st.divider()

    st.caption(
        "\U0001F510 Logged in as: "
        + str(st.session_state.get("current_username", "admin"))
    )

    st.divider()

    # Handle navigation redirect before the radio widget renders
    if st.session_state.get("requested_page"):
        st.session_state.main_navigation_radio = st.session_state.requested_page
        st.session_state.navigation = st.session_state.requested_page
        st.session_state.requested_page = None

    selected_page = st.radio(
        "Navigation",
        PAGES,
        key="main_navigation_radio"
    )

    st.session_state.navigation = selected_page

    st.divider()

    if st.button("\U0001F6AA Logout", use_container_width=True):

        st.session_state.authenticated = False
        st.session_state.current_username = None
        st.session_state.navigation = "Home"
        st.session_state.requested_page = None

        if "main_navigation_radio" in st.session_state:
            st.session_state.main_navigation_radio = "Home"

        st.session_state.quiz_target = None
        st.session_state.quiz_options = []
        st.session_state.quiz_answered = False
        st.session_state.quiz_score = 0
        st.session_state.quiz_questions = 0
        st.session_state.quiz_result = None
        st.session_state.quiz_streak = 0
        st.session_state.quiz_best_streak = 0

        st.session_state.match_board = []
        st.session_state.match_selected = []
        st.session_state.match_attempts = 0
        st.session_state.match_message = ""
        st.session_state.match_start_time = None
        st.session_state.match_best_attempts = None
        st.session_state.match_just_finished = False

        st.session_state.game_history = []

        st.session_state.delete_confirm_id = None

        st.session_state.walking_reminder_time = None
        st.session_state.walking_duration = 20
        st.session_state.walking_reminder_set = False

        st.rerun()


# ==================================================
# HOME
# ==================================================

if st.session_state.navigation == "Home":

    render_hero(
        "Welcome to Yaadein ♥♥",
        "A beautiful home for the people, photographs, "
        "and moments that make your family unique. \U0001F338",
        "YOUR FAMILY • YOUR MEMORIES • YOUR COMPANION \U0001F4F8"
    )

    render_tagline(
        "♥ Instead of asking an elder to remember random pictures, "
        "Yaadein turns their own family memories into personalized practice. \U0001F338"
    )

    st.write(
        "A special place to preserve family photographs, "
        "celebrate relationships, and revisit beautiful memories. ♥"
    )

    st.divider()

    st.markdown(
        "### \U00002728 Explore Yaadein"
    )

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):

            st.markdown(
                "## \U0001F4F8 Family Photos \U0001F338"
            )

            st.write(
                "Add, view, search, and manage family photographs. ♥"
            )

            if st.button(
                "Open Family Photos",
                key="home_photos",
                use_container_width=True
            ):

                go_to_page(
                    "Family Photos"
                )

    with col2:

        with st.container(border=True):

            st.markdown(
                "## \U0001F4F8 Family Photo Quiz ★"
            )

            st.write(
                "\"Who is this?\" -- with their own family photos, "
                "and gentle feedback that never says Wrong. ♥"
            )

            if st.button(
                "Play Photo Quiz",
                key="home_quiz",
                use_container_width=True
            ):

                go_to_page(
                    "Family Photo Quiz"
                )

    col3, col4 = st.columns(2)

    with col3:

        with st.container(border=True):

            st.markdown(
                "## ★ Memory Match ♥"
            )

            st.write(
                "A card-matching game built from real family faces, "
                "for gentle daily memory practice. \U0001F338"
            )

            if st.button(
                "Play Memory Match",
                key="home_match",
                use_container_width=True
            ):

                go_to_page(
                    "Memory Match"
                )

    with col4:

        with st.container(border=True):

            st.markdown(
                "## ▣ Family Dashboard \U0001F338"
            )

            st.write(
                "Progress, streaks, and the faces that need "
                "a little more practice. ♥"
            )

            if st.button(
                "Open Dashboard",
                key="home_dashboard",
                use_container_width=True
            ):

                go_to_page(
                    "Family Dashboard"
                )

    st.divider()

    col5, col6 = st.columns(2)

    with col5:

        with st.container(border=True):

            st.markdown(
                "## \U0001F6B6 Walking Reminder \U0001F338"
            )

            st.write(
                "Set a daily reminder for a healthy walking break. ♥"
            )

            if st.button(
                "Set Walking Reminder",
                key="home_walking",
                use_container_width=True
            ):

                go_to_page(
                    "Walking Reminder"
                )

    with col6:

        with st.container(border=True):

            st.markdown(
                "## ♥ Healthy Break \U0001F338"
            )

            st.write(
                "Take a short walk and refresh your mind and body. ♥"
            )

    # ----------------------------------------------------
    # LIVE HIGHLIGHTS STRIP
    # A quick, personal snapshot of how the games have gone
    # so far this session -- keeps Home feeling alive instead
    # of static, and gives first-time visitors (judges!) an
    # instant sense that the app is actually being used.
    # ----------------------------------------------------

    st.divider()

    if st.session_state.game_history:

        st.markdown("### 🌷 This Session's Highlights")

        highlight_col1, highlight_col2, highlight_col3 = st.columns(3)

        with highlight_col1:

            st.metric(
                "★ Quiz Best Streak",
                f"{st.session_state.quiz_best_streak} in a row"
            )

        with highlight_col2:

            if st.session_state.match_best_attempts is not None:

                st.metric(
                    "★ Match Best Score",
                    f"{st.session_state.match_best_attempts} attempts"
                )

            else:

                st.metric(
                    "★ Match Best Score",
                    "Not played yet"
                )

        with highlight_col3:

            st.metric(
                "\U0001F4C8 Games Played",
                len(st.session_state.game_history)
            )

        st.caption(
            "See the full breakdown any time on the Family Dashboard."
        )

    else:

        st.info(
            "♥ Every photograph holds a story. \U0001F338 "
            "Play the Photo Quiz or Memory Match to start "
            "building this family's highlight reel. ♥"
        )
# ==================================================
# FAMILY PHOTOS
# ==================================================

elif st.session_state.navigation == "Family Photos":

    render_hero(
        "Family Photos \U0001F4F8\U0001F49B",
        "Keep your favourite faces and family stories "
        "together in one beautiful collection. \U0001F338",
        "MEMORY GALLERY \U0001F499"
    )

    with st.expander(
        "➕ Add a Family Member",
        expanded=True
    ):

        with st.form(
            "add_member_form",
            clear_on_submit=True
        ):

            member_name = st.text_input(
                "Full Name"
            )

            relationship = st.selectbox(
                "Relationship",
                [
                    "Father",
                    "Mother",
                    "Brother",
                    "Sister",
                    "Grandfather",
                    "Grandmother",
                    "Uncle",
                    "Aunt",
                    "Cousin",
                    "Spouse",
                    "Child",
                    "Other"
                ]
            )

            uploaded_photo = st.file_uploader(
                "Upload Photograph",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ]
            )

            add_button = st.form_submit_button(
                "Save Family Member",
                use_container_width=True
            )

            if add_button:

                if not member_name.strip():

                    st.error(
                        "Please enter the family member's name."
                    )

                elif uploaded_photo is None:

                    st.error(
                        "Please upload a photograph."
                    )

                else:

                    add_family_member(
                        member_name,
                        relationship,
                        uploaded_photo
                    )

                    st.success(
                        f"{member_name.strip()} has been added!"
                    )

                    st.rerun()

    st.divider()

    st.subheader(
        "Your Family Collection"
    )

    search_text = st.text_input(
        "\U0001F50E Search by name or relationship",
        placeholder="Type a name or relationship..."
    )

    members = get_all_members()

    if search_text.strip():

        query = search_text.strip().casefold()

        members = [
            member
            for member in members
            if (
                query in member["name"].casefold()
                or query in member["relationship"].casefold()
            )
        ]

    if not members:

        st.info(
            "No family members found."
        )

    else:

        st.caption(
            f"{len(members)} family member(s) displayed."
        )

        for start in range(
            0,
            len(members),
            3
        ):

            row_members = members[
                start:start + 3
            ]

            columns = st.columns(3)

            for column, member in zip(
                columns,
                row_members
            ):

                with column:

                    with st.container(border=True):

                        photo_path = member.get(
                            "photo_path"
                        )

                        if (
                            photo_path
                            and Path(
                                photo_path
                            ).is_file()
                        ):

                            st.image(
                                photo_path,
                                use_container_width=True
                            )

                        else:

                            st.markdown(
                                "<div style='text-align:center; font-size:70px;'>\U0001F464</div>",
                                unsafe_allow_html=True
                            )

                        st.markdown(
                            f"### {member['name']}"
                        )

                        st.write(
                            "**Relationship:** "
                            + str(
                                member["relationship"]
                            )
                        )

                        if st.button(
                            "Delete Member",
                            key=f"delete_{member['id']}",
                            use_container_width=True
                        ):

                            st.session_state.delete_confirm_id = (
                                member["id"]
                            )

                            st.rerun()

    delete_id = st.session_state.get(
        "delete_confirm_id"
    )

    if delete_id is not None:

        member_to_delete = next(
            (
                member
                for member in get_all_members()
                if member["id"] == delete_id
            ),
            None
        )

        if member_to_delete:

            st.warning(
                f"Delete {member_to_delete['name']} "
                "and their stored photograph?"
            )

            confirm_col, cancel_col = st.columns(2)

            with confirm_col:

                if st.button(
                    "Yes, Delete",
                    type="primary",
                    key="confirm_delete"
                ):

                    delete_family_member(
                        delete_id
                    )

                    st.session_state.delete_confirm_id = None

                    st.rerun()

            with cancel_col:

                if st.button(
                    "Cancel",
                    key="cancel_delete"
                ):

                    st.session_state.delete_confirm_id = None

                    st.rerun()
# ==================================================
# FAMILY PHOTO QUIZ
# ==================================================

elif st.session_state.navigation == "Family Photo Quiz":

    render_hero(
        "📷 Family Photo Quiz ★",
        "\"Who is this?\" -- turned into a warm, gentle guessing game "
        "with your own family photos. 🌷",
        "PLAY • REMEMBER • CELEBRATE ♥"
    )

    render_tagline(
        "\U0001F499 Gentle feedback, always -- we say "
        "\"Let's try again\", never \"Wrong!\""
    )

    members = get_all_members()

    if len(members) < 2:

        st.warning(
            "Add at least two family members to play the quiz."
        )

    else:

        # --------------------------------------------
        # LIVE STATS STRIP
        # Accuracy and streak turn a simple right/wrong
        # quiz into something that feels like it is
        # actually tracking your progress.
        # --------------------------------------------

        accuracy = 0

        if st.session_state.quiz_questions > 0:

            accuracy = round(
                (
                    st.session_state.quiz_score
                    / st.session_state.quiz_questions
                )
                * 100
            )

        score_col, question_col, streak_col, accuracy_col = st.columns(4)

        with score_col:

            st.metric(
                "Correct Answers",
                st.session_state.quiz_score
            )

        with question_col:

            st.metric(
                "Questions Answered",
                st.session_state.quiz_questions
            )

        with streak_col:

            st.metric(
                "\U0001F525 Current Streak",
                st.session_state.quiz_streak,
                help="Best streak this session: "
                     f"{st.session_state.quiz_best_streak}"
            )

        with accuracy_col:

            st.metric(
                "★ Accuracy",
                f"{accuracy}%"
            )

        if st.session_state.quiz_questions > 0:

            st.progress(
                accuracy / 100,
                text=f"{accuracy}% correct so far"
            )

        st.divider()

        if st.session_state.quiz_target is None:

            if st.button(
                "▶️ Start Quiz",
                use_container_width=True
            ):

                target = random.choice(
                    members
                )

                other_members = [
                    member
                    for member in members
                    if member["id"] != target["id"]
                ]

                wrong_options = random.sample(
                    other_members,
                    min(
                        3,
                        len(other_members)
                    )
                )

                options = [
                    target
                ] + wrong_options

                random.shuffle(
                    options
                )

                st.session_state.quiz_target = target
                st.session_state.quiz_options = options
                st.session_state.quiz_answered = False
                st.session_state.quiz_result = None

                st.rerun()

        else:

            target = st.session_state.quiz_target

            photo_path = target.get(
                "photo_path"
            )

            if (
                photo_path
                and Path(
                    photo_path
                ).is_file()
            ):

                st.image(
                    photo_path,
                    caption="Who is this family member?",
                    width=350
                )

            else:

                st.warning(
                    "This member's photograph is unavailable."
                )

            option_names = [
                member["name"]
                for member
                in st.session_state.quiz_options
            ]

            # Large, touch-friendly name buttons.
            # Selecting a name immediately checks the answer;
            # there is no radio button and no extra "Check Answer" step.
            if not st.session_state.quiz_answered:

                st.markdown(
                    "<div style='text-align:center; color:#DDD6FE; "
                    "font-size:15px; font-weight:700; margin:8px 0 10px 0;'>"
                    "Choose the family member:</div>",
                    unsafe_allow_html=True
                )

                option_columns = st.columns(len(option_names))

                for option_index, option_name in enumerate(option_names):

                    with option_columns[option_index]:

                        if st.button(
                            option_name,
                            key=f"quiz_option_{st.session_state.quiz_target['id']}_{option_index}",
                            use_container_width=True
                        ):

                            st.session_state.quiz_answered = True

                            st.session_state.quiz_questions += 1

                            if option_name == target["name"]:

                                st.session_state.quiz_score += 1

                                st.session_state.quiz_streak += 1

                                if (
                                    st.session_state.quiz_streak
                                    > st.session_state.quiz_best_streak
                                ):

                                    st.session_state.quiz_best_streak = (
                                        st.session_state.quiz_streak
                                    )

                                st.session_state.quiz_result = (
                                    "correct"
                                )

                            else:

                                st.session_state.quiz_streak = 0

                                st.session_state.quiz_result = (
                                    "incorrect"
                                )

                            st.session_state.game_history.append(
                                {
                                    "game": "Family Photo Quiz",
                                    "detail": (
                                        f"Guessed {target['name']} "
                                        + (
                                            "correctly"
                                            if st.session_state.quiz_result
                                            == "correct"
                                            else "incorrectly"
                                        )
                                    ),
                                }
                            )

                            st.rerun()

            else:

                if (
                    st.session_state.quiz_result
                    == "correct"
                ):

                    correct_messages = [
                        "\U0001F389 Correct! You know this face so well. ♥",
                        "🌷 Spot on -- that's exactly right!",
                        "✨ Beautifully remembered!",
                        "\U0001F3C6 Yes! A memory held close. \U0001F499",
                    ]

                    render_shimmer_banner(
                        random.choice(correct_messages)
                    )

                    st.balloons()

                    if st.session_state.quiz_streak >= 3:

                        st.toast(
                            f"\U0001F525 {st.session_state.quiz_streak} "
                            "in a row! Keep going!"
                        )

                else:

                    # --------------------------------------------
                    # GENTLE FEEDBACK
                    # The pitch promises we never say "Wrong!" --
                    # a soft, encouraging nudge instead of a harsh
                    # red error, so the moment stays motivating
                    # rather than discouraging.
                    # --------------------------------------------

                    st.markdown(
                        "<div style='background: rgba(96,165,250,.12); "
                        "border: 1px solid rgba(96,165,250,.35); "
                        "border-radius: 14px; padding: 14px 18px; "
                        "color: #E0F2FE; font-size: 16px;'>"
                        f"🌷 Let's try again -- this is "
                        f"<b>{target['name']}</b>. Every attempt helps "
                        "the memory grow a little stronger. ♥"
                        "</div>",
                        unsafe_allow_html=True
                    )

                if st.button(
                    "Next Question",
                    use_container_width=True
                ):

                    st.session_state.quiz_target = None

                    st.session_state.quiz_options = []

                    st.session_state.quiz_answered = False

                    st.session_state.quiz_result = None

                    st.rerun()

        if st.button(
            "\U0001F504 Reset Quiz Score"
        ):

            st.session_state.quiz_target = None
            st.session_state.quiz_options = []
            st.session_state.quiz_answered = False
            st.session_state.quiz_score = 0
            st.session_state.quiz_questions = 0
            st.session_state.quiz_result = None
            st.session_state.quiz_streak = 0
            # quiz_best_streak is intentionally kept --
            # it is a lifetime personal best, not a
            # per-round counter.

            st.rerun()
# ==================================================
# MEMORY MATCH
# ==================================================

elif st.session_state.navigation == "Memory Match":

    render_hero(
        "Memory Match \U0001F3AE♥",
        "Flip the cards, remember the faces, "
        "and find every matching pair. 🌷",
        "A LITTLE MEMORY CHALLENGE \U0001F499"
    )

    render_tagline(
        "🌷 A card-matching game built from real family photos, "
        "not random images."
    )

    members = get_all_members()

    members_with_photos = [
        member
        for member in members
        if (
            member.get("photo_path")
            and Path(
                member["photo_path"]
            ).is_file()
        )
    ]

    if len(members_with_photos) < 2:

        st.warning(
            "Add at least two family members "
            "with photographs to play."
        )

    else:

        if st.session_state.match_best_attempts is not None:

            st.caption(
                "\U0001F3C6 Your best game so far: "
                f"{st.session_state.match_best_attempts} attempts"
            )

        if st.button(
            "\U0001F3AE New Game",
            use_container_width=True
        ):

            pair_count = min(
                6,
                len(members_with_photos)
            )

            chosen_members = random.sample(
                members_with_photos,
                pair_count
            )

            board = []

            for member in chosen_members:

                for _ in range(2):

                    board.append(
                        {
                            "member_id": member["id"],
                            "name": member["name"],
                            "photo_path": member["photo_path"],
                            "card_id": uuid.uuid4().hex,
                            "matched": False
                        }
                    )

            random.shuffle(board)

            st.session_state.match_board = board

            st.session_state.match_selected = []

            st.session_state.match_attempts = 0

            st.session_state.match_message = ""

            st.session_state.match_start_time = time.time()

            st.session_state.match_just_finished = False

            st.rerun()

        board = st.session_state.match_board

        if board:

            matched_pairs = sum(
                1
                for card in board
                if card["matched"]
            ) // 2

            total_pairs = len(board) // 2

            elapsed_seconds = 0

            if st.session_state.match_start_time:

                elapsed_seconds = int(
                    time.time() - st.session_state.match_start_time
                )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Pairs Found",
                    f"{matched_pairs}/{total_pairs}"
                )

            with col2:

                st.metric(
                    "Attempts",
                    st.session_state.match_attempts
                )

            with col3:

                st.metric(
                    "Remaining",
                    total_pairs - matched_pairs
                )

            with col4:

                st.metric(
                    "Time",
                    f"{elapsed_seconds}s"
                )

            st.progress(
                matched_pairs / total_pairs,
                text=f"{matched_pairs} of {total_pairs} pairs found"
            )

            st.divider()

            for start in range(
                0,
                len(board),
                4
            ):

                row_cards = board[
                    start:start + 4
                ]

                columns = st.columns(4)

                for column, card in zip(
                    columns,
                    row_cards
                ):

                    with column:

                        with st.container(border=True):

                            revealed = (
                                card["card_id"]
                                in st.session_state.match_selected
                                or card["matched"]
                            )

                            if revealed:

                                st.image(
                                    card["photo_path"],
                                    use_container_width=True
                                )

                                st.caption(
                                    card["name"]
                                )

                                if card["matched"]:

                                    st.success(
                                        "Matched!"
                                    )

                            else:

                                st.markdown(
                                    "<div style='text-align:center; font-size:60px; padding:15px;'>\U0001F499</div>",
                                    unsafe_allow_html=True
                                )

                                if st.button(
                                    "Reveal",
                                    key=(
                                        "reveal_"
                                        + card["card_id"]
                                    ),
                                    use_container_width=True
                                ):

                                    selected = list(
                                        st.session_state.match_selected
                                    )

                                    if (
                                        card["card_id"]
                                        not in selected
                                        and len(selected) < 2
                                    ):

                                        selected.append(
                                            card["card_id"]
                                        )

                                        st.session_state.match_selected = (
                                            selected
                                        )

                                        if len(selected) == 2:

                                            first = next(
                                                item
                                                for item in board
                                                if item["card_id"]
                                                == selected[0]
                                            )

                                            second = next(
                                                item
                                                for item in board
                                                if item["card_id"]
                                                == selected[1]
                                            )

                                            st.session_state.match_attempts += 1

                                            if (
                                                first["member_id"]
                                                == second["member_id"]
                                            ):

                                                first["matched"] = True

                                                second["matched"] = True

                                                st.session_state.match_selected = []

                                                st.session_state.match_message = (
                                                    "correct"
                                                )

                                            else:

                                                st.session_state.match_message = (
                                                    "wrong"
                                                )

                                    st.rerun()

            if (
                st.session_state.match_message
                == "wrong"
            ):

                st.markdown(
                    "<div style='background: rgba(96,165,250,.12); "
                    "border: 1px solid rgba(96,165,250,.35); "
                    "border-radius: 14px; padding: 14px 18px; "
                    "color: #E0F2FE; font-size: 16px;'>"
                    "🌷 Not a match yet -- take a moment to "
                    "remember them, then flip the cards back. ♥"
                    "</div>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "Hide Cards and Continue",
                    use_container_width=True
                ):

                    st.session_state.match_selected = []

                    st.session_state.match_message = ""

                    st.rerun()

            elif (
                st.session_state.match_message
                == "correct"
            ):

                render_shimmer_banner(
                    "\U0001F389 Beautifully matched! \U0001F499"
                )

                if st.button(
                    "Continue",
                    use_container_width=True
                ):

                    st.session_state.match_message = ""

                    st.rerun()

            if all(
                card["matched"]
                for card in board
            ):

                st.balloons()

                # --------------------------------------------
                # STAR RATING
                # Fewer attempts relative to the number of
                # pairs earns more stars -- turns a flat
                # "you won" message into something worth
                # bragging about.
                # --------------------------------------------

                if st.session_state.match_attempts <= total_pairs * 1.5:
                    stars = "★★★"
                elif st.session_state.match_attempts <= total_pairs * 2.5:
                    stars = "★★"
                else:
                    stars = "★"

                is_new_best = (
                    st.session_state.match_best_attempts is None
                    or st.session_state.match_attempts
                    < st.session_state.match_best_attempts
                )

                if is_new_best:

                    st.session_state.match_best_attempts = (
                        st.session_state.match_attempts
                    )

                render_shimmer_banner(
                    f"{stars}  Congratulations! You matched every pair "
                    f"in {st.session_state.match_attempts} attempts "
                    f"and {elapsed_seconds} seconds. ♥"
                )

                if is_new_best:

                    st.info(
                        "\U0001F3C6 That's a new personal best! \U0001F499"
                    )

                if not st.session_state.match_just_finished:

                    st.session_state.game_history.append(
                        {
                            "game": "Memory Match",
                            "detail": (
                                f"Finished in {st.session_state.match_attempts} "
                                f"attempts ({stars})"
                            ),
                        }
                    )

                    st.session_state.match_just_finished = True
# ==================================================
# WALKING REMINDER
# ==================================================

elif st.session_state.navigation == "Walking Reminder":

    render_hero(
        "Walking Reminder \U0001F6B6\U0001F49B",
        "Set a simple daily reminder for a healthy walking break. \U0001F338",
        "A LITTLE WALK, EVERY DAY \U0001F499"
    )

    st.subheader(
        "\U0001F6B6 Daily Walking Reminder"
    )

    reminder_time = st.time_input(
        "Choose your walking reminder time",
        key="walking_reminder_time_input"
    )

    duration = st.number_input(
        "Walking duration (minutes)",
        min_value=5,
        max_value=120,
        value=st.session_state.walking_duration,
        step=5,
        key="walking_duration_input"
    )

    if st.button(
        "\U0001F514 Set Walking Reminder",
        use_container_width=True
    ):

        st.session_state.walking_reminder_time = (
            reminder_time
        )

        st.session_state.walking_duration = (
            int(duration)
        )

        st.session_state.walking_reminder_set = True

        st.success(
            f"Walking reminder set for "
            f"{reminder_time.strftime('%I:%M %p')} "
            f"for {int(duration)} minutes. \U0001F6B6"
        )

    if st.session_state.walking_reminder_set:

        saved_time = (
            st.session_state.walking_reminder_time
        )

        saved_duration = (
            st.session_state.walking_duration
        )

        st.divider()

        st.success(
            f"\U0001F499 Reminder active: "
            f"{saved_time.strftime('%I:%M %p')} "
            f"for {saved_duration} minutes."
        )

        if st.button(
            "Turn Off Walking Reminder",
            use_container_width=True
        ):

            st.session_state.walking_reminder_set = False

            st.session_state.walking_reminder_time = None

            st.rerun()
# ==================================================
# FAMILY DASHBOARD
# ==================================================

elif st.session_state.navigation == "Family Dashboard":

    render_hero(
        "Family Dashboard \U0001F4CA\U0001F49B",
        "Progress, streaks, and the faces that need "
        "a little more practice. \U0001F338",
        "YOUR FAMILY AT A GLANCE \U0001F499"
    )

    members = get_all_members()

    total_members = len(members)

    total_photos = sum(
        1
        for member in members
        if (
            member.get("photo_path")
            and Path(
                member["photo_path"]
            ).is_file()
        )
    )

    relationship_count = {}

    for member in members:

        relationship = member["relationship"]

        relationship_count[relationship] = (
            relationship_count.get(
                relationship,
                0
            ) + 1
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "\U0001F468‍\U0001F469‍‍\U0001F467‍\U0001F466 Family Members",
            total_members
        )

    with col2:

        st.metric(
            "\U0001F4F8 Available Photos",
            total_photos
        )

    with col3:

        st.metric(
            "\U0001F499 Relationships",
            len(relationship_count)
        )

    st.divider()

    st.subheader(
        "\U0001F338 Relationship Summary"
    )

    if not relationship_count:

        st.info(
            "No family members have been added yet."
        )

    else:

        sorted_relationships = sorted(
            relationship_count.items(),
            key=lambda item: item[1],
            reverse=True
        )

        for relationship, count in sorted_relationships:

            col1, col2 = st.columns(
                [2, 3]
            )

            with col1:

                st.write(
                    f"**{relationship}**"
                )

            with col2:

                st.progress(
                    count / total_members
                )

                st.caption(
                    f"{count} member(s)"
                )

    st.divider()

    # ----------------------------------------------------
    # GAME ACTIVITY
    # Pulls together everything that happened in the Photo
    # Quiz and Memory Match into one place, so the dashboard
    # tells the whole story of the app, not just the photo
    # collection.
    # ----------------------------------------------------

    st.subheader(
        "\U0001F3AE Game Activity \U0001F49B"
    )

    quiz_accuracy = 0

    if st.session_state.quiz_questions > 0:

        quiz_accuracy = round(
            (
                st.session_state.quiz_score
                / st.session_state.quiz_questions
            )
            * 100
        )

    activity_col1, activity_col2, activity_col3, activity_col4 = st.columns(4)

    with activity_col1:

        st.metric(
            "Quiz Questions Answered",
            st.session_state.quiz_questions
        )

    with activity_col2:

        st.metric(
            "Quiz Accuracy",
            f"{quiz_accuracy}%"
        )

    with activity_col3:

        st.metric(
            "\U0001F525 Best Quiz Streak",
            st.session_state.quiz_best_streak
        )

    with activity_col4:

        if st.session_state.match_best_attempts is not None:

            st.metric(
                "\U0001F3AE Best Match Score",
                f"{st.session_state.match_best_attempts} attempts"
            )

        else:

            st.metric(
                "\U0001F3AE Best Match Score",
                "Not played yet"
            )

    if st.session_state.game_history:

        st.markdown("**Recent Activity**")

        recent_events = list(
            reversed(st.session_state.game_history)
        )[:5]

        for event in recent_events:

            icon = (
                "\U0001F3AF"
                if event["game"] == "Family Photo Quiz"
                else "\U0001F3AE"
            )

            st.write(
                f"{icon} **{event['game']}** — {event['detail']}"
            )

    else:

        st.info(
            "No games played yet. Visit the Family Photo Quiz "
            "or Memory Match page to get started."
        )

    st.divider()

    st.subheader(
        "\U0001F499 Family Members"
    )

    if not members:

        st.info(
            "Your family collection is currently empty."
        )

    else:

        for member in members:

            col1, col2, col3 = st.columns(
                [1, 3, 2]
            )

            with col1:

                photo_path = member.get(
                    "photo_path"
                )

                if (
                    photo_path
                    and Path(
                        photo_path
                    ).is_file()
                ):

                    st.image(
                        photo_path,
                        width=70
                    )

                else:

                    st.write(
                        "\U0001F464"
                    )

            with col2:

                st.write(
                    f"**{member['name']}**"
                )

            with col3:

                st.write(
                    member["relationship"]
                )

            st.divider()


# ==================================================
# FOOTER
# ==================================================

st.sidebar.divider()

st.sidebar.caption(
    "\U0001F499 Your Family. Your Memories. Your Companion. \U0001F338"
)
