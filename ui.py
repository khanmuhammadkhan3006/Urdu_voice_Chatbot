import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import uuid  # To generate unique filenames
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI


recognizer = sr.Recognizer()
parser = StrOutputParser()


model = ChatOpenAI(
    model_name='gpt-4o-mini',
    max_tokens=100,
    temperature=0.7,
)


def speak_text(text):
    """Convert text to speech using gTTS and return a unique audio file path."""
    tts = gTTS(text=text, lang='ur')
    unique_filename = f"response_{uuid.uuid4()}.mp3"  # Generate a unique filename
    tts.save(unique_filename)
    return unique_filename



def listen_to_speech():
    """Capture speech for 4 seconds."""
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
        except sr.WaitTimeoutError:
            st.error("Listening timed out while waiting for input.")
            return None
        return audio
    



def convert_audio_to_text(audio_data):
    """Convert speech to text using Google's Speech Recognition API."""
    try:
        text = recognizer.recognize_google(audio_data, language="ur-PK")
        return text
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand the Urdu audio.")
        return None
    except sr.RequestError:
        st.error("Could not request results; check your internet connection.")
        return None




def get_model_response(prompt):
    """Get a response from the model based on user input."""
    chain = model | parser
    response = chain.invoke(prompt)
    return response




# Initialize conversation history if not already done
if "conversation" not in st.session_state:
    st.session_state.conversation = []

st.markdown(
    """
    <style>
    .fixed-bottom {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit UI
st.markdown("<h1 style='text-align: center;'>Talk with me</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])

with col1:
    if st.button("Record"):
        audio_data = listen_to_speech()

        if audio_data:
            user_text = convert_audio_to_text(audio_data)

            if user_text:
                            # Append user input to conversation history
                st.session_state.conversation.append({"user": user_text})

                            # Get model's response
                model_response = get_model_response(user_text)

                            # Append model's response to conversation history
                audio_file = speak_text(model_response)
                st.session_state.conversation.append({"bot": model_response, "audio": audio_file})

with col2:
    # Display each prompt and response from the conversation history
    for message in st.session_state.conversation:
        if "user" in message:
            st.markdown(f"<p style='text-align: right;'>You: {message['user']}</p>", unsafe_allow_html=True)
        if "bot" in message:
            st.markdown(f"<p style='text-align: right;'>Bot: {message['bot']}</p>", unsafe_allow_html=True)
                # Play the unique audio of the bot's response
            st.audio(message["audio"], format='audio/mp3', start_time=0)


