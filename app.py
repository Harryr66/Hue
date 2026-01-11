#!/usr/bin/env python3
"""
Streamlit UI for Hue Voice Chat
Run with: streamlit run app.py
"""

import streamlit as st
import os
from pathlib import Path
import time

# Page config
st.set_page_config(
    page_title="Hue - Voice AI Assistant",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items=None
)

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env', override=True)
except ImportError:
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            st.warning(f"Could not load .env file: {e}")

from wrapped_grok import WrappedGrok

# Initialize session state
if 'hue' not in st.session_state:
    st.session_state.hue = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'is_listening' not in st.session_state:
    st.session_state.is_listening = False
if 'is_speaking' not in st.session_state:
    st.session_state.is_speaking = False
if 'voice_active' not in st.session_state:
    st.session_state.voice_active = False

def initialize_hue():
    """Initialize Hue (WrappedGrok) with API keys."""
    try:
        grok_api_key = os.getenv('GROK_API_KEY')
        serpapi_key = os.getenv('SERPAPI_KEY')
        elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        
        if not grok_api_key or 'your-grok' in grok_api_key.lower():
            return None, "❌ GROK_API_KEY not set in .env file"
        
        if not serpapi_key or 'your-serpapi' in serpapi_key.lower():
            return None, "❌ SERPAPI_KEY not set in .env file"
        
        hue = WrappedGrok(
            grok_api_key=grok_api_key,
            serpapi_key=serpapi_key,
            silence_timeout=2.0,
            max_response_words=20,
            explain_keyword='explain',
            elevenlabs_api_key=elevenlabs_api_key,
            elevenlabs_voice_id="21m00Tcm4TlvDq8ikWAM",
            use_elevenlabs=elevenlabs_api_key is not None and 'your-elevenlabs' not in elevenlabs_api_key.lower()
        )
        
        return hue, "✅ Hue initialized successfully"
    except Exception as e:
        return None, f"❌ Error initializing Hue: {str(e)}"

# Theme colors
theme = st.session_state.get('theme', 'dark')
is_dark = theme == 'dark'

if is_dark:
    bg_color = "hsl(0, 0%, 0%)"
    ring_gradient = "linear-gradient(135deg, #51C4D3 0%, #77ACF1 14%, #EF88AD 28%, #A53860 42%, #670D2F 56%, #E8988A 70%, #FFEAD8 84%, #BA487F 98%, #E1ACAC 100%)"
    ring_center_bg = "hsl(0, 0%, 0%)"
    input_bg = "rgba(0, 0, 0, 0.98)"
    text_color = "#ffffff"
    input_border = "rgba(81, 196, 211, 0.3)"
else:
    bg_color = "hsl(0, 0%, 100%)"
    ring_gradient = "linear-gradient(135deg, #1e3a8a 0%, #3b82f6 14%, #60a5fa 28%, #93c5fd 42%, #dbeafe 56%, #1d4ed8 70%, #2563eb 84%, #1e40af 100%)"
    ring_center_bg = "hsl(0, 0%, 100%)"
    input_bg = "rgba(255, 255, 255, 0.98)"
    text_color = "#000000"
    input_border = "rgba(30, 58, 138, 0.3)"

