import streamlit as st
from google import genai
import os

# 1. Page Title and Interface Setup
st.set_page_config(page_title="Any Language Translator", page_icon="🌐", layout="centered")
st.title("🌐 Any-to-Any Tone Translator")
st.write("Select your starting language and your target language, then type your message!")

# 2. Check for the Secret Key
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ API Key is missing! Make sure you set the GEMINI_API_KEY environment variable.")
else:
    client = genai.Client(api_key=API_KEY)

    # 3. INTERFACE UPGRADE: Two Dropdown Selectors Side-by-Side
    # We use st.columns(2) to create two neat columns on the screen
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

    # 4. We feed BOTH choices dynamically into the AI rules
    ROBOT_RULES = f"""
    You are a real-time conversational chat translator bot.
    The user wants to translate a phrase from {from_language} into natural, fluid {to_language}.

    CRITICAL RULE: Never translate literally word-for-word. Look for the hidden emotion, 
    street slang, friendship context, or cultural intensity of that specific speaker.

    Always output your response in this exact format:
    **Original Language:** [Specify the actual input language used]
    **Translation ({to_language}):** [The natural translation here]
    **Vibe:** [The emotion here, like Friendly, Sarcastic, Angry, Excited, Sad]
    """

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

        # Process via the AI engine
        with st.chat_message("assistant"):
            with st.spinner("Translating tone..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=user_prompt,
                        config=genai.types.GenerateContentConfig(
                            system_instruction=ROBOT_RULES,
                            temperature=0.3
                        )
                    )
                    bot_reply = response.text
                    st.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        st.warning("😴 The AI brain is taking a nap because we used up today's free limits! Please try again in a little while.")
                    else:
                        st.error(f"Something went wrong: {e}")