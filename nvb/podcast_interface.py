import streamlit as st
import httpx
import asyncio
import sys

S1 = S2 = S3 = ""
if len(sys.argv) == 4:
    S1, S2, S3 = sys.argv[1], sys.argv[2], sys.argv[3]

BASE_URL = "http://127.0.0.1:8000"

async def send_command(cmd, args):
    async with httpx.AsyncClient(timeout=2) as client:
        await client.get(f"{BASE_URL}/action/{cmd}/{args}")

def run_command(cmd, args=None):
    asyncio.run(send_command(cmd, args))


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
            padding: 0px 0px;
        }
        
        .stTitle {
            text-align: center;
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: black !important;
            text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            margin-bottom: 0px !important;
            letter-spacing: 2px;
            margin-top: 0px;
            padding-top:0px;
        }
        
        .section-title {
            font-size: 1rem !important;
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
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: #333 !important;
            margin-bottom: 20px !important;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        button {
            background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%) !important;
            border: none !important;
            border-radius: 10px !important;
            color: black !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 12px 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 8px 25px rgba(194, 233, 251, 0.6) !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        button:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 12px 35px rgba(102, 163, 255, 0.4) !important;
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

        [data-testid="stImage"] {
            display: flex;
            justify-content: center;
        }
        
        .pink-round-button button,
        .pink-round-button button[kind="primary"],
        .pink-round-button div[data-testid="stButton"] button {
            background: linear-gradient(135deg, #ff6b9d 0%, #ffc3d8 100%) !important;
            border-radius: 50% !important;
            width: 80px !important;
            height: 80px !important;
            min-width: 80px !important;
            min-height: 80px !important;
            max-width: 80px !important;
            max-height: 80px !important;
            padding: 0 !important;
            box-shadow: 0 8px 25px rgba(255, 107, 157, 0.6) !important;
            font-size: 0.75rem !important;
        }
        
        .pink-round-button button:hover,
        .pink-round-button button[kind="primary"]:hover,
        .pink-round-button div[data-testid="stButton"] button:hover {
            background: linear-gradient(135deg, #ff5a8f 0%, #ffb5cc 100%) !important;
            box-shadow: 0 12px 35px rgba(255, 107, 157, 0.8) !important;
        }
        
        .pink-round-button {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='stTitle'>🎙️ Elmo Control Panel</h1>", unsafe_allow_html=True)


tab1, tab2 = st.tabs(["Interaction Control", "Robot setup"])

with tab1:
    # Main container with two columns
    col_left, col_right = st.columns([1, 2], gap="large")

# LEFT PANEL - Robot State & Gaze Direction
with col_left:
    #st.markdown("<div class='left-panel'>", unsafe_allow_html=True)
    
    # Robot State Section
    st.markdown("<p class='panel-title'>Robot State (Icon)</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Backchannel", use_container_width=True, key="btn_state1"):
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
        
        st.image("images/elmo_icon.png", use_container_width=True)
        
    
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
    
    #st.markdown("</div>", unsafe_allow_html=True)


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
        st.image("images/wink.png", use_container_width=True)
        if st.button("Wink", use_container_width=True, key="btn_wink"):
            run_command("wink")
        
    col1, col2, col3, col4, col5, col6 = st.columns([1,2,1,1,2,1])
    with col2:
        st.image("images/normal.png", use_container_width=True) 
        if st.button("Normal", use_container_width=True, key="btn_normal"):
            run_command("normal")
    
    with col5:
        st.markdown("""
            <style>
            #idle-btn button {
                background: linear-gradient(135deg, #ff6b9d 0%, #ffc3d8 100%) !important;
                border-radius: 50% !important;
                width: 80px !important;
                height: 80px !important;
            }
            </style>
            <div id="idle-btn">
        """, unsafe_allow_html=True)
        if st.button("IDLE", key="btn_idle"):
            run_command("idle")
        st.markdown("</div>", unsafe_allow_html=True)


with tab2:
    st.markdown("<h2>Robot setup</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Toogle Motors", use_container_width=True, key="btn_toggle_motors"):
            run_command("toggle_motors")
    with col2:
        if st.button("Toggle Behaviours", use_container_width=True, key="btn_toggle_behaviours"):
            run_command("toggle_behaviours")

    st.markdown(f"<p class='panel-title'> {S1} </p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        num1s1 = st.number_input("Pan [-40,40]", value=35, step=1, key="num1_inputs1")
    with col2:
        num2s1 = st.number_input("Tilt [-15,15]", value=-7, step=1, key="num2_inputs1")
    with col3:
        st.markdown(f"<p></p>", unsafe_allow_html=True)
        if st.button("Submit Numbers", use_container_width=True, key="btn_submit_numberss1"):
            
            run_command("sets1", f"{num1s1},{num2s1}")
    
    #st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<p class='panel-title'> {S2} </p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        num1s2 = st.number_input("Pan [-40,40]", value=0, step=1, key="num1_inputs2")
    with col2:
        num2s2 = st.number_input("Tilt [-15,15]", value=-7, step=1, key="num2_inputs2")
    with col3:
        st.markdown(f"<p></p>", unsafe_allow_html=True)

        if st.button("Submit Numbers", use_container_width=True, key="btn_submit_numberss2"):
            
            run_command("sets2", f"{num1s2},{num2s2}")
    
    #st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<p class='panel-title'> {S3} </p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        num1s3 = st.number_input("Pan [-40,40]", value=-35, step=1, key="num1_inputs3")
    with col2:
        num2s3 = st.number_input("Tilt [-15,15]", value=-7, step=1, key="num2_inputs3")
    with col3:
        st.markdown(f"<p></p>", unsafe_allow_html=True)
        if st.button("Submit Numbers", use_container_width=True, key="btn_submit_numberss3"):
        
            run_command("sets3", f"{num1s3},{num2s3}")
    
    #st.markdown("</div>", unsafe_allow_html=True)