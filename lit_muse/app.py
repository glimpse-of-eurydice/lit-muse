from urllib.parse import quote

import streamlit as st

from lit_muse.core import MODEL_OPTIONS, analyze_text_for_music


st.set_page_config(page_title="Lit-Muse: The Text Composer", page_icon="🎵")

st.title("🎵 Lit-Muse: Find the Perfect BGM for Your Text")
st.write("Paste a text snippet and get a curated soundtrack with Spotify search links.")

with st.sidebar:
    st.header("Configuration")
    model_label = st.selectbox("Choose your model", list(MODEL_OPTIONS.keys()))
    selected_api_env = MODEL_OPTIONS[model_label]["api_env"]
    api_key = st.text_input(f"Enter your {selected_api_env}", type="password")

text_input = st.text_area(
    "Paste your text snippet (50-1000 words recommended):",
    height=220,
)

genre = st.selectbox(
    "Choose your preferred music genre:",
    ["Any", "Instrumental", "Jazz", "Classical", "Rock", "Pop", "Indie", "J-Rock"],
)

if st.button("Extract Vibe and Generate Playlist"):
    if not text_input.strip():
        st.warning("Please enter a text snippet before generating a playlist.")
    elif not api_key.strip():
        st.warning(f"Please enter your {selected_api_env} in the sidebar.")
    else:
        with st.spinner("Analyzing your text and building a playlist..."):
            result = analyze_text_for_music(
                text=text_input,
                genre=genre,
                api_key=api_key,
                model_label=model_label,
            )

        error_message = result.get("error")
        if error_message:
            st.error(error_message)
        else:
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
                st.warning("No tracks were returned. Try again with a different text snippet.")
            else:
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
