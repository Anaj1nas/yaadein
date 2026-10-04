import streamlit as st
import random

st.set_page_config(layout="centered")
st.title("Yaadein — Memory Match")

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

# If two cards are picked and don't match, show a Continue button first
if len(st.session_state.picks) == 2:
    a, b = st.session_state.picks
    if st.session_state.cards[a] != st.session_state.cards[b]:
        st.info("No match — click Continue to flip back.")
        if st.button("Continue ▶"):
            st.session_state.revealed[a] = False
            st.session_state.revealed[b] = False
            st.session_state.picks = []
            st.rerun()

cols = st.columns(4)
for i, symbol in enumerate(st.session_state.cards):
    col = cols[i % 4]
    is_locked = len(st.session_state.picks) == 2  # wait for Continue click

    if st.session_state.matched[i]:
        col.button(symbol, key=f"card_{i}", disabled=True)
    elif st.session_state.revealed[i]:
        col.button(symbol, key=f"card_{i}", disabled=True)
    else:
        if col.button("❓", key=f"card_{i}", disabled=is_locked):
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

if all(st.session_state.matched):
    st.success(f"🎉 You matched everything in {st.session_state.moves} moves!")