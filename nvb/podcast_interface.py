import streamlit as st
import httpx
import asyncio
import sys

S1 = S2 = S3 = ""
if len(sys.argv) == 4:
    S1, S2, S3 = sys.argv[1], sys.argv[2], sys.argv[3]

BASE_URL = "http://127.0.0.1:8000"

async def send_command(cmd):
    async with httpx.AsyncClient(timeout=2) as client:
        await client.get(f"{BASE_URL}/action/{cmd}")

def run_command(cmd):
    asyncio.run(send_command(cmd))


st.set_page_config(page_title="Elmo Control", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for beautiful styling
st.markdown("""
    <style>
        * {
            margin: 0;
            padding: 0;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
        }
        
        .stTitle {
            text-align: center;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            color: black !important;
            text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            margin-bottom: 40px !important;
            letter-spacing: 2px;
        }
        
        .section-title {
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            color: black !important;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            margin-top: 20px !important;
            margin-bottom: 15px !important;
            padding-left: 10px;
            border-left: 5px solid rgba(255, 255, 255, 0.8);
        }
        
        .container-row {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .left-panel {
            flex: 1;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        }
        
        .right-panel {
            flex: 2;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        }
        
        .panel-title {
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            color: #333 !important;
            margin-bottom: 20px !important;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        button {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
            border: none !important;
            border-radius: 10px !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 12px 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 8px 25px rgba(245, 87, 108, 0.4) !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        button:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 12px 35px rgba(245, 87, 108, 0.6) !important;
        }
        
        button:active {
            transform: translateY(-2px) !important;
        }
        
        .button-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 15px;
        }
        
        .button-grid-3x4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }
        
        .divider {
            height: 1px;
            background: linear-gradient(90deg, rgba(102, 126, 234, 0.2) 0%, rgba(102, 126, 234, 0.5) 50%, rgba(102, 126, 234, 0.2) 100%);
            margin: 25px 0;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='stTitle'>🎙️ Elmo Control Panel</h1>", unsafe_allow_html=True)

# Main container with two columns
col_left, col_right = st.columns([1, 2], gap="large")

# LEFT PANEL - Robot State & Gaze Direction
with col_left:
    #st.markdown("<div class='left-panel'>", unsafe_allow_html=True)
    
    # Robot State Section
    st.markdown("<p class='panel-title'>Robot State (Icon)</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Backchanneling", use_container_width=True, key="btn_state1"):
            run_command("backchanneling")
    with col2:
        if st.button("Speaking", use_container_width=True, key="btn_state2"):
            run_command("speaking")
    with col3:
        if st.button("Listening", use_container_width=True, key="btn_state3"):
            run_command("listening")
    
    
    # Gaze Direction Section
    st.markdown("<p class='panel-title'>Gaze Direction</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        try:
            st.image("images/elmo_icon.png", use_container_width=True)
        except:
            st.markdown("<div style='text-align: center; font-size: 2rem;'>🎤</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button(S3, use_container_width=True, key="btn_gaze_left"):
            run_command("s3")
    
    with col3:
        if st.button(S1, use_container_width=True, key="btn_gaze_right"):
            run_command("s1")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(S2, use_container_width=True, key="btn_gaze_down"):
            run_command("s2")
    
    st.markdown("</div>", unsafe_allow_html=True)


# RIGHT PANEL - Eyes Emotions
with col_right:
    #st.markdown("<div class='right-panel'>", unsafe_allow_html=True)
    
    st.markdown("<p class='panel-title'>Eyes Emotions</p>", unsafe_allow_html=True)
    
    # Emotions Grid 4x2
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.image("images/blush.png", use_container_width=True)
        if st.button("Blush", use_container_width=True, key="btn_blush"):
            run_command("blush")
    with col2:
        st.image("images/cry.png", use_container_width=True)
        if st.button("Cry", use_container_width=True, key="btn_cry"):
            run_command("cry")
    with col3:
        st.image("images/effort.png", use_container_width=True)
        if st.button("Effort", use_container_width=True, key="btn_effort"):
            run_command("effort")
    with col4:
        st.image("images/love.png", use_container_width=True)
        if st.button("Love", use_container_width=True, key="btn_love"):
            run_command("love")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.image("images/sad.png", use_container_width=True)
        if st.button("Sad", use_container_width=True, key="btn_sad"):
            run_command("sad")
    with col2:
        st.image("images/star.png", use_container_width=True)
        if st.button("Star", use_container_width=True, key="btn_star"):
            run_command("star")
    with col3:
        st.image("images/thinking.png", use_container_width=True)
        if st.button("Thinking", use_container_width=True, key="btn_thinking"):
            run_command("thinking")
    with col4:
        st.image("images/normal.png", use_container_width=True)
        if st.button("Normal", use_container_width=True, key="btn_normal"):
            run_command("normal")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # IDLE Button - Full Width
    if st.button("IDLE", use_container_width=True, key="btn_idle"):
        run_command("idle")
    
    st.markdown("</div>", unsafe_allow_html=True)