import streamlit as st
from google import genai
import os

# 1. Page Title and Interface Setup
st.set_page_config(page_title="Any Language Translator", page_icon="🌐", layout="centered")
st.title("🌐 Any-to-Any Tone Translator")
st.write("Select your languages, type your message, and save your API tickets via smart caching!")

# 2. Check for the Secret Key
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ API Key is missing! Make sure you set the GEMINI_API_KEY environment variable.")
else:
    client = genai.Client(api_key=API_KEY)

    # 3. Dropdown Selectors Side-by-Side
    col1, col2 = st.columns(2)
    with col1:
        from_language = st.selectbox(
            "Translate FROM:",
            ["Auto-Detect", "Telugu", "Telugu (English Script / Phonetic)", "English", "Hindi", "Spanish", "French", "Japanese", "Tamil"]
        )
    with col2:
        to_language = st.selectbox(
            "Translate INTO:",
            ["English", "Telugu", "Telugu (English Script / Phonetic)", "Hindi", "Spanish", "French", "Japanese", "Tamil"]
        )

    # 4. THE ULTIMATE UPGRADE: The Cached Engine Function
    # The @st.cache_data decorator tells Streamlit to look into memory first!
    @st.cache_data(show_spinner=False)
    def get_cached_translation(from_lang, to_lang, user_text):
        # This code ONLY runs if this exact match has NEVER been typed before (Cache Miss)
        rules = f"""
        You are a real-time conversational chat translator bot.
        The user wants to translate a phrase from {from_lang} into natural, fluid {to_lang}.

        CRITICAL RULE: Never translate literally word-for-word. Look for the hidden emotion, 
        street slang, friendship context, or cultural intensity of that specific speaker.

        Always output your response in this exact format:
        **Original Language:** [Specify the actual input language used]
        **Translation ({to_lang}):** [The natural translation here]
        **Vibe:** [The emotion here, like Friendly, Sarcastic, Angry, Excited, Sad]
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Using the high-limit fallback model
            contents=user_text,
            config=genai.types.GenerateContentConfig(
                system_instruction=rules,
                temperature=0.3
            )
        )
        return response.text

    # 5. Initialize Chat History Memory
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display past chat bubbles
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 6. Read User Messages in Real-Time
    if user_prompt := st.chat_input("Type your message here..."):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing data streams..."):
                try:
                    # Call our smart cached function
                    bot_reply = get_cached_translation(from_language, to_language, user_prompt)
                    
                    st.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        st.warning("😴 The AI brain is taking a nap because we used up today's free limits! Please try again in a little while.")
                    else:
                        st.error(f"Something went wrong: {e}")