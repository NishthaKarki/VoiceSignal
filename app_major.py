# app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if "onboard_step" not in st.session_state:
    st.session_state.onboard_step = 1

# --- Dummy Data ---
def get_dummy_sentiment():
    teams = ["HR", "Engineering", "Sales", "Marketing"]
    data = np.random.uniform(-1, 1, (len(teams), 7))
    df = pd.DataFrame(data, index=teams, columns=pd.date_range("2025-04-15", periods=7))
    return df

def get_dummy_topics():
    dates = pd.date_range("2025-04-01", periods=14)
    topics = {
        "Work-Life": np.random.rand(14).cumsum(),
        "Tools": np.random.rand(14).cumsum(),
        "Culture": np.random.rand(14).cumsum(),
    }
    df = pd.DataFrame(topics, index=dates)
    return df

def get_dummy_alerts():
    return [
        {"level": "Critical", "text": "Engagement drop > 20% in Sales", "timestamp": "2025-04-20 10:15"},
        {"level": "Warning",  "text": "Spike in negative mentions in #general", "timestamp": "2025-04-19 16:42"},
    ]

def get_dummy_snippets():
    return [
        {"snippet": "[Engineer] I feel overwhelmed by tool changes..."},
        {"snippet": "[Sales] We need better onboarding..."},
        {"snippet": "[HR] Can we get more frequent check‑ins?"},
    ]

def get_dummy_recs():
    return [
        {"action": "Schedule 1:1 with Engineering Lead", "confidence": 0.87},
        {"action": "Deploy pulse survey to Sales",       "confidence": 0.79},
    ]

# --- Navigation Helpers ---
def go_to(page):
    st.session_state.page = page

# --- Pages ---
def login_page():
    st.title("🔐 VoiceSignal Login")
    email = st.text_input("Email")
    pwd   = st.text_input("Password", type="password")
    if st.button("Sign In"):
        # Dummy auth
        if email and pwd and len(pwd) >= 8:
            st.session_state.logged_in = True
            go_to("welcome")
        else:
            st.error("Please enter valid credentials (pwd ≥ 8 chars).")


def welcome_page():
    st.title(f"👋 Welcome, User!")
    st.write("Choose how you’d like to proceed:")
    col1, col2, col3 = st.columns(3)
    if col1.button("🚀 Onboarding Wizard"):
        go_to("onboarding")
    if col2.button("📊 Dashboard"):
        go_to("dashboard")
    if col3.button("❌ Exit"):
        st.warning("You have exited. Please close the window.")

# --- Updated Onboarding Wizard (remove “Exit” on Alerts page; Save → Welcome) ---
def onboarding_page():
    st.title("🛠️ Onboarding Wizard")
    step = st.session_state.onboard_step

    if step == 1:
        st.header("1. Privacy & Retention")
        st.checkbox("Enable Anonymization", value=True)
        st.slider("Data Retention (days)", min_value=30, max_value=365, value=90)
    elif step == 2:
        st.header("2. Platform Integration")
        st.multiselect("Connect with:", ["Slack", "MS Teams", "Email"], default=["Slack"])
    elif step == 3:
        st.header("3. Alerts & Roles")
        st.subheader("Thresholds")
        st.slider("Sentiment drop %", 1, 50, 20)
        st.slider("Message spike %", 1, 100, 30)
        st.subheader("Notifications")
        st.multiselect("Notify roles:", ["HR Lead", "Team Manager"], default=["HR Lead"])

    # Navigation buttons
    cols = st.columns(3)
    if cols[0].button("Back") and step > 1:
        st.session_state.onboard_step -= 1

    # Save now returns to Welcome, not Dashboard
    if step == 3 and cols[1].button("Save"):
        go_to("welcome")
        return

    if cols[2].button("Next") and step < 3:
        st.session_state.onboard_step += 1


def dashboard_page():
    st.title("📈 VoiceSignal AI Dashboard")

    if st.button("❌ Exit to Welcome"):
        go_to("welcome")
        return  # short‑circuit to avoid drawing the rest

    # ─── Sentiment Heatmap ──────────────────────────────────────────
    st.subheader("Sentiment Overview by Department")
    sent = get_dummy_sentiment()
    fig1 = px.imshow(
        sent,
        labels=dict(x="Date", y="Team", color="Sentiment"),
        x=sent.columns.strftime("%b %d"),
        y=sent.index,
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ─── Topic Trends ───────────────────────────────────────────────
    st.subheader("Topic Trends Over Time")
    topics = get_dummy_topics()
    fig2 = px.line(
        topics,
        x=topics.index,
        y=topics.columns,
        labels={"value": "Mentions", "index": "Date"},
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ─── Alerts Panel ───────────────────────────────────────────────
    st.subheader("Alerts")
    alerts = get_dummy_alerts()
    for a in alerts:
        if a["level"] == "Critical":
            st.error(f"**{a['level']}**: {a['text']}\n_{a['timestamp']}_")
        else:
            st.warning(f"**{a['level']}**: {a['text']}\n_{a['timestamp']}_")

    # ─── Deep Dive Navigation ───────────────────────────────────────
    if st.button("🔍 Deep Dive Report"):
        go_to("deep_dive")


def deep_dive_page():
    st.title("🔎 Deep Dive Report")

    # Filters
    teams = ["All", "Engineering", "Sales", "HR"]
    topics = ["All", "Work‑Life", "Tools", "Culture"]
    cols = st.columns(4)
    sel_team  = cols[0].selectbox("Team", teams)
    sel_topic = cols[1].selectbox("Topic", topics)
    date_range = cols[2].date_input("Date Range", 
                                    [pd.to_datetime("2025-04-15"), pd.to_datetime("2025-04-21")])
    if cols[3].button("Reset Filters"):
        sel_team, sel_topic = "All", "All"

    st.markdown("---")

    # Snippets
    st.subheader("Anonymized Snippets")
    snippets = get_dummy_snippets()
    for s in snippets:
        st.write(f"- {s['snippet']}")

    # Action Recommendations
    st.subheader("Action Recommendations")
    recs = get_dummy_recs()
    for r in recs:
        st.write(f"- {r['action']}  _(Confidence: {r['confidence']*100:.0f}% )_")

    # Export / Share
    cols = st.columns(2)
    if cols[0].button("📥 Export CSV"):
        df = pd.DataFrame(snippets)
        df.to_csv("deep_dive_report.csv", index=False)
        st.success("Exported deep_dive_report.csv")
    if cols[1].button("🔗 Share Link"):
        st.info("Shareable link generated: https://voice.signal/report/XYZ123")

    if st.button("⬅️ Back to Dashboard"):
        go_to("dashboard")

# --- Main App Logic ---
st.set_page_config(page_title="VoiceSignal", layout="wide")
if not st.session_state.logged_in or st.session_state.page == "login":
    login_page()
elif st.session_state.page == "welcome":
    welcome_page()
elif st.session_state.page == "onboarding":
    onboarding_page()
elif st.session_state.page == "dashboard":
    dashboard_page()
elif st.session_state.page == "deep_dive":
    deep_dive_page()
