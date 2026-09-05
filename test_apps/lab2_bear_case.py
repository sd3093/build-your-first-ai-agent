"""Lab 2 checkpoint — see your Skeptic's bear case.

Runs just the Optimist + your new Skeptic (no Strategist yet) so you can read the
Bull case and Bear case side by side as soon as you finish Lab 2.

✅ PROVIDED — run this to check your filled-in Lab 2 work. You don't edit it.

   Run it (from the project root):  streamlit run test_apps/lab2_bear_case.py
"""
import os
import sys
from pathlib import Path

# This app lives in test_apps/, but it imports the root-level src/ package.
# Add the project root to the import path so `src` resolves.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from dotenv import load_dotenv
from crewai import Crew, Process

from src import LabTODO
from src.agents import build_optimist, build_skeptic
from src.tasks import build_bull_task, build_bear_task

load_dotenv()

st.set_page_config(page_title="Lab 2 — Bull vs Bear", page_icon="🔪")
st.title("Lab 2 — Bull vs Bear")
st.caption("Runs the Optimist + your Skeptic (no Strategist yet) so you can read both cases.")

DEFAULT_IDEA = "TutorVoice: retired teachers tutor kids over voice chat, paid by the minute."
idea = st.text_area("Startup idea", value=DEFAULT_IDEA)

if st.button("Run Optimist + Skeptic", type="primary"):
    if not os.getenv("GEMINI_API_KEY"):
        st.error("Add your GEMINI_API_KEY to a .env file first (see .env.example).")
    elif not idea.strip():
        st.warning("Type an idea first.")
    else:
        try:
            with st.spinner("Two agents are researching and debating… (about 1–2 minutes)"):
                optimist = build_optimist("gemini/gemini-3.6-flash", 0.6, 6)
                skeptic = build_skeptic("gemini/gemini-3.6-flash", 0.6, 6)
                bull = build_bull_task(optimist, idea.strip(), "", "", "")
                bear = build_bear_task(skeptic, idea.strip(), "", "", "")
                crew = Crew(
                    agents=[optimist, skeptic],
                    tasks=[bull, bear],
                    process=Process.sequential,
                    verbose=True,
                )
                result = crew.kickoff()
            outs = [str(t.raw) for t in result.tasks_output]
            tab_bull, tab_bear = st.tabs(["🚀 Bull Case", "🔪 Bear Case"])
            with tab_bull:
                st.markdown(outs[0] if len(outs) > 0 else "No bull case.")
            with tab_bear:
                st.markdown(outs[1] if len(outs) > 1 else "No bear case.")
        except LabTODO as e:
            # Lab 2 isn't finished yet — show the prompt instead of a crash.
            st.warning(str(e))
