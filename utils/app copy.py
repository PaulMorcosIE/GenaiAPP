"""
TTS-only version: User types message, GPT responds in text and voice.
Run with: streamlit run app.py
"""

import streamlit as st
from azure_openai_utils import get_client, load_config, chat_completion
from azure_speech_utils import text_to_speech

# ────────────────────── Setup ──────────────────────
cfg    = load_config("GenAISetup3.json")
CLIENT = get_client()

st.set_page_config(page_title="Chat with Voice", layout="centered")
st.title("🧠 GPT Voice Assistant (TTS Only)")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": cfg["systemPrompt"]}
    ]
if "play_audio" not in st.session_state:
    st.session_state.play_audio = True

st.sidebar.checkbox("🔊 Speak assistant replies", key="play_audio")

# ────────────────────── Text input ──────────────────────
user_input = st.chat_input("Type your message here...")
if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get GPT reply
    reply = chat_completion(CLIENT, cfg, st.session_state.messages)
    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Optionally speak it
    if st.session_state.play_audio:
        wav_bytes = text_to_speech(reply)
        st.audio(wav_bytes, format="audio/wav")


