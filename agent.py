import argparse
import json
import os
import re
import sys
from collections.abc import Callable
from typing import Any

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

# ── Constants ─────────────────────────────────────────────────────────────────

MODEL = "anthropic.claude-sonnet-4-5-20250929"
BASE_URL = "https://chat.dartmouth.edu/api"
TEMPERATURE = 0.3
MAX_ITERATIONS = 10       # max agent loop turns before we bail out
FETCH_TIMEOUT_SECONDS = 10
FETCH_MAX_CHARS = 10_000

# ── Prompt template ───────────────────────────────────────────────────────────
#
# The system prompt is assembled from three parts at runtime:
#
#   PROMPT_BASE      — always included. Defines the agent's role, tools,
#                      output format, and hard rules. Never changes between calls.
#                      Tested once; stable.
#
#   PROMPT_CONTEXT   — injected when the caller provides a context string.
#                      Uses {context} as the single substitution site.
#                      Tells the model WHO is asking and HOW to adapt its lens.
#
#   PROMPT_GENERIC   — injected when no context is provided.
#                      Falls back to a general B2B framing so the model still
#                      knows what kind of signals to prioritize.
#
# Keeping base and variable sections separate means you can test the base
# prompt in isolation and unit-test the injected section independently.
# The alternative — one big f-string — tangles static and dynamic content
# and makes prompt regression testing impractical.

PROMPT_BASE = """\
You are an expert B2B account researcher. Your job is to produce a concise, \
accurate research brief about a company so that the person using this tool \
can walk into a meeting, sales call, or partnership conversation fully prepared.

You have two tools:
- search_web(query): Search the internet for relevant pages about the company.
- fetch_url(url): Retrieve and read the text content of any webpage.

Your research process:
1. If the context below includes a specific URL, fetch that page first. \
Otherwise, fetch the organisation's homepage (https://{domain}).
2. Based on the context provided below, determine which signals matter most \
(e.g. funding for startup sales, earnings for public-company sales, hiring trends \
for sales targeting, security incidents for cybersecurity sales, regulatory filings \
for legal/fintech) and search for those specifically.
3. Fetch the most relevant results to gather detail.
4. Continue until you have enough information to write a complete brief.

If a fetch fails or search returns no results, try an alternative URL or query \
and keep going — do not stop early.

Output format — return a Markdown document with exactly these five sections:
## Company Overview
## What They Do
## Relevant Signals
## Likely Priorities & Pain Points
## Openers Tailored to Your Context

Rules:
- Every factual claim must be followed by its source URL in parentheses.
- Be specific — avoid generic statements like "they are a fast-growing startup."
- If you cannot find reliable information for a section, say so rather than guessing.
- Keep the entire brief under 600 words so it can be read in two minutes.
- Do not include raw lists of links — synthesize what you find into prose and bullets.\
"""

PROMPT_CONTEXT = """

--- RESEARCHER CONTEXT ---
The person using this tool has described themselves and their goal as:

  {context}

Use this context to:
- Select which signals to surface in "Relevant Signals" (match what would move the needle for this person's goal)
- Frame "Likely Priorities & Pain Points" from the perspective of this person's role and what they care about
- Make "Openers Tailored to Your Context" specific to their situation — not generic talking points
--- END CONTEXT ---"""

PROMPT_GENERIC = """

--- RESEARCHER CONTEXT ---
No specific context was provided. Research this company from a general B2B perspective. \
Prioritize signals relevant to sales, partnerships, or strategic research: \
funding rounds, product launches, leadership changes, and competitive moves.
--- END CONTEXT ---"""


def build_system_prompt(domain: str, context: str | None) -> str:
    """Assemble the system prompt from the stable base and a context-specific section.

    The substitution happens here, once, before the first API call.
    The model receives a single fully-rendered string — it never sees template syntax.
    {domain} in PROMPT_BASE tells the agent which homepage to fall back to when no
    specific URL is present in the context.
    """
    if context and context.strip():
        return PROMPT_BASE.format(domain=domain) + PROMPT_CONTEXT.format(context=context.strip())
    return PROMPT_BASE.format(domain=domain) + PROMPT_GENERIC

