import streamlit as st
from google import genai
import os

# 1. This sets up the title and look of our web page
st.set_page_config(page_title="Telugu Tone Bot", page_icon="💬")
st.title("💬 Telugu-English Tone Translator")
st.write("Type casual Telugu to see the real meaning and emotion!")

# 2. Look for the key hidden inside the computer's secret environment variables
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ API Key is missing! Make sure you set the GEMINI_API_KEY environment variable.")
else:
    # Connect to the AI brain
    client = genai.Client(api_key=API_KEY)

    ROBOT_RULES = """
    You are a real-time chat translator bot.
    Take casual Telugu or phonetic Telugu (written in English letters like 'nuvu ela unavu') 
    and translate it into natural, friendly, conversational English.

    CRITICAL RULE: Do not translate literally word-for-word. Look for the hidden emotion, 
    slang, or friendship context.

    Always answer in this exact format:
    **English:** [Natural English translation here]
    **Vibe:** [The emotion here, like Friendly, Sarcastic, Excited, Angry]
    """

    # 3. Memory Box
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show past messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 4. Chat Input
    if user_prompt := st.chat_input("Type your Telugu sentence here..."):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
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
                    st.error(f"Something went wrong: {e}")