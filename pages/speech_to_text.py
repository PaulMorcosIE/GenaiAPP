import streamlit as st
import base64
from azure_openai_utils import get_client, load_config, chat_completion
from azure_speech_utils import speech_to_text

st.set_page_config(page_title="Voice to GPT", page_icon="🎤")
st.title("🎤 Voice Message GPT Assistant")

cfg = load_config("GenAISetup3.json")
client = get_client()

# Track chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": cfg["systemPrompt"]}
    ]

st.markdown("### Record a message and upload:")
audio_file = st.file_uploader("Upload a WAV file (16kHz mono 16-bit)", type=["wav"])

if audio_file:
    wav_bytes = audio_file.read()
    st.audio(wav_bytes, format='audio/wav')

    with st.spinner("Transcribing your voice..."):
        transcript = speech_to_text(wav_bytes)

    if transcript:
        st.chat_message("user").markdown(f"🗣️ {transcript}")
        st.session_state.messages.append({"role": "user", "content": transcript})

        with st.spinner("Getting GPT reply..."):
            reply = chat_completion(client, cfg, st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        st.chat_message("assistant").markdown(reply)
    else:
        st.warning("⚠️ Could not understand your voice. Try uploading a clearer recording?")

# Chat history
st.markdown("---")
st.subheader("🕘 Conversation History")
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
