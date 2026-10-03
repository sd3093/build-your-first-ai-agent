"""Crew wiring for the Startup Idea Validator.

🔨 YOU BUILD THIS FILE (Lab 3).

This is the "fan-in" pattern — the big idea of the workshop:
  1. The Optimist runs and builds the bull case.
  2. The Skeptic runs and builds the bear case.
  3. The Strategist receives BOTH of their outputs as `context` and writes the memo.

There is ONE blank to fill (look for 🔨 TODO below).

Stuck? Ask in your breakout room — we'll work through it together at the regroup.
"""
from crewai import Crew, Process

from .agents import build_optimist, build_skeptic, build_strategist
from .tasks import build_bull_task, build_bear_task, build_memo_task
from . import fan_in_guard


def build_crew(
    idea: str,
    customer: str = "",
    advantage: str = "",
    budget: str = "",
    model: str = "gemini/gemini-2.5-flash",
    temperature: float = 0.6,
    max_search_results: int = 6,
    step_callback=None,
) -> Crew:
    """Construct the three-agent validation crew."""
    # 1) Optimist + Bull task — ✅ DONE for you (your worked example).
    optimist = build_optimist(model, temperature, max_search_results)
    bull_task = build_bull_task(optimist, idea, customer, advantage, budget)

    # 2) 🔨 Lab 2 — Skeptic + Bear task (you build these in src/agents.py & src/tasks.py).
    skeptic = build_skeptic(model, temperature, max_search_results)
    bear_task = build_bear_task(skeptic, idea, customer, advantage, budget)

    # 3) 🔨 Lab 3 — Strategist (you build it in src/agents.py; it runs cooler — less random).
    strategist = build_strategist(model, max(0.2, temperature - 0.3))

    # 4) 🔨 TODO (Lab 3) — THE FAN-IN.
    #    The memo task needs BOTH earlier tasks as its `context`, so the Strategist
    #    can read what the Optimist and Skeptic found.
    #    👉 Replace the empty list  []  with  [bull_task, bear_task]  on the next line.
    memo_context = []  # ← TODO (Lab 3): change [] to [bull_task, bear_task]
    fan_in_guard(
        memo_context,
        message=(
            "🎯 Lab 3 isn't finished yet — open src/crew.py and wire the fan-in: change "
            "memo_context from [] to [bull_task, bear_task]. See README → Lab 3."
        ),
    )
    memo_task = build_memo_task(
        strategist, idea, customer, advantage, budget, memo_context
    )

    # 5) Assemble the crew: three agents, three tasks, run one after another.
    return Crew(
        agents=[optimist, skeptic, strategist],
        tasks=[bull_task, bear_task, memo_task],
        process=Process.sequential,
        verbose=True,
        step_callback=step_callback,
    )
