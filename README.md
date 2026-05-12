# Account Research Assistant

**Generate a structured B2B research brief on any company in under 90 seconds, tailored to your specific use case.**

---

## Demo

![demo](docs/demo.png)

---

## Why this exists

B2B sales reps, PMs, and partnership leads spend 30–60 minutes per prospect doing manual research across a dozen browser tabs before every call — and still walk in under-prepared. Generic AI tools produce generic briefs: the same five facts about every company, formatted differently. This tool produces context-aware briefs that adapt based on who is asking and why — a cybersecurity AE sees breach history and compliance gaps; a PM doing competitive intel sees product weaknesses and positioning vulnerabilities; a founder exploring a partnership sees distribution model and tech maturity.

---

## What it does

- **Domain in, structured brief out.** Paste any company domain (`ramp.com`, `akamai.com`) and get a five-section Markdown brief: Company Overview, What They Do, Relevant Signals, Likely Priorities & Pain Points, and Openers Tailored to Your Context.
- **Context-aware output.** The same company produces a different brief depending on your role and goal. A cybersecurity AE gets phishing exposure and compliance certifications; a PM doing competitive intel gets product gaps and analyst positioning; a founder exploring a partnership gets customer base and integration maturity.
- **Real agent loop with tool use.** The model autonomously decides what to search and fetch across multiple iterations — it is not a single prompt. It uses Tavily for web search and a custom `fetch_url` tool for page extraction, stopping when it has enough information.
- **Every claim is cited.** All factual statements include source URLs so you can verify or dig deeper before the call.
- **CLI and web UI.** Run `python agent.py ramp.com --verbose --context "..."` from the terminal, or use the Streamlit UI for a point-and-click interface with live agent activity streaming.

---

## Example output

From a real run on `akamai.com` with context: *"Product Manager doing competitive intelligence on Akamai's Bot Management product line."*

```
## Relevant Signals

**Analyst positioning gap:** Akamai's most recent Forrester Bot Management Leader citation
is from 2022. In the Q3 2024 Forrester Wave, HUMAN Security achieved the top strategy score
and highest scores across nine criteria including Detection Models and Mobile/API Protection.
Akamai did not appear in the 2024 top-tier rankings. (humansecurity.com/forrester-wave-2024)

**Customer complaints on detection accuracy:** An El Al engineer using Akamai Bot Manager
publicly stated their anomaly detection "is not really helpful" because sophisticated bots
move like humans. Customers report needing to manually analyze traffic patterns and fine-tune
thresholds after each attack — automatic ML-based tuning is absent. (peerspot.com/akamai-bot-manager)

**Bundling trap:** Bot Manager cannot be purchased standalone — it requires an existing
Kona Site Defender (WAF) or CDN contract, creating friction in pure bot management evaluations.
(vendr.com/marketplace/akamai-technologies)

## Openers Tailored to Your Context

"Akamai's last Forrester Bot Management citation is from 2022. In the 2024 Wave, we scored
highest in strategy and across nine criteria. When prospects bring up Akamai's analyst
recognition, that's the specific response."

"An El Al security engineer published that Akamai's anomaly detection 'is not really helpful'
against sophisticated bots. If a prospect is running Akamai and facing evasive bots, that's
the conversation to open."
```

---

## Quick start

```bash
# Clone and set up environment
git clone https://github.com/your-repo/account-research-agent.git
cd account-research-agent
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add API keys
cp .env.example .env
# Edit .env and add:
#   DARTMOUTH_CHAT_API_KEY=your-key
#   TAVILY_API_KEY=your-key

# CLI
python agent.py ramp.com
python agent.py ramp.com --context "AE selling cybersecurity to mid-market fintechs"
python agent.py ramp.com --verbose --output brief.md

# Web UI
streamlit run app_demo.py
```

---

## Architecture

The agent uses the OpenAI Python SDK pointed at Dartmouth Chat (`chat.dartmouth.edu/api`), which exposes an OpenAI-compatible interface to Claude Sonnet 4.5. On each iteration, the model receives the conversation history and a list of two tools — `search_web` (Tavily) and `fetch_url` (requests + BeautifulSoup with nav/footer/script stripping and 10,000-character truncation) — and emits either tool calls or a final answer. Tool results are appended to the conversation with matching `tool_call_id`s and the loop continues until the model stops calling tools or hits the 10-iteration limit. The system prompt is assembled from three separate string constants: a stable base that defines role, output format, and rules; a context-injection section rendered with the user's research framing; and a generic fallback when no context is provided. The Streamlit UI wires an `on_tool_call` callback into the loop to stream live agent activity to the frontend without touching stderr.

---

## Design decisions worth noting

- **Institution-domain affordance:** For universities, nonprofits, and government agencies, the root domain (e.g. `bu.edu`) gives the agent no useful signal and burns iterations exploring irrelevant pages. The system prompt instructs the agent to fetch a specific URL from the context first if one is present — learned from a real test run on BU Law's debt collection clinic where the first attempt hit max iterations on the root domain.
- **`on_tool_call` fires before execution:** The callback fires before the tool runs, not after, so the UI shows "Searching: *Ramp funding 2025*" while the search is happening rather than displaying a completed log after the fact.
- **Personal/demo app split:** `app.py` pre-fills API keys from `.env` for personal use; `app_demo.py` shows blank optional override fields that fall back to the server's keys silently — safe to screen-share during demos without exposing credentials.
- **Three-part prompt template:** The system prompt is split into `PROMPT_BASE` (stable), `PROMPT_CONTEXT` (rendered with `str.format(context=...)`), and `PROMPT_GENERIC` (static fallback) so each section can be tested and evaluated independently without touching the others.

---

## Honest limitations

- **Hallucination risk on edge claims.** The agent synthesizes from web sources it finds at runtime. On one competitive intelligence run, a third-party proxy vendor blog appeared in search results and was cited as a source for market rankings — that citation needed manual verification before use in a customer conversation. Treat every claim as a research starting point, not a source of record.
- **Not a replacement for human judgment on critical deals.** The brief surfaces signals and openers; it does not know your relationship history with the account, internal context, or what actually matters to that specific buyer. It is pre-call preparation, not deal strategy.
- **Quality varies with domain.** Works well for tech companies with strong public web footprints (SaaS, fintech, cybersecurity). Works poorly for private companies with minimal press coverage, low-profile professional services firms, or organizations where the relevant research lives behind paywalls.
- **Tavily free tier has rate limits.** At scale or in rapid-fire testing, searches start returning empty results. A paid Tavily plan or fallback search provider would be needed for production use.

---

## v2 / production roadmap

- **Batch mode:** CSV of domains in, one brief per row out — for SDRs who need to prep a full pipeline before a territory review.
- **CRM integration:** Push the finished brief directly into a Salesforce or HubSpot account record so reps don't have to copy-paste.
- **Slack bot:** `/research ramp.com` in a deal channel returns the brief inline — zero context-switching for AEs.
- **Team-configured context prompts:** Organizations define their own context templates once (e.g. "We sell [product] to [ICP]") so every rep gets consistently framed briefs without having to write their own context each time.

---

## Built with

- [Python 3.10](https://python.org)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Anthropic Claude Sonnet 4.5](https://anthropic.com) via [Dartmouth Chat](https://chat.dartmouth.edu)
- [Tavily](https://tavily.com) — search API built for AI agents
- [Streamlit](https://streamlit.io)
- [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io)
- [Requests](https://requests.readthedocs.io)
