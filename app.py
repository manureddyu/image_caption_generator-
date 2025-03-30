import streamlit as st
import pandas as pd
import os
import pyperclip
import time

# Define file path
CAPTIONS_FILE = r"C:\\Users\\manuj\\captions_combined.txt"

# Streamlit UI setup
st.set_page_config(page_title="AI Video Captions", layout="wide")

# Session state for dark mode and search history
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'copy_message' not in st.session_state:
    st.session_state.copy_message = ""
if 'copy_message_visible' not in st.session_state:
    st.session_state.copy_message_visible = False

# Custom CSS for improved UI
def apply_custom_styles():
    theme = "dark" if st.session_state.dark_mode else "light"
    background = "#1E1E1E" if theme == "dark" else "#F5F5F5"
    text_color = "#FFFFFF" if theme == "dark" else "#000000"
    button_color = "#3498DB" if theme == "light" else "#A29BFE"
    
    st.markdown(
        f"""
        <style>
            body {{ background-color: {background}; color: {text_color}; }}
            .stDataFrame {{ border-radius: 10px; overflow: hidden; }}
            div.stButton > button {{ background-color: {button_color}; color: white; border-radius: 8px; font-weight: bold; }}
            div.stButton > button:hover {{ background-color: #2980B9; }}
            .search-history {{ font-size: 14px; color: {text_color}; }}
            .copy-message {{
                position: fixed;
                top: 50px;
                right: 20px;
                background-color: rgba(0, 128, 0, 0.8);
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 16px;
                z-index: 9999;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
apply_custom_styles()

# Sidebar Settings
st.sidebar.markdown("## ⚙️ **Settings**")
search_query = st.sidebar.text_input("🔍 Search Captions")
available_languages = ["Tamil", "English", "Kannada", "Telugu", "Hindi"]
selected_languages = st.sidebar.multiselect("🌍 Filter by Language", available_languages, default=["English"])

# Dark mode toggle
if st.sidebar.button("🌙 Toggle Dark Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.experimental_rerun()

# Store search history
if search_query and search_query not in st.session_state.search_history:
    st.session_state.search_history.append(search_query)
    if len(st.session_state.search_history) > 5:
        st.session_state.search_history.pop(0)

# Display search history
if st.session_state.search_history:
    st.sidebar.markdown("### 🔍 Recent Searches")
    for past_search in st.session_state.search_history:
        if st.sidebar.button(past_search):
            search_query = past_search
            st.experimental_rerun()
    
    # Add delete search history button
    if st.sidebar.button("🗑️ Clear Search History"):
        st.session_state.search_history = []
        st.experimental_rerun()

# Check if captions file exists
if os.path.exists(CAPTIONS_FILE):
    st.success("📂 Captions file loaded successfully!")
    
    with open(CAPTIONS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    data = []
    current_video = None
    for line in lines:
        line = line.strip()
        if line.startswith("🎥"):
            current_video = line.replace("🎥", "").strip()
        elif line.startswith("🌍"):
            parts = line.split(": ")
            if len(parts) == 2:
                language = parts[0].replace("🌍", "").strip().lower()
                caption = parts[1].strip()
                data.append((current_video, language, caption))
    
    df = pd.DataFrame(data, columns=["Video", "Language", "Caption"])
    df["Language"] = df["Language"].str.lower()
    
    existing_languages = set(df["Language"].unique())
    selected_languages_lower = [lang.lower() for lang in selected_languages]
    missing_languages = [lang.capitalize() for lang in selected_languages_lower if lang not in existing_languages]
    
    if selected_languages:
        df = df[df["Language"].isin(selected_languages_lower)]
    if search_query:
        df = df[df["Caption"].str.contains(search_query, case=False, na=False)]
    
    st.markdown("## 🎥 **AI Video Captions**")
    
    if missing_languages:
        st.warning(f"⚠️ Captions for {', '.join(missing_languages)} are not available!")
        st.markdown("**❗ Try selecting different languages that exist in the dataset.**")
    
    if df.empty:
        st.error("⚠️ No captions found for the selected filters!")
        st.markdown("**❗ Modify search or select available languages.**")
    else:
        for index, row in df.iterrows():
            video = row["Video"]
            caption = row["Caption"]
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(f"**🎬 {video}**")
                st.markdown(f"📜 {caption}")
            with col2:
                if st.button("📋", key=f"copy_{index}"):
                    pyperclip.copy(caption)
                    st.session_state.copy_message = "✅ Caption copied!"
                    st.session_state.copy_message_visible = True
                    st.experimental_rerun()
            
            if video.endswith(".mp4"):
                st.video(video)
            st.write("---")

    # Display top-right message
    if st.session_state.copy_message_visible:
        st.markdown(f'<div class="copy-message">{st.session_state.copy_message}</div>', unsafe_allow_html=True)
        time.sleep(2)
        st.session_state.copy_message_visible = False
        st.experimental_rerun()
else:
    st.error("⚠️ Captions file not found!")
    st.markdown("**🚨 Make sure `captions_combined.txt` is in `C:\\Users\\manuj\\`.**")