# ── Tool schemas ───────────────────────────────────────────────────────────────
#
# These JSON Schema objects describe each callable tool to the model.
# The model reads the "description" fields to decide when to call a tool,
# and reads "parameters" to know what arguments to pass.
# We never call these directly from Python — the model emits a structured
# JSON object referencing one of these names, and we dispatch accordingly.

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": (
                "Retrieve and extract readable text from a webpage. "
                "Use this to read homepages, about pages, blog posts, "
                "press releases, and news articles."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The full URL to fetch, including https://",
                    }
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the web for pages about a company. Returns up to 5 results "
                "with titles, URLs, and snippets. Use this to discover news, funding "
                "announcements, product launches, and leadership changes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string",
                    }
                },
                "required": ["query"],
            },
        },
    },
]


# ── Tool implementations ───────────────────────────────────────────────────────

def fetch_url(url: str) -> str:
    """Fetch a webpage and return clean readable text, truncated to FETCH_MAX_CHARS.

    Strips nav, footer, scripts, and styles before extracting text so the model
    receives signal rather than boilerplate. Returns a descriptive error string
    (not an exception) so the agent can keep going on failure.
    """
    try:
        resp = requests.get(
            url,
            timeout=FETCH_TIMEOUT_SECONDS,
            headers={"User-Agent": "Mozilla/5.0 (compatible; AccountResearchBot/1.0)"},
        )
        if resp.status_code != 200:
            return f"fetch_url failed: {resp.status_code} for {url}"

        soup = BeautifulSoup(resp.text, "html.parser")

        # Drop chrome — nav, footer, scripts, styles are noise not content
        for tag in soup(["nav", "footer", "script", "style", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if len(text) > FETCH_MAX_CHARS:
            text = text[:FETCH_MAX_CHARS] + "\n[Content truncated at 10,000 characters]"

        return text or f"fetch_url: page rendered empty after stripping for {url}"

    except requests.exceptions.Timeout:
        return f"fetch_url failed: timeout after {FETCH_TIMEOUT_SECONDS}s for {url}"
    except requests.exceptions.RequestException as exc:
        return f"fetch_url failed: {exc} for {url}"
    except Exception as exc:
        return f"fetch_url failed: unexpected error — {exc}"


def search_web(query: str, tavily_key: str | None = None) -> str:
    """Search the web via Tavily and return up to 5 results as a JSON string.

    Returns a JSON-encoded list of {"title", "url", "snippet"} dicts.
    Tool result messages must be strings, so we serialize here.
    Returns a descriptive error string on failure rather than raising.
    tavily_key overrides TAVILY_API_KEY env var — used when the UI passes a key directly.
    """
    try:
        tavily = TavilyClient(api_key=tavily_key or os.getenv("TAVILY_API_KEY"))
        response = tavily.search(query=query, max_results=5)
        results = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", ""),
            }
            for r in response.get("results", [])
        ]
        if not results:
            return f'search_web returned no results for: "{query}"'
        return json.dumps(results, indent=2)

    except Exception as exc:
        return f'search_web failed: {exc} — no results for: "{query}"'


# ── Agent loop ─────────────────────────────────────────────────────────────────

