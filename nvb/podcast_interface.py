import streamlit as st
import httpx
import asyncio

BASE_URL = "http://127.0.0.1:8000"

async def send_command(cmd):
    async with httpx.AsyncClient(timeout=2) as client:
        await client.get(f"{BASE_URL}/action/{cmd}")

def run_command(cmd):
    asyncio.run(send_command(cmd))

st.set_page_config(page_title="Elmo Control", layout="wide")

st.title("Elmo: The Podcast Star")

# Row 1
col1, col2, col3, col4, col5 = st.columns(5)
col1.write("Conversation")
col4.write("Eyes")

# Row 2
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("Backchanneling", use_container_width=True):
        run_command("backchanneling")
with col2:
    if st.button("Listening", use_container_width=True):
        run_command("listening")
with col3:
    if st.button("Speaking", use_container_width=True):
        run_command("speaking")
with col4:
    if st.button("Blush", use_container_width=True):
        run_command("blush")
with col5:
    if st.button("Cry", use_container_width=True):
        run_command("cry")

# Row 3
col1, col2, col3, col4, col5 = st.columns(5)
col1.write("Gaze at")
with col4:
    if st.button("Effort", use_container_width=True):
        run_command("effort")
with col5:
    if st.button("Love", use_container_width=True):
        run_command("love")


# Row 4
col1, col2, col3, col4, col5 = st.columns(5)
with col2:
    if st.button("S2", use_container_width=True):
        run_command("s2")
with col4:
    if st.button("Normal", use_container_width=True):
        run_command("normal")
with col5:
    if st.button("Sad", use_container_width=True):
        run_command("sad")

# Row 5
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("S3", use_container_width=True):
        run_command("s3")
with col3:
    if st.button("S1", use_container_width=True):
        run_command("s1")
with col4:
    if st.button("Star", use_container_width=True):
        run_command("star")
with col5:
    if st.button("Thinking", use_container_width=True):
        run_command("thinking")

# Row 6
col1, col2, col3, col4, col5 = st.columns(5)
#col2.image("", caption="Image")
with col5:
    if st.button("idle", use_container_width=True):
        run_command("idle")