# CSS - CLEAN LAYOUT FROM SCRATCH
st.markdown(f"""
<style>
    * {{
        box-sizing: border-box;
    }}
    
    html, body {{
        margin: 0;
        padding: 0;
        height: 100vh;
        overflow: hidden;
    }}
    
    .stApp {{
        background: {bg_color} !important;
        padding: 0 !important;
        margin: 0 !important;
    }}
    
    .main .block-container {{
        padding: 0 !important;
        padding-top: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }}
    
    .stAppViewContainer {{
        padding-top: 0 !important;
        margin-top: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}
    
    #MainMenu, header, footer {{
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        display: none !important;
    }}
    
    /* Remove all default Streamlit spacing - AGGRESSIVE */
    section[data-testid="stSidebar"], section[data-testid="stMain"] {{
        padding-top: 0 !important;
        margin-top: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}
    
    div[data-testid="stVerticalBlock"] {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    
    /* Force main content to start at top */
    .main {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    
    /* Override any Streamlit container padding */
    .block-container, [data-testid="stAppViewContainer"] > div {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    
    /* Main wrapper - simple flex layout */
    /* Main wrapper - visible flex layout */
    .main-wrapper {{
        display: flex !important;
        flex-direction: column !important;
        min-height: 100vh !important;
        width: 100% !important;
        background: {bg_color} !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative !important;
        z-index: 1 !important;
        visibility: visible !important;
    }}
    
    /* TOP HALF - Hue ring - AT TOP */
    .top-half {{
        min-height: 50vh !important;
        height: 50vh !important;
        width: 100% !important;
        display: flex !important;
        align-items: flex-start !important;
        justify-content: center !important;
        background: {bg_color} !important;
        padding-top: 2rem !important;
        margin: 0 !important;
        visibility: visible !important;
        opacity: 1 !important;
    }}
    
    .hue-ring-wrapper {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        visibility: visible !important;
        opacity: 1 !important;
    }}
    
    .hue-ring {{
        width: 200px !important;
        height: 200px !important;
        border-radius: 50% !important;
        background: {ring_gradient} !important;
        background-size: 300% 300% !important;
        animation: gradientShift 6s ease infinite, ringPulse 3s ease-in-out infinite !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 15px 50px rgba(81, 196, 211, 0.5) !important;
        position: relative !important;
        margin: 1rem 0 0 0 !important;
    }}
    
    .hue-ring::before {{
        content: '';
        position: absolute;
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: {ring_center_bg};
        z-index: 1;
    }}
    
    .hue-core {{
        position: relative;
        z-index: 2;
        color: {text_color if not is_dark else '#ffffff'};
        font-size: 2.2rem;
        font-weight: bold;
        text-shadow: 0 2px 15px rgba(0,0,0,0.4);
    }}
    
    .hue-status {{
        margin-top: 0.75rem !important;
        font-size: 0.95rem;
        font-weight: 500;
        color: {text_color};
        text-align: center;
        padding: 0 !important;
    }}
    
    .hue-ring.active {{
        animation: gradientShift 4s ease infinite, ringPulse 1.5s ease-in-out infinite;
    }}
    
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; filter: hue-rotate(0deg); }}
        25% {{ background-position: 100% 50%; filter: hue-rotate(10deg); }}
        50% {{ background-position: 100% 100%; filter: hue-rotate(20deg); }}
        75% {{ background-position: 0% 100%; filter: hue-rotate(10deg); }}
        100% {{ background-position: 0% 50%; filter: hue-rotate(0deg); }}
    }}
    
    @keyframes ringPulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.02); }}
    }}
    
    /* BOTTOM HALF - Input */
    .bottom-half {{
        min-height: 50vh !important;
        height: 50vh !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: {input_bg} !important;
        border-top: 2px solid {input_border} !important;
        box-shadow: 0 -5px 20px rgba(0,0,0,0.3) !important;
        padding: 2rem !important;
        margin: 0 !important;
    }}
    
    .input-wrapper {{
        width: 100%;
        max-width: 800px;
    }}
    
    .input-wrapper .stTextInput > div > div > input {{
        background: {input_bg};
        color: {text_color};
        border-color: {input_border};
    }}
    
    /* Hide Streamlit spacing */
    .element-container {{
        margin-bottom: 0 !important;
        padding: 0 !important;
    }}
    
    .stForm {{
        margin: 0 !important;
        padding: 0 !important;
    }}
</style>
""", unsafe_allow_html=True)

