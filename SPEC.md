# Account Research Assistant — Product Spec

## Problem & User

**Who uses this:** B2B sales reps, account executives, partnership leads, and product managers who need to understand a company before a call, demo, or outreach.

**The painful workflow it replaces:** Before any important meeting, these people manually open a dozen browser tabs — the company's homepage, their blog, Crunchbase, LinkedIn, Google News — skim each one, and try to synthesize it into something useful. That process takes 30–60 minutes per prospect, gets skipped under time pressure, and produces inconsistent results depending on how thorough the person is that day.

**The outcome:** A consistent, well-structured research brief delivered in under two minutes, tailored to who is asking and why.

---

## Inputs & Outputs

**Inputs:**

| Input | Required? | Example |
|---|---|---|
| Company domain | Required | `ramp.com` |
| Researcher context | Optional | `"AE selling cybersecurity training to mid-market fintechs"` |

The context string describes who the user is and what they are researching for. It tells the agent which signals to surface, how to frame pain points, and how to angle the conversation openers. Without it, the agent falls back to a generic B2B framing.

**Output:** A structured Markdown research brief with the following sections:

| Section | What it contains |
|---|---|
| **Company Overview** | What they do, size, funding stage, headquarters — always universal |
| **What They Do** | Core product or service, target customers, business model — always universal |
| **Relevant Signals** | Recent developments selected based on context (funding, earnings, breaches, hiring, regulatory action, product launches, etc.) |
| **Likely Priorities & Pain Points** | Inferred challenges framed from the perspective of the researcher's role and goal |
| **Openers Tailored to Your Context** | 3–5 specific talking points calibrated to the researcher's situation |

All claims are cited with the source URL so the reader can verify or dig deeper.

---

### Example output — `ramp.com` under three contexts

> **Note:** These are illustrative examples showing how the same company produces different briefs depending on context. Not live data.

---

#### Context: "AE selling cybersecurity training to mid-market fintechs"

