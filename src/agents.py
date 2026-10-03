"""Agent definitions for the Startup Idea Validator crew.

🔨 YOU BUILD THIS FILE (with the instructor).

Three agents share the SAME LLM but produce very different output because their
role / goal / backstory differ. That difference IS the lesson of this workshop.

  • build_optimist   → ✅ DONE for you (your worked example — read it closely)
  • build_skeptic    → 🔨 TODO (Lab 2): mirror the Optimist, but make it pessimistic
  • build_strategist → 🔨 TODO (Lab 3): the synthesizer — note it has NO tools

Stuck? Ask in your breakout room — we'll work through it together at the regroup.
"""
from crewai import Agent, LLM
from crewai_tools import ScrapeWebsiteTool

from .tools import DuckDuckGoSearchTool
from . import todo_guard


def _make_llm(model: str, temperature: float) -> LLM:
    return LLM(model=model, temperature=temperature)


def build_optimist(model: str, temperature: float, max_search_results: int) -> Agent:
    """🚀  ✅ WORKED EXAMPLE (read this in Lab 1) — hunts for tailwinds and reasons this could win.

    This is your template: in Lab 2 you'll mirror it to build the Skeptic.
    """
    return Agent(
        role="Ex-VC Associate & Bull Case Builder",
        goal=(
            "Find the strongest possible evidence that this startup idea could become a "
            "real, venture-scale business. Surface market signals, customer demand, recent "
            "funding in adjacent spaces, and comparable winners. Cite every claim with a URL."
        ),
        backstory=(
            "You spent five years as an associate at a top-tier seed fund, where you saw "
            "unicorns that everyone laughed at in their first pitch. You believe most great "
            "businesses look like bad ideas at first. Your superpower is spotting tailwinds — "
            "demographic shifts, regulatory changes, new infrastructure — that make this the "
            "right time for an idea. You are optimistic but evidence-driven, never naive."
        ),
        tools=[DuckDuckGoSearchTool(max_results=max_search_results), ScrapeWebsiteTool()],
        llm=_make_llm(model, temperature),
        verbose=True,
        allow_delegation=False,
        max_iter=12,
    )


def build_skeptic(model: str, temperature: float, max_search_results: int) -> Agent:
    """🔪  🔨 TODO (Lab 2) — the mirror image of the Optimist: find why it FAILS.

    Fill in the role / goal / backstory below in your own words — make this agent
    hunt for why the idea won't work. Keep the tools and everything else like the
    Optimist (it also searches the web). The app stays paused until you replace
    every "TODO".  See README → Lab 2.
    """
    # 🔨 Lab 2: write your own role / goal / backstory. (Removing every "TODO" unlocks the app.)
    role = "TODO"
    goal = "TODO"
    backstory = "TODO"

    todo_guard(
        role, goal, backstory,
        message=(
            "🔪 Lab 2 isn't finished yet — open src/agents.py → build_skeptic and "
            "rewrite the TODO role / goal / backstory. See README → Lab 2."
        ),
    )

    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        tools=[DuckDuckGoSearchTool(max_results=max_search_results), ScrapeWebsiteTool()],
        llm=_make_llm(model, temperature),
        verbose=True,
        allow_delegation=False,
        max_iter=12,
    )


def build_strategist(model: str, temperature: float) -> Agent:
    """🎯  🔨 TODO (Lab 3) — reads BOTH cases and writes the final memo.

    Notice the difference: this agent has NO tools. It doesn't search — it
    THINKS, using what the other two agents already found. That is the
    "synthesis" role in a multi-agent system.

    Fill in its role / goal / backstory below in your own words. The app stays
    paused until you replace every "TODO".  See README → Lab 3.
    """
    # 🔨 Lab 3: write your own role / goal / backstory. (Removing every "TODO" unlocks the app.)
    role = "TODO"
    goal = "TODO"
    backstory = "TODO"

    todo_guard(
        role, goal, backstory,
        message=(
            "🎯 Lab 3 isn't finished yet — open src/agents.py → build_strategist and "
            "rewrite the TODO role / goal / backstory (keep tools=[]). See README → Lab 3."
        ),
    )

    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        tools=[],  # ← the synthesizer has NO tools. Leave this list empty.
        llm=_make_llm(model, temperature),
        verbose=True,
        allow_delegation=False,
    )