# Sidebar - CONVERSATION HISTORY
with st.sidebar:
    st.header("💬 Conversation History")
    
    if st.session_state.chat_history:
        for idx, msg in enumerate(st.session_state.chat_history):
            if msg["type"] == "user":
                st.markdown(f'**You:** {msg["content"]}')
            else:
                st.markdown(f'**Hue:** {msg["content"]}')
            if idx < len(st.session_state.chat_history) - 1:
                st.markdown("---")
    else:
        st.info("No messages yet. Start chatting!")
    
    st.divider()
    
    if st.button("🔄 Initialize Hue", type="primary", use_container_width=True):
        with st.spinner("Initializing..."):
            hue, message = initialize_hue()
            if hue:
                st.session_state.hue = hue
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    st.selectbox("Theme", ["Dark", "Light"], index=0 if st.session_state.theme == 'dark' else 1, key="theme_select", on_change=lambda: setattr(st.session_state, 'theme', 'dark' if st.session_state.theme_select == 'Dark' else 'light') or st.rerun())
    
    with st.expander("API Status"):
        grok_key = os.getenv('GROK_API_KEY', '')
        serp_key = os.getenv('SERPAPI_KEY', '')
        eleven_key = os.getenv('ELEVENLABS_API_KEY', '')
        st.write(f"{'🟢' if grok_key and 'your-grok' not in grok_key.lower() else '🔴'} Grok")
        st.write(f"{'🟢' if serp_key and 'your-serpapi' not in serp_key.lower() else '🔴'} SerpAPI")
        st.write(f"{'🟢' if eleven_key and 'your-elevenlabs' not in eleven_key.lower() else '🔴'} ElevenLabs")

# MAIN PAGE - CLEAN SPLIT SCREEN
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

# TOP HALF - HUE RING
st.markdown('<div class="top-half">', unsafe_allow_html=True)

ring_class = "hue-ring"
if st.session_state.is_listening:
    ring_class += " active"
    status_text = "🎤 Listening..."
elif st.session_state.is_speaking:
    ring_class += " active"
    status_text = "🔊 Speaking..."
elif st.session_state.hue:
    status_text = "✨ Ready"
else:
    status_text = "⚡ Initialize Hue in sidebar →"

st.markdown(f'''
<div class="hue-ring-wrapper">
    <div class="{ring_class}"><div class="hue-core">HUE</div></div>
    <div class="hue-status">{status_text}</div>
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close top-half

# BOTTOM HALF - INPUT
st.markdown('<div class="bottom-half">', unsafe_allow_html=True)
st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    input_col1, input_col2, input_col3 = st.columns([7, 1, 1])
    
    with input_col1:
        user_input = st.text_input(
            "Type your message...",
            key="message_input",
            label_visibility="collapsed",
            placeholder="Type your message to Hue... (Enter to send)"
        )
    
    with input_col2:
        submitted = st.form_submit_button("📤", use_container_width=True, disabled=not st.session_state.hue)
    
    with input_col3:
        voice_button_text = "🎤" if not st.session_state.voice_active else "⏹️"
        voice_clicked = st.form_submit_button(voice_button_text, use_container_width=True, disabled=not st.session_state.hue)

st.markdown('</div>', unsafe_allow_html=True)  # Close input-wrapper
st.markdown('</div>', unsafe_allow_html=True)  # Close bottom-half
st.markdown('</div>', unsafe_allow_html=True)  # Close main-wrapper

# Handle form submission
if submitted and user_input and st.session_state.hue and user_input.strip():
    with st.spinner("Hue is thinking..."):
        response = st.session_state.hue.process_input(user_input.strip())
        st.session_state.chat_history.append({
            "type": "user",
            "content": user_input.strip(),
            "timestamp": time.time()
        })
        st.session_state.chat_history.append({
            "type": "hue",
            "content": response,
            "timestamp": time.time()
        })
        st.rerun()

# Handle voice button
if voice_clicked and st.session_state.hue:
    if st.session_state.voice_active:
        if hasattr(st.session_state.hue, 'stop_listening'):
            st.session_state.hue.stop_listening()
        st.session_state.voice_active = False
        st.session_state.is_listening = False
    else:
        st.session_state.voice_active = True
        st.session_state.is_listening = True
    st.rerun()
