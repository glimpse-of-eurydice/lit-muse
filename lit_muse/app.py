from urllib.parse import quote

import streamlit as st

from lit_muse.core import MODEL_OPTIONS, analyze_book_vibe, analyze_text_for_music


st.set_page_config(page_title="Lit-Muse: The Text Composer", page_icon="🎵")

st.title("🎵 Lit-Muse: Smart Book Search and Text Vibe Playlist")
st.write("Generate a soundtrack from a book context or a text snippet, then add tracks via Spotify search links.")

with st.sidebar:
    st.header("Configuration")
    model_label = st.selectbox("Choose model", list(MODEL_OPTIONS.keys()))
    selected_api_env = MODEL_OPTIONS[model_label]["api_env"]
    api_key = st.text_input(f"Enter your {selected_api_env}", type="password")

genre = st.selectbox(
    "Choose your preferred music genre:",
    ["Any", "Instrumental", "Jazz", "Classical", "Rock", "Pop", "Indie", "J-Rock"],
)

def render_playlist_result(result: dict) -> None:
    error_message = result.get("error")
    if error_message:
        st.error(error_message)
        return

    vibe_keywords = result.get("vibe_keywords", [])
    analysis = result.get("analysis", "")
    tracks = result.get("tracks", [])
    warning_message = result.get("warning")

    st.subheader("Vibe Keywords")
    keywords_text = ", ".join(vibe_keywords) if vibe_keywords else "No keywords returned."
    st.info(keywords_text)

    st.subheader("Atmosphere Analysis")
    st.info(analysis if analysis else "No analysis returned.")

    with st.expander("📌 How to save this to your Spotify?", expanded=True):
        st.write("1. Open Spotify and create a new playlist.")
        st.write("2. Click each search link below to open the song search page in Spotify Web.")
        st.write("3. Add the matching track to your new playlist.")

    st.subheader("Recommended Tracks")
    if warning_message:
        st.warning(warning_message)
    if not tracks:
        st.warning("No tracks were returned. Try again with a different input.")
        return

    for index, track in enumerate(tracks, start=1):
        title = track.get("title", "").strip()
        artist = track.get("artist", "").strip()
        if not title or not artist:
            continue

        query = f"{title} {artist}"
        encoded_query = quote(query)
        spotify_url = f"https://open.spotify.com/search/{encoded_query}"

        st.write(f"{index}. **{title}** - {artist}")
        st.markdown(f"[🔍 Search on Spotify]({spotify_url})")


book_tab, text_tab = st.tabs(["Book Search Mode", "Text Snippet Mode"])

with book_tab:
    book_title = st.text_input("Book Title", placeholder="The Catcher in the Rye")
    author = st.text_input("Author (optional)", placeholder="J.D. Salinger")
    mood = st.text_area(
        "Current Mood/Scenario",
        placeholder="Reading alone in a cozy cafe on a rainy day",
        height=120,
    )

    if st.button("Generate Playlist from Book Context"):
        if not api_key.strip():
            st.warning(f"Please enter your {selected_api_env} in the sidebar.")
        elif not book_title.strip():
            st.warning("Please enter the book title.")
        elif not mood.strip():
            st.warning("Please describe your current mood/scenario.")
        else:
            with st.spinner("Analyzing the book vibe and building your playlist..."):
                result = analyze_book_vibe(
                    title=book_title.strip(),
                    author=author.strip(),
                    mood=mood.strip(),
                    genre=genre,
                    api_key=api_key.strip(),
                    model_label=model_label,
                )
            render_playlist_result(result)

with text_tab:
    text_input = st.text_area(
        "Paste your text snippet (50-1000 words recommended):",
        height=220,
    )

    if st.button("Generate Playlist from Text Snippet"):
        if not api_key.strip():
            st.warning(f"Please enter your {selected_api_env} in the sidebar.")
        elif not text_input.strip():
            st.warning("Please enter a text snippet before generating a playlist.")
        else:
            with st.spinner("Analyzing your text and building a playlist..."):
                result = analyze_text_for_music(
                    text=text_input.strip(),
                    genre=genre,
                    api_key=api_key.strip(),
                    model_label=model_label,
                )
            render_playlist_result(result)
