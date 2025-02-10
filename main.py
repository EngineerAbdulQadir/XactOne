import streamlit as st
import google.generativeai as genai
import os
import base64
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Set up Gemini API key
genai.configure(api_key="AIzaSyALmE5GLBYqPFTWOJq-cy4tr2MRPXG12Ac")

# Model configuration
MODEL_MAPPING = {
    "XAI SURGE 0.1": "gemini-2.0-flash-exp"
}

# Custom AI Icon (Base64 Encoded)
AI_ICON = "data:image/svg+xml;base64," + base64.b64encode(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="url(#aiGradient)"><defs><linearGradient id="aiGradient" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#6a11cb;stop-opacity:1"/><stop offset="100%" style="stop-color:#2575fc;stop-opacity:1"/></linearGradient></defs><path d="M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8z"/><path d="M8 16l2-4 2 4 2-4 2 4 2-4"/></svg>'.encode()
).decode('utf-8')

# Streamlit page configuration
st.set_page_config(page_title="Xact One", page_icon="🚀", layout="wide")

# --- Custom CSS for Bluish and White Gradient Theme ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2575fc; /* Blue */
            --secondary: #6a11cb; /* Purple */
            --background: linear-gradient(135deg, #ffffff, #e0f7fa); /* White to light blue */
            --text-color: #333; /* Dark text */
            --heading-color: #2575fc; /* Heading color */
        }
        
        body {
            background: var(--background);
            color: var(--text-color);
        }

        * {
            font-family: 'Poppins', sans-serif;
            box-sizing: border-box;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 2rem;
            animation: fadeIn 1s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* General heading styles */
        h1, h2, h3 {
            margin: 0; /* Remove default margin */
            color: var(--heading-color);
        }
        
        /* More specific gradient style for headings and any element with .gradient-text */
        h1.gradient-text, h2.gradient-text, h3.gradient-text, .gradient-text {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            font-weight: 700;
        }
        
        h1 {
            font-size: 2.5rem; /* Adjust size for h1 */
        }

        h2 {
            font-size: 2rem; /* Adjust size for h2 */
        }

        h3 {
            font-size: 1.5rem; /* Adjust size for h3 */
        }

        .emoji {
            font-size: 1.5rem; /* Adjust emoji size */
            vertical-align: middle; /* Align emoji with text */
        }

        .response-card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            border: 1px solid rgba(0,0,0,0.1);
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .typing-indicator {
            display: inline-block;
            position: relative;
            padding-left: 1.5rem;
            color: var(--primary);
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            background: var(--primary);
            border-radius: 50%;
            display: inline-block;
            animation: typing 1.4s infinite;
        }
        
        @keyframes typing {
            0%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
        }

        /* Chat History Styles */
        .history-section {
            margin-top: 1rem;
        }
        .history-item {
            padding: 0.5rem;
            margin: 0.25rem 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            background: rgba(37, 117, 252, 0.05); /* Light blue */
            border: 1px solid rgba(37, 117, 252, 0.1);
        }
        .history-item:hover {
            background: rgba(37, 117, 252, 0.1);
            border-color: rgba(37, 117, 252, 0.2);
        }
        .history-item.active {
            background: rgba(37, 117, 252, 0.15);
            border-color: rgba(37, 117, 252, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar for Settings ---
with st.sidebar:
    st.markdown("<h2 class='gradient-text'>⚙️ Agent Configuration</h2><hr>", unsafe_allow_html=True)
    temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7, help="Higher values produce more creative responses")
    model_display = st.selectbox(
        "AI Model",
        list(MODEL_MAPPING.keys()),
        index=0,
        help="Select Xactrix model variant"
    )
    
    # Chat History Section
    st.markdown("---")
    st.markdown("<h3 class='gradient-text'>💬 Chat History</h3>", unsafe_allow_html=True)
    
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        # Group messages by conversation
        conversations = []
        current_convo = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                if current_convo:
                    conversations.append(current_convo)
                current_convo = [msg]
            else:
                current_convo.append(msg)
        if current_convo:
            conversations.append(current_convo)
        
        # Display conversations
        for i, convo in enumerate(conversations):
            user_msg = convo[0]["content"]
            truncated_msg = (user_msg[:35] + '...') if len(user_msg) > 35 else user_msg
            if st.button(
                f"🗨️ {truncated_msg}",
                key=f"hist_{i}",
                use_container_width=True,
                help="Click to view this conversation"
            ):
                st.session_state.active_convo_idx = i
    
    st.markdown("---")
    st.markdown(f"""
        <div style="text-align: center; margin-top: 2rem;">
            <img src="{AI_ICON}" style="width: 60px; margin-bottom: 1rem;">
            <p style="font-size: 0.9rem; color: #666;">
                Powered by
                <span class="gradient-text" style="font-weight: 600;">
                    Xactrix AI
                </span>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
# --- Header Section ---
st.markdown("""
    <div class="header">
        <h1 class="gradient-text">🚀 Xact One</h1>
        <p style="font-size: 1.2rem; color: #666;">Advanced Problem Solving with Contextual Intelligence</p>
        <div style="height: 3px; background: linear-gradient(90deg, var(--primary), var(--secondary)); margin: 1rem auto; width: 60%;"></div>
    </div>
""", unsafe_allow_html=True)

# --- Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Determine which messages to display
if "active_convo_idx" in st.session_state:
    # Group messages into conversations
    conversations = []
    current_convo = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            if current_convo:
                conversations.append(current_convo)
            current_convo = [msg]
        else:
            current_convo.append(msg)
    if current_convo:
        conversations.append(current_convo)
    
    # Display active conversation
    active_convo = conversations[st.session_state.active_convo_idx]
    for msg in active_convo:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
else:
    # Display all messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

SYSTEM_PROMPT = """You are Xact One, an advanced AI Agent developed by Xactrix AI. Provide comprehensive, 
well-structured responses with clear headings and bullet points when appropriate. 
Always maintain professional yet approachable tone."""

user_input = st.chat_input("Ask Xact One anything...")

if user_input:
    # Reset active conversation when new input is received
    if "active_convo_idx" in st.session_state:
        del st.session_state.active_convo_idx
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            actual_model = MODEL_MAPPING[model_display]
            model = genai.GenerativeModel(actual_model)
            
            conversation = [{"role": "user", "parts": [SYSTEM_PROMPT]}]
            for msg in st.session_state.messages[-4:]:
                conversation.append({"role": msg["role"], "parts": [msg["content"]]})
            
            response = model.generate_content(
                contents=conversation,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048
                ),
                stream=True
            )
            
            typing_indicator = "<div class='typing-indicator'>" + \
                               "<div class='typing-dot' style='animation-delay: 0s'></div>" + \
                               "<div class='typing-dot' style='animation-delay: 0.2s'></div>" + \
                               "<div class='typing-dot' style='animation-delay: 0.4s'></div></div>"
            message_placeholder.markdown(typing_indicator, unsafe_allow_html=True)
            
            for chunk in response:
                full_response += chunk.text
                time.sleep(0.02)
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        except Exception as e:
            full_response = f"⚠️ Error: {str(e)}"
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- Footer ---
st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: #666;">
        <div style="height: 2px; background: linear-gradient(90deg, var(--primary), var(--secondary)); margin: 1rem auto; width: 40%;"></div>
        <p style="font-size: 0.9rem;">
            Made with ❤️ by Engineer Abdul Qadir<br>
            <span style="font-size: 0.8rem;">Version 0.1 | Xactrix AI Engine</span>
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
