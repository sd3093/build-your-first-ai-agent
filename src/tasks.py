"""Task definitions for the Startup Idea Validator crew.

🔨 YOU BUILD THIS FILE (with the instructor).

A Task = a `description` (what to do) + an `expected_output` (the shape of the
answer) + the `agent` that owns it.

  • build_bull_task → ✅ DONE for you (your worked example)
  • build_bear_task → 🔨 TODO (Lab 2): mirror the bull task, but argue the opposite
  • build_memo_task → ✅ PROVIDED (the memo's structure is long, so it's given)

Stuck? Ask in your breakout room — we'll work through it together at the regroup.
"""
from crewai import Task, Agent

from . import todo_guard


def _idea_block(idea: str, customer: str, advantage: str, budget: str) -> str:
    lines = [f"**Idea:** {idea}"]
    if customer.strip():
        lines.append(f"**Target customer:** {customer}")
    if advantage.strip():
        lines.append(f"**Founder's unfair advantage:** {advantage}")
    if budget.strip():
        lines.append(f"**Budget tier:** {budget}")
    return "\n".join(lines)


def build_bull_task(
    agent: Agent, idea: str, customer: str, advantage: str, budget: str
) -> Task:
    """✅ WORKED EXAMPLE (read this in Lab 1) — the strongest evidence-backed case FOR the idea.

    In Lab 2 you'll mirror this to write the Bear task.
    """
    return Task(
        description=(
            f"Build the strongest evidence-backed BULL CASE for this startup idea.\n\n"
            f"{_idea_block(idea, customer, advantage, budget)}\n\n"
            f"Use the search and scrape tools to research:\n"
            f"1. Market size signals (any data you can find — even rough proxies).\n"
            f"2. Recent funding rounds or acquisitions in adjacent spaces (last 18 months).\n"
            f"3. Evidence of unmet customer demand (forum complaints, Reddit threads, "
            f"product reviews, search trends).\n"
            f"4. Comparable winners — companies in adjacent niches that prove the business "
            f"model can work.\n"
            f"5. Tailwinds — tech, regulatory, demographic, or cultural shifts that make NOW "
            f"the right time.\n\n"
            f"Be optimistic but rigorous. Cite every claim with a URL. If you cannot find "
            f"evidence for something, say so — do not fabricate."
        ),
        expected_output=(
            "A structured Markdown brief titled `# 🚀 Bull Case` with these sections:\n"
            "- **Top Reasons to Pursue** (3-5 bullets, each ending with a source link)\n"
            "- **Market Signals** (bulleted evidence with URLs)\n"
            "- **Tailwinds** (why now)\n"
            "- **Comparable Winners** (companies that prove the model)\n"
            "- **Customer Demand Evidence** (quotes/links from forums, reviews, search trends)\n"
            "- **Sources** (numbered list of all URLs)"
        ),
        agent=agent,
    )


