"""
app.py – ChatGPT-style interface with optional .wav upload
Run: streamlit run app.py
"""

import streamlit as st
from azure_openai_utils import get_client, load_config, chat_completion
from azure_speech_utils import text_to_speech, speech_to_text

# ─────────────────── Setup ───────────────────
cfg    = load_config("GenAISetup3.json")
CLIENT = get_client()

st.set_page_config(page_title="Chat with Voice", layout="centered")
st.title("🧠 GPT Voice Assistant (Text + Audio Upload)")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": cfg["systemPrompt"]}
    ]
if "play_audio" not in st.session_state:
    st.session_state.play_audio = True

st.sidebar.checkbox("🔊 Speak assistant replies", key="play_audio")

# ─────────────────── Text input ───────────────────
user_input = st.chat_input("Type a message …")
if user_input:
    # show and store user text
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # GPT reply
    with st.spinner("GPT is thinking …"):
        reply = chat_completion(CLIENT, cfg, st.session_state.messages)
    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

    # optional TTS
    if st.session_state.play_audio:
        st.audio(text_to_speech(reply), format="audio/wav")

# ─────────────────── WAV upload ───────────────────
st.markdown("### 📤 Or upload a voice message (.wav 16 kHz mono)")
wav_file = st.file_uploader("Choose a .wav file", type=["wav"])

if wav_file:
    wav_bytes = wav_file.read()
    st.audio(wav_bytes, format="audio/wav")

    # Transcribe
    with st.spinner("Transcribing your voice …"):
        transcript = speech_to_text(wav_bytes)

    if transcript:
        st.success(f"🗣️ You said: **{transcript}**")
        st.session_state.messages.append({"role": "user", "content": transcript})

        # GPT reply
        with st.spinner("GPT is replying …"):
            reply = chat_completion(CLIENT, cfg, st.session_state.messages)
        st.chat_message("assistant").markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # optional TTS
        if st.session_state.play_audio:
            st.audio(text_to_speech(reply), format="audio/wav")
    else:
        st.warning("⚠️ Could not understand that recording. Try another?")

# ─────────────────── Full chat history ───────────────────
st.divider()
st.markdown("### 📝 Conversation History")
for msg in st.session_state.messages[1:]:
    role = "🧑‍💻 You" if msg["role"] == "user" else "🤖 Assistant"
    st.markdown(f"**{role}:** {msg['content']}")
