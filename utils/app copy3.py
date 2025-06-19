"""
app_modified.py – ChatGPT-style UI with Compact Input + Fixed Audio Button
"""

import streamlit as st
from azure_openai_utils import get_client, load_config, chat_completion
from azure_speech_utils import text_to_speech, speech_to_text

cfg = load_config("GenAISetup3.json")
CLIENT = get_client()

st.set_page_config(page_title="Chat with Voice", layout="centered")

# Inject CSS for compact, fixed input + audio upload next to it
st.markdown(
    """
    <style>
    .block-container {
        padding-bottom: 5rem;
    }
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 1rem;
        left: 1rem;
        right: 6rem;
        z-index: 9999;
    }
    textarea {
        font-size: 1.2rem !important;
        height: 2.5rem !important;
    }
    [data-testid="stFileUploader"] {
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        z-index: 9999;
    }
    [data-testid="stFileUploader"] > div {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 3rem;
        height: 3rem;
        background-color: #262730;
        border-radius: 0.5rem;
    }
    [data-testid="stFileUploader"] label {
        font-size: 1.4rem;
        padding: 0;
        cursor: pointer;
    }
    [data-testid="stFileUploader"] span {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": cfg["systemPrompt"]}
    ]

st.sidebar.checkbox("🔊 Speak assistant replies", key="play_audio", value=True)

for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Chat input field only (smaller width, fixed)
user_input = st.chat_input("Type your message …")

# Fixed-position mic uploader (to the right of chat input)
wav_file = st.file_uploader("🎙️", type=["wav"], label_visibility="visible")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("GPT is thinking …"):
        reply = chat_completion(CLIENT, cfg, st.session_state.messages)

    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

    if st.session_state.get("play_audio", True):
        st.audio(text_to_speech(reply), format="audio/wav")

if wav_file is not None:
    wav_bytes = wav_file.read()
    st.audio(wav_bytes, format="audio/wav")

    with st.spinner("Transcribing …"):
        transcript = speech_to_text(wav_bytes)

    if transcript:
        st.chat_message("user").markdown(transcript)
        st.session_state.messages.append({"role": "user", "content": transcript})

        with st.spinner("GPT is replying …"):
            reply = chat_completion(CLIENT, cfg, st.session_state.messages)

        st.chat_message("assistant").markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        if st.session_state.get("play_audio", True):
            st.audio(text_to_speech(reply), format="audio/wav")
    else:
        st.warning("⚠️ Could not understand that recording – try again?")