def run_agent(
    domain: str,
    verbose: bool = False,
    context: str | None = None,
    dart_api_key: str | None = None,
    tavily_api_key: str | None = None,
    on_tool_call: Callable[[str, dict], None] | None = None,
) -> str:
    """Run the research agent for a given domain and return the finished brief.

    dart_api_key / tavily_api_key override .env values — used when the Streamlit UI
    accepts keys directly from the sidebar rather than from the environment.

    on_tool_call(tool_name, tool_args) is called just before each tool executes,
    letting callers stream live status without touching stderr.

    The loop works like this:
      1. Send the conversation (system prompt + user message + any prior tool results)
         to the model.
      2. If the model returns a message with no tool_calls, it's done — return the
         content as the final brief.
      3. If the model returns tool_calls, we must:
         a. Append the assistant message to the conversation FIRST — this is required
            because the API enforces conversation ordering. Tool result messages must
            immediately follow the assistant message that requested them. Skipping
            this step causes an API error on the next turn.
         b. Execute each requested tool and append a "tool" role message for each one,
            using the tool_call_id to link result back to request. The id is how the
            model knows which result belongs to which call when multiple tools are
            invoked in the same turn.
      4. Loop until no tool_calls or MAX_ITERATIONS is hit.
    """
    load_dotenv()

    resolved_dart_key = dart_api_key or os.getenv("DARTMOUTH_CHAT_API_KEY")
    resolved_tavily_key = tavily_api_key or os.getenv("TAVILY_API_KEY")

    client = OpenAI(
        base_url=BASE_URL,
        api_key=resolved_dart_key,
    )

    messages: list[Any] = [
        {"role": "system", "content": build_system_prompt(domain, context)},
        {"role": "user", "content": f"Research the company: {domain}"},
    ]

    partial_brief = ""  # holds any content the model emits before the final turn

    for iteration in range(MAX_ITERATIONS):
        if verbose:
            print(f"[iteration {iteration + 1}/{MAX_ITERATIONS}]", file=sys.stderr)

        response = client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            tools=TOOLS,
            messages=messages,
        )

        message = response.choices[0].message

        # Save any content the model produced, even if it also issued tool calls.
        # This gives us something to return if we hit max iterations.
        if message.content:
            partial_brief = message.content

        # No tool calls → the model is satisfied with what it has gathered.
        # Return the content directly as the finished brief.
        if not message.tool_calls:
            return message.content or "[Warning: model returned empty response]"

        # Append the assistant message BEFORE adding tool results.
        # The conversation must record that the model "asked" for these tools
        # before we record the answers. The API validates this ordering.
        messages.append(message)

        # Execute every tool the model requested in this turn
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if verbose:
                print(f"[{tool_name}] {json.dumps(tool_args)}", file=sys.stderr)

            # Notify UI caller (e.g. Streamlit) before executing so it can update live
            if on_tool_call is not None:
                on_tool_call(tool_name, tool_args)

            if tool_name == "fetch_url":
                result = fetch_url(**tool_args)
            elif tool_name == "search_web":
                result = search_web(query=tool_args["query"], tavily_key=resolved_tavily_key)
            else:
                result = f"Unknown tool: {tool_name}"

            if verbose:
                preview = result[:120].replace("\n", " ")
                ellipsis = "..." if len(result) > 120 else ""
                print(f"  → {preview}{ellipsis}", file=sys.stderr)

            # Each tool result is linked to its request via tool_call_id.
            # Without this id, the model can't match a result to the call that
            # generated it — especially important when multiple tools run in one turn.
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

    # Reached MAX_ITERATIONS without a final answer from the model
    return (
        "[Warning: max iterations reached — brief may be incomplete]\n\n"
        + (partial_brief or "[No content generated]")
    )


# ── CLI ────────────────────────────────────────────────────────────────────────

def validate_domain(domain: str) -> bool:
    """Return True if the string looks like a valid domain name."""
    pattern = re.compile(
        r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$"
    )
    return bool(pattern.match(domain))


def main() -> None:
    """Entry point — parse args, validate input, run agent, emit brief."""
    parser = argparse.ArgumentParser(
        description="Account Research Assistant — generate a pre-call brief for any company domain."
    )
    parser.add_argument("domain", help='Company domain to research, e.g. "ramp.com"')
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Stream tool activity to stderr while the agent works",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Save the brief to a file instead of printing to stdout",
    )
    parser.add_argument(
        "--context",
        metavar="TEXT",
        help=(
            'Who you are and what you\'re researching for. '
            'e.g. "AE selling cybersecurity training to mid-market fintechs"'
        ),
        default=None,
    )
    args = parser.parse_args()

    if not validate_domain(args.domain):
        print(
            f'Error: "{args.domain}" doesn\'t look like a valid domain. Try "ramp.com".',
            file=sys.stderr,
        )
        sys.exit(1)

    brief = run_agent(domain=args.domain, verbose=args.verbose, context=args.context)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(brief)
        print(f"Brief saved to {args.output}", file=sys.stderr)
    else:
        print(brief)


if __name__ == "__main__":
    main()
