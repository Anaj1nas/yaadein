import streamlit as st
import random

st.set_page_config(layout="centered")

st.sidebar.title("Yaadein")
page = st.sidebar.radio("Go to", ["Photo Quiz", "Memory Match"])

if page == "Photo Quiz":
    st.title("Family Photo Quiz")

    people = [
        {"name": "Riya", "image": "images/Riya.jpg"},
        {"name": "Amit", "image": "images/Amit.jpg"},
        {"name": "Grandma", "image": "images/Grandma.jpg"},
    ]

    if "score" not in st.session_state:
        st.session_state.score = 0
    if "answered" not in st.session_state:
        st.session_state.answered = False

    if "quiz_person" not in st.session_state:
        chosen = random.choice(people)
        other_names = [p["name"] for p in people if p["name"] != chosen["name"]]
        opts = [chosen["name"]] + random.sample(other_names, min(2, len(other_names)))
        random.shuffle(opts)
        st.session_state.quiz_person = chosen
        st.session_state.quiz_options = opts

    person = st.session_state.quiz_person
    options = st.session_state.quiz_options

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image(person["image"], width=200)

    st.subheader("Who is this?")
    

    cols = st.columns(len(options))
    for i, name in enumerate(options):
        if cols[i].button(name, type="primary", key=f"quiz_opt_{i}", disabled=st.session_state.answered):
            st.session_state.answered = True
            if name == person["name"]:
                st.session_state.score += 1
                st.session_state.last_result = "correct"
            else:
                st.session_state.last_result = "wrong"
            st.rerun()

    if st.session_state.answered:
        if st.session_state.last_result == "correct":
            st.success("Well done! That's right. 🎉")
        else:
            st.info(f"Let's try again! This is {person['name']}.")

        if st.button("Next photo ▶"):
            del st.session_state.quiz_person
            del st.session_state.quiz_options
            st.session_state.answered = False
            st.rerun()

    st.divider()
    st.write(f"**Score: {st.session_state.score}**")

elif page == "Memory Match":
    import time

    st.title("Memory Match")

    symbols = ["🐶", "🐱", "🐸", "🦋", "🌸", "⭐"]

    if "cards" not in st.session_state:
        cards = symbols + symbols
        random.shuffle(cards)
        st.session_state.cards = cards
        st.session_state.revealed = [False] * len(cards)
        st.session_state.matched = [False] * len(cards)
        st.session_state.picks = []
        st.session_state.moves = 0

    st.write(f"Moves: {st.session_state.moves}")

    cols = st.columns(4)
    for i, symbol in enumerate(st.session_state.cards):
        col = cols[i % 4]

        if st.session_state.matched[i]:
            col.button(symbol, key=f"card_{i}", disabled=True)
        elif st.session_state.revealed[i]:
            col.button(symbol, key=f"card_{i}", disabled=True)
        else:
            if col.button("❓", key=f"card_{i}"):
                st.session_state.revealed[i] = True
                st.session_state.picks.append(i)

                if len(st.session_state.picks) == 2:
                    a, b = st.session_state.picks
                    st.session_state.moves += 1
                    if st.session_state.cards[a] == st.session_state.cards[b]:
                        st.session_state.matched[a] = True
                        st.session_state.matched[b] = True
                    st.session_state.picks = []

                st.rerun()

    revealed_indices = [i for i, r in enumerate(st.session_state.revealed) if r and not st.session_state.matched[i]]
    if len(revealed_indices) == 2:
        time.sleep(0.8)
        for i in revealed_indices:
            st.session_state.revealed[i] = False
        st.rerun()

    if all(st.session_state.matched):
        st.success(f"🎉 You matched everything in {st.session_state.moves} moves!")