def build_bear_task(
    agent: Agent, idea: str, customer: str, advantage: str, budget: str
) -> Task:
    """🔪 🔨 TODO (Lab 2) — the mirror of the bull task: the strongest case AGAINST.

    Fill in the `description` (what to research to argue the idea will fail) and the
    `expected_output` (the shape of the bear-case brief). The bull task above is your
    template — mirror its shape, including how it passes the idea details to the agent.
    The app stays paused until you replace every "TODO".  See README → Lab 2.
    """
    # 🔨 Lab 2: write your own description + expected_output. (Removing every "TODO" unlocks the app.)
    description = (
        f"Build the strongest evidence-backed BEAR CASE for this startup idea.\n\n"
        f"{_idea_block(idea, customer, advantage, budget)}\n\n"
        f"Use the search and scrape tools to research:\n"
        f"1. Evidence that the reachable market is smaller, slower-growing, or harder to "
        f"access than claimed. Challenge top-down market estimates with bottom-up proxies.\n"
        f"2. Evidence of weak or unmet customer demand, low willingness to pay, poor "
        f"retention, or strong existing alternatives from forums, reviews, and search trends.\n"
        f"3. Competitive and differentiation risks, including incumbent advantages, crowded "
        f"categories, low switching costs, and easily copied features.\n"
        f"4. Business-model and unit-economics risks. Quantify pricing, CAC, churn, gross "
        f"margin, payback period, capital requirements, and runway where evidence permits.\n"
        f"5. Comparable failures from adjacent markets, including shutdowns, down rounds, "
        f"failed acquisitions, pivots, and investor pullback during the last 18 months.\n"
        f"6. Technical, regulatory, demographic, cultural, distribution, and execution "
        f"headwinds that could make now the wrong time or prevent the idea from scaling.\n"
        f"7. Evidence that contradicts the bear case, so credible strengths are not ignored.\n\n"
        f"Prioritize recent primary sources, then reputable secondary sources. For each "
        f"material claim, provide a URL and publication date and label the evidence "
        f"`Verified`, `Inferred`, or `Unknown`. Rank each major risk by likelihood and "
        f"impact on a 1-5 scale. If evidence is weak, conflicting, or unavailable, state "
        f"what is unknown, why it matters, and the cheapest test that could resolve it. "
        f"Do not fabricate evidence or present estimates as facts."
    )
    expected_output = (
        "A structured Markdown brief titled `# 🔪 Bear Case` with these sections:\n"
        "- **Executive Verdict** (3-5 sentences summarizing the case against the idea)\n"
        "- **Critical Assumptions** (table: assumption, evidence, evidence status, consequence)\n"
        "- **Top Failure Risks** (5-7 risks ranked by likelihood and impact from 1-5, "
        "with evidence and source links)\n"
        "- **Demand and Market Weakness** (reachable-market and willingness-to-pay evidence)\n"
        "- **Competition and Differentiation Risks** (incumbents, alternatives, switching "
        "costs, and defensibility)\n"
        "- **Unit Economics and Funding Risks** (available CAC, churn, margin, payback, "
        "capital, and runway evidence; mark unavailable metrics `Unknown`)\n"
        "- **Comparable Failures** (shutdowns, down rounds, failed acquisitions, or pivots)\n"
        "- **Headwinds** (technical, regulatory, demographic, cultural, distribution, "
        "and execution barriers)\n"
        "- **Evidence Against the Bear Case** (credible strengths or contradictory findings)\n"
        "- **Unknowns and Validation Tests** (missing evidence, why it matters, and the "
        "cheapest test for each unknown)\n"
        "- **Sources** (numbered URLs with source name and publication date)"
    )

    todo_guard(
        description, expected_output,
        message=(
            "🔪 Lab 2 isn't finished yet — open src/tasks.py → build_bear_task and write the "
            "description + expected_output (mirror build_bull_task). See README → Lab 2."
        ),
    )

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )


def build_memo_task(
    agent: Agent,
    idea: str,
    customer: str,
    advantage: str,
    budget: str,
    context_tasks: list[Task],
) -> Task:
    """✅ PROVIDED — synthesize the bull + bear cases into the final memo.

    Note the `context=context_tasks` at the bottom: that's how this task RECEIVES
    the outputs of the bull and bear tasks. You wire those up in crew.py (Hour 3).
    """
    return Task(
        description=(
            f"Read the bull case and bear case in your context. Weigh the evidence. "
            f"Write the final Validation Memo for this founder.\n\n"
            f"{_idea_block(idea, customer, advantage, budget)}\n\n"
            f"The memo must be DECISION-GRADE — short, opinionated, and actionable. "
            f"Do not hedge. Pick a verdict. The goal is to help the founder learn fast, "
            f"not feel good. Preserve the most important source links from the briefs.\n\n"
            f"Required structure (use this exact Markdown skeleton):\n\n"
            f"# 🎯 Validation Memo: <one-line idea summary>\n\n"
            f"## Verdict\n"
            f"🟢 **Pursue** / 🟡 **Pivot** / 🔴 **Pass** — one-sentence reason.\n\n"
            f"## The Riskiest Assumption\n"
            f"The single belief that, if wrong, kills this. One paragraph.\n\n"
            f"## Top 3 Reasons to Pursue\n"
            f"1. ... [source](url)\n"
            f"2. ...\n"
            f"3. ...\n\n"
            f"## Top 3 Reasons It'll Fail\n"
            f"1. ... [source](url)\n"
            f"2. ...\n"
            f"3. ...\n\n"
            f"## 90-Day MVP Scope\n"
            f"The smallest, cheapest experiment that tests the riskiest assumption. "
            f"Bullet what to build, what to skip, what success looks like.\n\n"
            f"## Kill Criteria\n"
            f"Specific, measurable signals that should make the founder stop. "
            f"e.g. '<5% of waitlist converts to paid in 30 days'.\n\n"
            f"## Key Sources\n"
            f"Numbered list of the 5-8 most important URLs from both briefs."
        ),
        expected_output=(
            "A complete Markdown memo following the exact skeleton above. "
            "Output the Markdown directly — no surrounding code fences, no preamble, "
            "no 'Here is the memo:' intro."
        ),
        agent=agent,
        context=context_tasks,
    )
