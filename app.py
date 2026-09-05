"""Streamlit UI for the CrewAI Startup Idea Validator.

✅ PROVIDED — this is the full, polished app (the "after" picture). You run it
   and deploy it; you do NOT need to type it. In Hour 4 we read
   `test_apps/lab4_minimal_app.py` together to see the smallest version, then run
   THIS one for the real thing.

   Run it:  streamlit run app.py
"""
from __future__ import annotations

import os
import re
import threading
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.crew import build_crew
from src import LabTODO
from src.pdf import markdown_to_pdf_bytes
from src.streaming import capture_stdout_stderr
from src.theme import agent_cards, hero, inject_css, verdict_pill

# ---------------------------------------------------------------------------
# Config & setup
# ---------------------------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="Startup Idea Validator",
    page_icon="🎯",
    layout="wide",
)

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:60] or "idea"


def strip_code_fences(md: str) -> str:
    md = md.strip()
    if md.startswith("```"):
        md = re.sub(r"^```[a-zA-Z]*\n", "", md)
        md = re.sub(r"\n```\s*$", "", md)
    return md


def detect_active_agent(log: str, roles: list[str] | None = None) -> tuple[str | None, set[str]]:
    """Parse the live log tail to figure out which agent is currently working.

    Returns (active_agent_name, set_of_done_agent_names).

    Uses the crew's ACTUAL agent roles when available (passed in as
    [optimist_role, skeptic_role, strategist_role]) so the animation works no
    matter what role text a student writes; falls back to the reference roles.
    """
    # CrewAI prints each agent's role in its verbose logs. We look for those strings.
    if roles and len(roles) >= 3:
        optimist_markers = [roles[0]]
        skeptic_markers = [roles[1]]
        strategist_markers = [roles[2]]
    else:
        optimist_markers = ["Ex-VC Associate", "Bull Case Builder"]
        skeptic_markers = ["Serial Founder", "Devil's Advocate"]
        strategist_markers = ["Founding Partner", "Memo Writer"]

    def last_index(markers: list[str]) -> int:
        idx = -1
        for m in markers:
            i = log.rfind(m)
            if i > idx:
                idx = i
        return idx

    o_idx = last_index(optimist_markers)
    s_idx = last_index(skeptic_markers)
    st_idx = last_index(strategist_markers)

    if max(o_idx, s_idx, st_idx) < 0:
        return None, set()

    # Whichever marker was seen most recently = currently working
    indices = [("optimist", o_idx), ("skeptic", s_idx), ("strategist", st_idx)]
    indices.sort(key=lambda x: x[1], reverse=True)
    active = indices[0][0] if indices[0][1] >= 0 else None

    # Everyone before the active one (in sequential order) is done
    order = ["optimist", "skeptic", "strategist"]
    done: set[str] = set()
    if active:
        for name in order:
            if name == active:
                break
            done.add(name)
    return active, done


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
def _init_state():
    defaults = {
        "history": [],          # list of validation runs
        "running": False,
        "current_idea": "",
        "bull_md": "",
        "bear_md": "",
        "memo_md": "",
        "memo_path": "",
        "log_text": "",
        "error_msg": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Settings")

    st.subheader("Model")
    model = st.selectbox(
        "LLM",
        options=[
            "gemini/gemini-3.6-flash",
        ],
        index=0,
        help="Gemini models via Google AI Studio. Flash is fast + free tier friendly.",
    )
    temperature = st.slider(
        "Temperature",
        0.0, 1.0, 0.6, 0.05,
        help="Higher = more divergent personas. The Strategist always runs cooler.",
    )

    st.subheader("Research")
    max_results = st.slider("Max search results per agent", 3, 10, 6)

    st.divider()
    st.subheader("🔑 API Keys")
    gemini_ok = bool(os.getenv("GEMINI_API_KEY"))
    st.write(f"Gemini: {'✅' if gemini_ok else '❌'}")
    st.caption("Web search uses DuckDuckGo — no key needed.")
    if not gemini_ok:
        st.caption("Add `GEMINI_API_KEY` to your `.env`, then restart Streamlit.")

    st.divider()
    st.subheader("🕘 History")
    if not st.session_state.history:
        st.caption("No validations yet.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            label = item["idea"][:42] + ("…" if len(item["idea"]) > 42 else "")
            if st.button(f"📄 {label}", key=f"hist-{i}", use_container_width=True):
                st.session_state.current_idea = item["idea"]
                st.session_state.bull_md = item["bull_md"]
                st.session_state.bear_md = item["bear_md"]
                st.session_state.memo_md = item["memo_md"]
                st.session_state.memo_path = item["memo_path"]
                st.rerun()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
inject_css()
hero(gemini_ok=gemini_ok)
# Agent cards: dynamically updated below during a run; this is the idle state.
agent_cards_slot = st.empty()
if not st.session_state.running:
    with agent_cards_slot.container():
        agent_cards(active=None, done=set())

# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------
with st.form("idea_form", clear_on_submit=False):
    idea = st.text_area(
        "Your startup idea",
        placeholder="e.g. A Duolingo-style app that teaches you to read sheet music in 5 minutes a day.",
        height=80,
        disabled=st.session_state.running,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        customer = st.text_input(
            "Target customer (optional)",
            placeholder="e.g. adult amateur musicians",
            disabled=st.session_state.running,
        )
    with c2:
        advantage = st.text_input(
            "Your unfair advantage (optional)",
            placeholder="e.g. former music teacher + 10y mobile dev",
            disabled=st.session_state.running,
        )
    with c3:
        budget = st.selectbox(
            "Budget tier",
            options=["", "Bootstrap (<$25k)", "Pre-seed ($25-250k)", "Seed ($250k-2M)"],
            index=0,
            disabled=st.session_state.running,
        )

    submitted = st.form_submit_button(
        "🚀 Validate Idea",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.running or not gemini_ok,
    )


# ---------------------------------------------------------------------------
# Background runner
# ---------------------------------------------------------------------------
def run_crew_threaded(params: dict, result_box: dict):
    try:
        crew = build_crew(
            idea=params["idea"],
            customer=params["customer"],
            advantage=params["advantage"],
            budget=params["budget"],
            model=params["model"],
            temperature=params["temperature"],
            max_search_results=params["max_results"],
        )
        # Expose the agents' actual roles so the live animation can track them
        # no matter what role text the student wrote.
        try:
            result_box["roles"] = [a.role for a in crew.agents]
        except Exception:  # noqa: BLE001
            result_box["roles"] = None
        crew_output = crew.kickoff()
        # Collect outputs from each task
        task_outputs = []
        try:
            task_outputs = [str(t.raw) for t in crew_output.tasks_output]
        except Exception:
            task_outputs = [str(crew_output)]
        result_box["task_outputs"] = task_outputs
        result_box["final"] = str(crew_output)
    except LabTODO as e:
        # A lab isn't finished — not a crash, just a prompt to fill something in.
        result_box["todo"] = str(e)
    except Exception as e:  # noqa: BLE001
        result_box["error"] = f"{type(e).__name__}: {e}"
    finally:
        result_box["done"] = True


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if submitted and idea.strip():
    st.session_state.running = True
    st.session_state.current_idea = idea.strip()
    st.session_state.bull_md = ""
    st.session_state.bear_md = ""
    st.session_state.memo_md = ""
    st.session_state.memo_path = ""
    st.session_state.error_msg = ""

    params = {
        "idea": idea.strip(),
        "customer": customer.strip(),
        "advantage": advantage.strip(),
        "budget": budget,
        "model": model,
        "temperature": temperature,
        "max_results": max_results,
    }

    status = st.status("🧠 Crew is working — Optimist → Skeptic → Strategist…", expanded=True)
    log_placeholder = status.empty()

    result_box: dict = {"done": False}

    with capture_stdout_stderr() as cap:
        thread = threading.Thread(
            target=run_crew_threaded,
            args=(params, result_box),
            daemon=True,
        )
        thread.start()

        last_len = 0
        last_active: str | None = None
        while not result_box["done"]:
            current = cap.getvalue()
            if len(current) != last_len:
                last_len = len(current)
                log_placeholder.code(current[-12000:], language="text")
                # Update agent cards based on the log
                active, done = detect_active_agent(current, result_box.get("roles"))
                if active != last_active:
                    last_active = active
                    with agent_cards_slot.container():
                        agent_cards(active=active, done=done)
            time.sleep(0.3)
        log_placeholder.code(cap.getvalue()[-12000:], language="text")
        # Mark all done on success path
        if "error" not in result_box:
            with agent_cards_slot.container():
                agent_cards(active=None, done={"optimist", "skeptic", "strategist"})

    if "todo" in result_box:
        status.update(label="🔨 One step left — finish the current lab", state="error")
        st.session_state.error_msg = result_box["todo"]
    elif "error" in result_box:
        status.update(label=f"❌ Failed: {result_box['error']}", state="error")
        st.session_state.error_msg = result_box["error"]
    else:
        status.update(label="✅ Crew finished", state="complete")
        outputs = result_box.get("task_outputs", [])
        # Expect 3 outputs: bull, bear, memo
        if len(outputs) >= 3:
            st.session_state.bull_md = strip_code_fences(outputs[0])
            st.session_state.bear_md = strip_code_fences(outputs[1])
            st.session_state.memo_md = strip_code_fences(outputs[2])
        else:
            st.session_state.memo_md = strip_code_fences(result_box.get("final", ""))

        # Save memo to disk
        slug = slugify(st.session_state.current_idea)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = OUTPUT_DIR / f"{slug}-{ts}.md"
        path.write_text(st.session_state.memo_md, encoding="utf-8")
        st.session_state.memo_path = str(path)

        st.session_state.history.append(
            {
                "idea": st.session_state.current_idea,
                "bull_md": st.session_state.bull_md,
                "bear_md": st.session_state.bear_md,
                "memo_md": st.session_state.memo_md,
                "memo_path": st.session_state.memo_path,
                "ts": ts,
            }
        )

    st.session_state.running = False
    st.rerun()


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if (st.session_state.memo_md or st.session_state.bull_md) and not st.session_state.running:
    st.divider()

    st.markdown(
        f"""
        <div class="result-card">
            <div class="title">🎯 Validation Result</div>
            <div class="idea">{st.session_state.current_idea}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.memo_md:
        verdict_pill(st.session_state.memo_md)

    if st.session_state.memo_path:
        st.caption(f"💾 Saved to `{st.session_state.memo_path}`")

    _, dl_md_col, dl_pdf_col = st.columns([4, 1, 1])

    base_filename = (
        Path(st.session_state.memo_path).stem
        if st.session_state.memo_path
        else "validation-memo"
    )

    with dl_md_col:
        st.download_button(
            "⬇️ .md",
            data=st.session_state.memo_md,
            file_name=f"{base_filename}.md",
            mime="text/markdown",
            use_container_width=True,
            disabled=not st.session_state.memo_md,
        )

    with dl_pdf_col:
        if st.session_state.memo_md:
            try:
                footer = f"Generated {datetime.now().strftime('%Y-%m-%d')} · CrewAI Idea Validator"
                pdf_bytes = markdown_to_pdf_bytes(st.session_state.memo_md, footer=footer)
                st.download_button(
                    "⬇️ PDF",
                    data=pdf_bytes,
                    file_name=f"{base_filename}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                )
            except Exception as e:  # noqa: BLE001
                st.error(f"PDF error: {e}")
        else:
            st.download_button(
                "⬇️ PDF", data=b"", file_name="x.pdf",
                use_container_width=True, disabled=True,
            )

    tab_memo, tab_bull, tab_bear = st.tabs(
        ["🎯 Memo", "🚀 Bull Case", "🔪 Bear Case"]
    )
    with tab_memo:
        if st.session_state.memo_md:
            st.markdown(st.session_state.memo_md)
        else:
            st.info("No memo generated.")
    with tab_bull:
        if st.session_state.bull_md:
            st.markdown(st.session_state.bull_md)
        else:
            st.info("No bull case available.")
    with tab_bear:
        if st.session_state.bear_md:
            st.markdown(st.session_state.bear_md)
        else:
            st.info("No bear case available.")

elif st.session_state.error_msg and not st.session_state.running:
    msg = st.session_state.error_msg
    if msg.lstrip().startswith(("🔨", "🔪", "🎯")):
        # A lab isn't finished yet — show the instructions as a gentle prompt.
        st.warning(msg)
        st.caption("Finish the step above, save, then click **Validate Idea** again.")
    else:
        st.error(f"Last run failed: {msg}")

elif not st.session_state.running:
    st.info(
        "👋 Describe your idea above, optionally add context, and click **Validate Idea**. "
        "Three agents will research, argue, and deliver a decision memo you can download as PDF."
    )
    with st.expander("💡 Example ideas to try"):
        st.markdown(
            "- A subscription box that mails a different rare hot sauce every month.\n"
            "- A Duolingo for learning to read sheet music in 5 minutes a day.\n"
            "- A tool that auto-generates Terraform from a screenshot of an AWS diagram.\n"
            "- A platform where retired teachers tutor kids over voice chat, paid by the minute."
        )
