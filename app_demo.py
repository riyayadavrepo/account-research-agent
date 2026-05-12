import os

import streamlit as st
from dotenv import load_dotenv

from agent import run_agent, validate_domain

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Account Research Assistant",
    page_icon="🔍",
    layout="centered",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### API Keys")
    st.caption("Leave blank to use the server's default keys.")

    dart_key_override = st.text_input(
        "LLM API Key",
        value="",
        type="password",
        placeholder="sk-...",
        help="Optional. Paste your own OpenAI or compatible API key to use your own credits.",
    )

    tavily_key_override = st.text_input(
        "Tavily Search API Key",
        value="",
        type="password",
        placeholder="tvly-...",
        help="Optional. Get a free key at tavily.com.",
    )

    # Use sidebar value if provided, otherwise fall back to server .env silently
    dart_key = dart_key_override or os.getenv("DARTMOUTH_CHAT_API_KEY", "")
    tavily_key = tavily_key_override or os.getenv("TAVILY_API_KEY", "")

    st.divider()

    with st.expander("About"):
        st.markdown(
            """
**Account Research Assistant** generates structured pre-call research briefs
for any company domain using an AI agent with live web search.

The agent autonomously fetches the company homepage, searches for relevant
signals, and synthesizes a tailored brief — adapting its focus based on your
research context (sales, competitive intel, partnerships, etc.).

**Tech:** Python · OpenAI function calling · Tavily search · Streamlit
· Claude (via Dartmouth Chat API)

[View on GitHub](https://github.com/your-repo/account-research-agent) ↗
            """
        )

# ── Presets ───────────────────────────────────────────────────────────────────

PRESETS: dict[str, str] = {
    "B2B Sales (cybersec)": (
        "Account Executive selling enterprise cybersecurity products to mid-market companies. "
        "Focus on security posture, recent incidents, and existing vendor relationships."
    ),
    "B2B Sales (general)": (
        "Account Executive selling B2B SaaS to growing companies. "
        "Focus on growth signals, recent funding, and likely operational pain points."
    ),
    "Competitive intel": (
        "Product Manager doing competitive intelligence on this company. "
        "Focus on product capabilities, recent launches, customer wins, "
        "and weaknesses in their positioning."
    ),
    "Partnership research": (
        "Exploring a B2B/B2B2C partnership with this organization. "
        "Focus on their customer base, distribution model, tech maturity, "
        "and strategic priorities."
    ),
}

CONTEXT_PLACEHOLDER = (
    "Who you are + what you're researching for + (for institutions) the specific page URL.\n\n"
    "Company example:\n"
    "AE at Acme selling payroll software to mid-market retail chains — "
    "focus on labor cost signals, hiring freezes, and compliance news.\n\n"
    "Institution example:\n"
    "Co-founder of OpenDoor Justice researching BU Law's Consumer Economic Justice Clinic "
    "for a partnership. Specific page: "
    "https://www.bu.edu/law/experiential-learning/clinics/consumer-economic-justice-clinic/"
)

# ── Main panel ────────────────────────────────────────────────────────────────

st.title("Account Research Assistant")
st.caption(
    "Generate a structured B2B research brief on any company in under 90 seconds "
    "— tailored to your specific use case."
)

st.markdown("#### Company domain")
domain_input = st.text_input(
    label="domain",
    label_visibility="collapsed",
    placeholder="e.g., ramp.com",
    help="Just the domain — no https:// needed. For institutions, use the root domain and paste the specific page URL in your context below.",
)

st.markdown("#### Your context <span style='color:grey;font-size:0.85em;font-weight:normal'>(optional, but strongly recommended)</span>", unsafe_allow_html=True)
st.caption(
    "Describe who you are and what you're researching for. "
    "The agent tailors signals, pain points, and openers to your goal. "
    "For universities, nonprofits, or government agencies, paste the specific "
    "page URL — the root domain alone won't give the agent enough signal."
)

# Preset buttons — clicking one pre-fills the context textarea via session state
if "context_value" not in st.session_state:
    st.session_state["context_value"] = ""

preset_cols = st.columns(len(PRESETS))
for col, (label, value) in zip(preset_cols, PRESETS.items()):
    if col.button(label, use_container_width=True):
        st.session_state["context_value"] = value

context_input = st.text_area(
    label="context_area",
    label_visibility="collapsed",
    value=st.session_state["context_value"],
    placeholder=CONTEXT_PLACEHOLDER,
    height=130,
)

generate = st.button("Generate Brief", type="primary", use_container_width=True)

# ── Cache ─────────────────────────────────────────────────────────────────────

if "results_cache" not in st.session_state:
    st.session_state["results_cache"] = {}

# ── Run ───────────────────────────────────────────────────────────────────────

if generate:
    raw_domain = domain_input.strip().lower()
    context = context_input.strip() or None

    # Validate inputs before touching the API
    if not raw_domain:
        st.error("Please enter a company domain.")
        st.stop()

    if not validate_domain(raw_domain):
        st.error(
            f'**"{raw_domain}"** doesn\'t look like a valid domain. '
            'Try something like `ramp.com` or `akamai.com`.'
        )
        st.stop()

    if not dart_key:
        st.error(
            "**Dartmouth Chat API Key is missing.** "
            "Add it in the sidebar or set `DARTMOUTH_CHAT_API_KEY` in your `.env` file."
        )
        st.stop()

    if not tavily_key:
        st.error(
            "**Tavily API Key is missing.** "
            "Add it in the sidebar or set `TAVILY_API_KEY` in your `.env` file. "
            "Get a free key at [tavily.com](https://tavily.com)."
        )
        st.stop()

    cache_key = (raw_domain, context or "")

    if cache_key in st.session_state["results_cache"]:
        # Serve cached result — skip the agent run entirely
        brief = st.session_state["results_cache"][cache_key]
        if context:
            st.info(f"**Research lens:** {context}")
        st.caption("*Showing cached result. Modify the domain or context and click Generate to run a fresh search.*")
        st.markdown("---")
        st.markdown(brief)
        st.download_button(
            label="Download as Markdown",
            data=brief,
            file_name=f"{raw_domain.replace('.', '_')}_brief.md",
            mime="text/markdown",
        )
        st.stop()

    # Live status area — updated by on_tool_call as the agent works
    status_container = st.empty()
    tool_log: list[str] = []

    def on_tool_call(tool_name: str, tool_args: dict) -> None:
        if tool_name == "fetch_url":
            url = tool_args.get("url", "")
            entry = f"📄 Reading `{url}`"
        else:
            query = tool_args.get("query", "")
            entry = f"🔎 Searching: *{query}*"
        tool_log.append(entry)
        # Show the last 6 tool calls as a live log inside the placeholder
        status_container.markdown(
            "**Agent activity**\n\n" + "\n\n".join(tool_log[-6:])
        )

    with st.spinner(f"Researching **{raw_domain}**…"):
        brief = run_agent(
            domain=raw_domain,
            context=context,
            dart_api_key=dart_key,
            tavily_api_key=tavily_key,
            on_tool_call=on_tool_call,
        )

    # Clear the live status log now that we have the result
    status_container.empty()

    # Cache the result for this session
    st.session_state["results_cache"][cache_key] = brief

    # Show the research lens so the user remembers what framing was used
    if context:
        st.info(f"**Research lens:** {context}")

    st.markdown("---")
    st.markdown(brief)

    st.download_button(
        label="Download as Markdown",
        data=brief,
        file_name=f"{raw_domain.replace('.', '_')}_brief.md",
        mime="text/markdown",
    )
