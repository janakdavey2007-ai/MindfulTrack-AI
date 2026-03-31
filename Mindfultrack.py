{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\froman\fcharset0 Times-Roman;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;\red255\green255\blue255;\red255\green255\blue255;
}
{\*\expandedcolortbl;;\cssrgb\c0\c1\c1;\cssrgb\c100000\c100000\c99985;\cssrgb\c100000\c100000\c99956;
}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs24 \cf2 \cb3 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec4 import streamlit as st\
import pandas as pd\
import sqlite3\
import plotly.express as px\
from datetime import datetime, timedelta\
import numpy as np\
\
# ---------------- CONFIG ---------------- #\
st.set_page_config(page_title="MindfulTrack \uc0\u55356 \u57119 ", layout="wide")\
\
# ---------------- DATABASE ---------------- #\
@st.cache_resource\
def init_db():\
    conn = sqlite3.connect("mindfultrack.db", check_same_thread=False)\
    c = conn.cursor()\
\
    c.execute('''\
        CREATE TABLE IF NOT EXISTS users (\
            username TEXT PRIMARY KEY\
        )\
    ''')\
\
    c.execute('''\
        CREATE TABLE IF NOT EXISTS mood_entries (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            username TEXT,\
            mood TEXT,\
            note TEXT,\
            date TEXT\
        )\
    ''')\
\
    c.execute('''\
        CREATE TABLE IF NOT EXISTS journal_entries (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            username TEXT,\
            content TEXT,\
            date TEXT\
        )\
    ''')\
\
    conn.commit()\
    return conn\
\
conn = init_db()\
\
MOODS = \{\
    "\uc0\u55357 \u56842 ": "Happy",\
    "\uc0\u55357 \u56866 ": "Sad",\
    "\uc0\u55357 \u56865 ": "Angry",\
    "\uc0\u55357 \u56844 ": "Calm",\
    "\uc0\u55357 \u56880 ": "Anxious",\
    "\uc0\u55357 \u56884 ": "Tired"\
\}\
\
# ---------------- LOGIN ---------------- #\
if "user" not in st.session_state:\
    st.session_state.user = None\
\
def login():\
    st.title("\uc0\u55357 \u56592  Login to MindfulTrack")\
\
    username = st.text_input("Enter Username")\
\
    if st.button("Login"):\
        if username.strip() == "":\
            st.error("Enter valid username")\
        else:\
            st.session_state.user = username\
            st.success("Logged in!")\
            st.rerun()\
\
# ---------------- AI SUGGESTIONS ---------------- #\
def ai_suggestions(moods):\
    if not moods:\
        return ["Start tracking your mood daily \uc0\u55357 \u56842 "]\
\
    mood_list = [m[0] for m in moods]\
\
    suggestions = []\
\
    if mood_list.count("\uc0\u55357 \u56880 ") > 2:\
        suggestions.append("You seem stressed. Try breathing exercises \uc0\u55356 \u57132 \u65039 ")\
\
    if mood_list.count("\uc0\u55357 \u56866 ") > 2:\
        suggestions.append("Take a break and talk to someone you trust \uc0\u55357 \u56492 ")\
\
    if mood_list.count("\uc0\u55357 \u56842 ") > 3:\
        suggestions.append("Great job! Keep maintaining your happiness \uc0\u55356 \u57119 ")\
\
    if not suggestions:\
        suggestions.append("Maintain a balanced routine \uc0\u55358 \u56792 ")\
\
    return suggestions\
\
# ---------------- MAIN APP ---------------- #\
def app():\
    st.title(f"\uc0\u55356 \u57096  MindfulTrack - Welcome \{st.session_state.user\}")\
\
    if st.button("Logout"):\
        st.session_state.user = None\
        st.rerun()\
\
    tab1, tab2, tab3, tab4 = st.tabs(\
        ["\uc0\u55357 \u56522  Dashboard", "\u55357 \u56842  Mood Tracker", "\u55357 \u56541  Journal", "\u55357 \u56520  Analytics"]\
    )\
\
    # -------- DASHBOARD -------- #\
    with tab1:\
        st.subheader("Quick Mood Check")\
\
        mood = st.selectbox("How are you feeling?", list(MOODS.keys()))\
\
        if st.button("Log Mood"):\
            c = conn.cursor()\
            c.execute("""\
                INSERT INTO mood_entries (username, mood, date)\
                VALUES (?, ?, ?)\
            """, (st.session_state.user, mood,\
                  datetime.now().strftime('%Y-%m-%d')))\
            conn.commit()\
            st.success("Mood Logged!")\
\
        # Stats\
        c = conn.cursor()\
        c.execute("""\
            SELECT COUNT(*) FROM mood_entries\
            WHERE username=?\
        """, (st.session_state.user,))\
        total = c.fetchone()[0]\
\
        st.metric("Total Entries", total)\
\
        # AI suggestions\
        c.execute("""\
            SELECT mood FROM mood_entries\
            WHERE username=?\
            ORDER BY id DESC LIMIT 10\
        """, (st.session_state.user,))\
        moods = c.fetchall()\
\
        st.subheader("\uc0\u55358 \u56598  AI Suggestions")\
        for tip in ai_suggestions(moods):\
            st.info(tip)\
\
    # -------- MOOD TRACKER -------- #\
    with tab2:\
        st.subheader("Track Mood")\
\
        mood = st.selectbox("Select Mood", list(MOODS.keys()), key="mood_tab")\
\
        note = st.text_area("Add Note")\
\
        if st.button("Save Entry"):\
            if note.strip() == "":\
                st.warning("Note is empty (optional)")\
            c = conn.cursor()\
            c.execute("""\
                INSERT INTO mood_entries (username, mood, note, date)\
                VALUES (?, ?, ?, ?)\
            """, (st.session_state.user, mood, note,\
                  datetime.now().strftime('%Y-%m-%d')))\
            conn.commit()\
            st.success("Saved!")\
\
    # -------- JOURNAL -------- #\
    with tab3:\
        st.subheader("Journal")\
\
        entry = st.text_area("Write here...")\
\
        if st.button("Save Journal"):\
            if entry.strip() == "":\
                st.error("Cannot be empty")\
            else:\
                c = conn.cursor()\
                c.execute("""\
                    INSERT INTO journal_entries (username, content, date)\
                    VALUES (?, ?, ?)\
                """, (st.session_state.user, entry,\
                      datetime.now().strftime('%Y-%m-%d')))\
                conn.commit()\
                st.success("Saved!")\
\
        c.execute("""\
            SELECT content, date FROM journal_entries\
            WHERE username=?\
            ORDER BY id DESC LIMIT 5\
        """, (st.session_state.user,))\
        rows = c.fetchall()\
\
        for content, date in rows:\
            st.info(f"\{date\} - \{content\}")\
\
    # -------- ANALYTICS -------- #\
    with tab4:\
        st.subheader("Analytics")\
\
        c = conn.cursor()\
        c.execute("""\
            SELECT mood, COUNT(*) FROM mood_entries\
            WHERE username=?\
            GROUP BY mood\
        """, (st.session_state.user,))\
        data = c.fetchall()\
\
        if data:\
            df = pd.DataFrame(data, columns=["Mood", "Count"])\
            fig = px.bar(df, x="Mood", y="Count", title="Mood Frequency")\
            st.plotly_chart(fig)\
        else:\
            st.info("No data yet")\
\
# ---------------- RUN ---------------- #\
if st.session_state.user is None:\
    login()\
else:\
    app()}