## Company Overview
Ramp is a corporate card and spend management platform founded in 2019, headquartered in New York. It raised $500M at a $22.5B valuation in July 2025 and serves over 40,000 businesses. (https://ramp.com/about)

## What They Do
Ramp offers corporate cards, bill pay, expense management, procurement, and AI-powered spend automation in a single platform. Target customers are finance teams at growth-stage and mid-market companies. (https://ramp.com/product)

## Relevant Signals
- Ramp launched autonomous AI agents in July 2025 that access sensitive financial data across thousands of vendor accounts — expanding the blast radius of any credential compromise. (https://prnewswire.com/ramp-ai-agents)
- Ramp processes $80B+ in annualized purchase volume, making its platform a high-value target for social engineering and phishing campaigns against finance teams. (https://ramp.com)
- No recent public disclosures of security incidents, but the fintech sector averaged 2.5 breaches per company in 2024, with expense platforms frequently targeted. (https://ibm.com/cost-of-data-breach-2024)

## Likely Priorities & Pain Points
- Finance teams at Ramp's customer companies handle large volumes of transactions across many vendors — employees approving expenses are a prime phishing target and rarely receive role-specific security training
- Ramp's AI agents authenticate automatically across external systems; a compromised employee credential could cascade across the entire vendor network
- As a fintech serving 40,000 companies, Ramp likely has SOC 2 and PCI compliance obligations that require demonstrable employee security awareness programs

## Openers Tailored to Your Context
- "Your AI agents now authenticate across hundreds of vendor accounts on behalf of finance teams — has that changed how you think about credential security training for the employees those agents act for?"
- "Finance teams are the #1 target for BEC attacks. Are Ramp's customers asking you about employee security awareness as part of onboarding?"
- "PCI DSS 4.0 requires documented security training for anyone who handles cardholder data. Does that create a compliance conversation you're having with prospects?"

---

#### Context: "PM exploring partnership and integration opportunities"

## Company Overview
Ramp is a financial operations platform founded in 2019, headquartered in New York. Raised $500M in July 2025 at a $22.5B valuation, serving 40,000+ businesses. (https://ramp.com/about)

## What They Do
Ramp consolidates corporate cards, bill pay, expense management, procurement, and travel into one platform with an AI automation layer. Positioned as a replacement for fragmented point solutions. (https://ramp.com/product)

## Relevant Signals
- Ramp launched an AI agents platform in July 2025, built on OpenAI reasoning models — indicating an active API/SDK ecosystem and a potential surface for third-party integrations. (https://prnewswire.com/ramp-ai-agents)
- Ramp announced a Stripe partnership in 2024 to embed cards into Stripe's billing workflows — a precedent for deep API partnerships over surface-level integrations. (https://ramp.com/blog)
- Ramp Treasury launched in 2024 and crossed $1B AUM — a new product line still building out its integration ecosystem. (https://prnewswire.com/ramp-series-e)

## Likely Priorities & Pain Points
- Ramp's platform vision is to replace 4+ point solutions; they need native integrations with the tools their customers already use (ERP systems, HRIS, procurement software) to close deals against Brex and Concur
- The AI agents layer requires clean data pipelines from third-party vendors — a gap for companies with clean structured data to offer as a feed
- Treasury is a new product line that likely needs ecosystem partners for yield products, FX, or embedded banking features

## Openers Tailored to Your Context
- "Your AI agents layer seems to require clean vendor data — are you building a partner program for companies that can feed structured data into those workflows?"
- "The Stripe integration in 2024 looked like a deep API partnership rather than a simple connector. Is that the model you're applying to other ecosystem partners?"
- "Ramp Treasury is growing fast — what does the integration roadmap look like for yield products or embedded banking partners?"

---

#### Context: "Investor researching potential acquisition targets in fintech"

## Company Overview
Ramp is a financial operations platform founded in 2019, headquartered in New York. Latest round: $500M Series E-2 at $22.5B valuation (July 2025), total equity raised: $1.9B. Achieved positive cash flow in early 2025. ~1,200 employees. (https://prnewswire.com/ramp-series-e)

## What They Do
Ramp sells corporate spend management to 40,000+ businesses, processing $80B+ annualized purchase volume. Revenue model is primarily interchange (card transactions) plus SaaS fees for software products. Most customers use 2+ products — a strong cross-sell signal. (https://ramp.com)

## Relevant Signals
- Two funding rounds 45 days apart (June and July 2025) at dramatically increasing valuations ($16B → $22.5B) suggest either a competitive process or staged capital deployment ahead of a liquidity event. (https://prnewswire.com/ramp-series-e)
- CEO Eric Glyman publicly committed to "autonomous finance by 2028" — a 3-year product horizon that suggests a pre-IPO build phase, not near-term acquisition mode. (https://cfodive.com/ramp-ceo-autonomous-finance)
- Ramp crossed positive cash flow in 2025 with $80B transaction volume — interchange at standard rates implies $240–320M annualized gross revenue assuming 30–40bps. (https://prnewswire.com/ramp-series-e)

## Likely Priorities & Pain Points
- Interchange revenue is structurally under regulatory pressure (Durbin Amendment, potential EU-style caps) — long-term model needs SaaS revenue to grow as a share of mix
- Enterprise upmarket push faces entrenched competition from Concur (SAP), Coupa, and American Express; Ramp's self-serve DNA may create friction at larger deal sizes
- $22.5B valuation at estimated ~$300M revenue implies ~75x revenue multiple — justifiable only if growth rate and SaaS mix continue expanding

## Openers Tailored to Your Context
- "You've raised $1.9B total and are cash flow positive — what does the path to liquidity look like from your perspective? IPO, strategic, or longer-term independence?"
- "Interchange revenue carries regulatory tail risk. How large does the SaaS revenue mix need to be before you feel structurally protected?"
- "Your valuation implies continued hyper-growth. What's the biggest execution risk between here and that outcome?"

---

## Architecture

**Runtime:** Python script, no web server, runs from the command line. Streamlit web UI available via `app.py`.

**Model:** `anthropic.claude-sonnet-4-5-20250929` via the Dartmouth Chat API  
(`https://chat.dartmouth.edu/api`), accessed using the OpenAI Python SDK with a custom `base_url`.

**Temperature:** `0.3` — low enough for factual consistency and predictable output structure, with just enough flexibility for natural prose.

**Why this model:** Dartmouth Chat provides free API credits for Dartmouth-affiliated users. The OpenAI SDK is used because Dartmouth Chat exposes an OpenAI-compatible interface.

**Tools the agent has access to:**

- `fetch_url(url: str) → str`  
  Retrieves a webpage and extracts its readable text content. Used to read homepages, about pages, press releases, blog posts, and news articles.  
  Output is truncated to **10,000 characters** before being returned to the model. This prevents oversized pages (e.g. documentation sites, long blog archives) from consuming the entire context window. If truncation occurs, a note is appended: `[Content truncated at 10,000 characters]`.

- `search_web(query: str) → list[{title, url, snippet}]`  
  Searches the web and returns a ranked list of relevant URLs with titles and snippets. The agent uses this to find pages worth fetching.  
  > **TODO:** Requires a [Tavily](https://tavily.com) API key (`TAVILY_API_KEY` in `.env`). Tavily is a search API built for AI agents that returns clean, LLM-friendly results.

**`--verbose` flag:** When the script is run with `--verbose`, the agent streams a live activity log to `stderr` — each tool call name and argument is printed as it happens (e.g. `[search_web] "Ramp funding 2024"`). The final brief still goes to `stdout` only, so the two streams can be separated cleanly in terminal or piped output.

**Flow:**
1. User provides a domain (e.g. `ramp.com`) and optional context string
2. The system prompt is assembled: stable base + context-specific section (or generic fallback)
3. The agent calls tools autonomously — the specific signals it searches for depend on the context
4. The agent writes the final brief in structured Markdown and returns it
5. The brief is printed to stdout (and optionally saved to a `.md` file)

> **v1 vs. v2 trade-off:** v1 uses a guided research process (homepage → context-relevant search → fetch top results) to keep behavior predictable; a fully autonomous v2 would let the model plan its own research strategy from scratch, which is more flexible but harder to debug and evaluate.

---

## Prompt Template Structure

The system prompt is assembled from three separate string constants:

**`PROMPT_BASE`** (always included) — defines the agent's role, available tools, output format, and hard rules. This part never changes between calls. Keeping it separate from the variable sections means you can test and evaluate it in isolation.

**`PROMPT_CONTEXT`** (injected when context is provided) — contains a single `{context}` substitution site. Rendered at runtime via `str.format(context=...)`. Instructs the model to use the provided context to select signals, frame pain points, and angle conversation openers.

**`PROMPT_GENERIC`** (injected when no context) — a static fallback that tells the model to apply a general B2B lens. No substitution needed.

The assembly function `build_system_prompt(context: str | None) -> str` picks the right section and concatenates. The model receives a single fully-rendered string — it never sees template syntax.

**Why separate them:** A single big f-string tangles stable and variable content, making prompt regression testing impractical. With the three-part structure, you can run eval suites against `PROMPT_BASE` independently, unit-test the context injection with fixed inputs, and swap out either section without touching the other.

---

## Agent Loop

```
user_message = "Research the company: {domain}"

messages = [build_system_prompt(context), user_message]

while True:
    response = model.chat(messages, tools=[fetch_url, search_web], temperature=0.3)

    if response has no tool calls:
        # Model is done — the response is the final brief
        print(response.content)
        break

    # Execute each tool the model requested
    for tool_call in response.tool_calls:
        if verbose:
            stderr.write(f"[{tool_call.name}] {tool_call.args}")
        result = execute_tool(tool_call.name, tool_call.args)
        messages.append(tool_result(tool_call.id, result))

    # Add the model's response to the conversation and loop
    messages.append(response)
```

The model decides what to search, what to fetch, and when it has enough information to stop. The context string shapes *which* signals it searches for, not the structure of the loop itself.

A maximum iteration limit (10 tool calls) is enforced to prevent runaway loops.

---

## Error Handling

| Scenario | Behavior |
|---|---|
| **Invalid domain** | Validated with a regex before the agent starts. If the input doesn't look like a domain (e.g. missing TLD, contains spaces), exit immediately with a clear error message: `Error: "{input}" doesn't look like a valid domain. Try "ramp.com".` |
| **Failed fetch** | If `fetch_url` gets a non-200 HTTP response or a network timeout, return an error string to the model: `fetch_url failed: 404 for https://...`. The model is instructed to skip failed URLs and continue research rather than stopping. |
| **Max iterations exceeded** | If the agent reaches 10 tool calls without returning a final answer, the loop exits and prints whatever the last model message was, prefixed with a warning: `[Warning: max iterations reached — brief may be incomplete]`. |
| **Empty search results** | If `search_web` returns zero results, return `search_web returned no results for: "{query}"` to the model so it can try a different query rather than looping on an empty state. |
| **Oversized page** | `fetch_url` truncates all output at 10,000 characters and appends `[Content truncated at 10,000 characters]`. The model is not given raw HTML — only extracted text — so this limit applies to the readable content after parsing. |

---

## System Prompt

See `PROMPT_BASE`, `PROMPT_CONTEXT`, and `PROMPT_GENERIC` in `agent.py`. The rendered prompt for a cybersecurity AE researching `ramp.com` would look like:

```
You are an expert B2B account researcher...
[base content]

--- RESEARCHER CONTEXT ---
The person using this tool has described themselves and their goal as:

  AE selling cybersecurity training to mid-market fintechs

Use this context to:
- Select which signals to surface in "Relevant Signals"...
- Frame "Likely Priorities & Pain Points" from the perspective of this person's role...
- Make "Openers Tailored to Your Context" specific to their situation...
--- END CONTEXT ---
```

---

## Definition of Done

The v1 implementation is complete when all of the following are true:

- [ ] Running `python agent.py ramp.com` produces a brief with all five sections populated in under 120 seconds
- [ ] Running `python agent.py ramp.com --context "AE selling cybersecurity"` produces a brief with signals and openers visibly different from the no-context run
- [ ] Every factual claim in the output includes a cited URL
- [ ] The brief is under 600 words
- [ ] Running with `--verbose` streams tool activity to `stderr` without corrupting the `stdout` brief
- [ ] An invalid domain (e.g. `notadomain`) exits with a clear error message and a non-zero exit code
- [ ] A domain with no findable web presence (e.g. `zzznoresults123.com`) completes without crashing and notes the lack of information
- [ ] Fetching a page that exceeds 10,000 characters does not cause an error — output is silently truncated
- [ ] The agent never exceeds 10 tool calls in a single run
- [ ] Streamlit UI (`app.py`) renders the brief and shows the research lens above the output when context is provided
- [ ] Tested against at least 5 real company domains spanning different industries and sizes

---

## Out of Scope for v1

The following are explicitly excluded from this version to keep scope manageable:

- **LinkedIn data** — scraping LinkedIn is against their ToS and unreliable; contact and org-chart data is out of scope
- **Paid news APIs** — no integration with Bloomberg, Dow Jones, or similar; public web search is sufficient for v1
- **Structured contact extraction** — the brief does not identify or output individual names, emails, or phone numbers
- **Multi-language support** — the brief is always written in English regardless of the company's home country
- **CRM integration** — no syncing to Salesforce, HubSpot, or other tools; output is plain Markdown
- **Batch processing** — one company at a time; no bulk research mode
