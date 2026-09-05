"""Lab 1 — Your very first agent (provided & complete).

This agent already works. Your Lab 1 job is to READ it, understand the four
pieces every agent has — a role + a goal + a backstory + a tool — then make it
your own by changing its personality. Reading and improving working code is a
core skill, especially now that AI writes so much of it.

Run it in the terminal:  python hello_agent.py
Test it in a web UI:     streamlit run test_apps/lab1_meet_your_agent.py
"""
import os

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

from src.tools import DuckDuckGoSearchTool

load_dotenv()

# 👇 Change this question to anything you're curious about.
QUESTION = "What are the 3 biggest AI agent trends in 2026? Cite your sources."


# --- The agent: who it is + what it's for ---
# 🔨 TODO (Lab 1): make this agent your own — rewrite its role / goal / backstory
#                  below, then re-run to hear its "voice" change.
researcher = Agent(
    role="Research Assistant",
    goal=(
        "Answer the user's question accurately using up-to-date web sources, "
        "and cite every claim with a URL."
    ),
    backstory=(
        "You are a meticulous research assistant who never makes things up. "
        "When you are unsure, you search the web before answering."
    ),
    tools=[DuckDuckGoSearchTool(max_results=5)],
    llm=LLM(model="gemini/gemini-3.6-flash", temperature=0.3),
    verbose=True,  # so you can WATCH it think and decide to search
)

# --- The task: what to do right now ---
task = Task(
    description=QUESTION,
    expected_output="A clear, well-structured answer with a short list of source URLs at the end.",
    agent=researcher,
)


if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit(
            "❌ Add your GEMINI_API_KEY to a .env file first (copy .env.example to .env)."
        )
    crew = Crew(agents=[researcher], tasks=[task], verbose=True)
    result = crew.kickoff()
    print("\n\n===== ANSWER =====\n")
    print(result)
