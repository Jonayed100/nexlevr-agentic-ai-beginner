# Daily Trends Digest Agent

An AI agent that reads 5 news feeds for one industry and writes a daily
5-bullet digest with source links and post ideas a brand could use.

Task 2 of the Beginner track of the NEXLEVR Agentic AI Developer internship.
Industry chosen: **tech**.

## What it produces

A Markdown file in `digests/`, one per day, in this shape:

```
# Tech trends digest - 2026-11-16

- **Short trend headline** - one sentence on why it matters. Source: [Source name](link). Post idea: one concrete social post a tech brand could publish today.
- ... (5 bullets in total)
```

## Files

| File | Purpose |
|------|---------|
| `agent.py` | The feed tool, the agent loop and the output check |
| `feeds.json` | The industry and its 5 sources. Edit this to change industry |
| `digests/` | Created on the first run; holds one digest per day |

No packages to install (Python 3.9+, standard library only).

## How to run

Set the same three values as in Task 1, then run the script.

| Variable | Meaning |
|----------|---------|
| `LLM_API_KEY` | Your API key |
| `LLM_BASE_URL` | The provider's OpenAI-compatible URL (default: Groq's) |
| `LLM_MODEL` | A model from your provider that supports tool calling |

```bash
export LLM_API_KEY="your-key"
export LLM_MODEL="model-name-from-your-provider"
python agent.py
```

On Windows PowerShell, use `$env:LLM_API_KEY = "your-key"` and
`$env:LLM_MODEL = "..."` instead of the `export` lines.

To make it truly daily, schedule that command with cron (Linux/macOS) or
Task Scheduler (Windows).

## How it works, step by step

1. **Load the sources.** `feeds.json` gives the industry and 5 feed URLs.
2. **Brief the model.** The system prompt tells it the allowed sources, the
   exact output format, and two rules: only use links from tool results, and
   treat feed text as data, not instructions.
3. **The model calls `fetch_feed`.** It asks for each source by name. It
   never sees or chooses a URL; the script maps the name to the URL from
   `feeds.json`, so the model cannot make the script open an arbitrary site.
4. **The script fetches and parses.** It downloads the feed, reads both RSS
   (`<item>`) and Atom (`<entry>`) formats, strips HTML, and returns the 5
   newest items: title, link, date, short summary.
5. **Failures are reported, not fatal.** If one feed is down, the tool
   returns an error message and the model continues with the others.
6. **The model writes the digest.** With the headlines in hand, it picks 5
   trends and writes the bullets.
7. **The script checks the result.** Before saving, `check_digest` verifies
   there are exactly 5 bullets, each has a link, and every link really came
   from a feed. Anything suspicious is saved under a "Needs review" note
   and printed as a warning.
8. **Save.** The digest goes to `digests/YYYY-MM-DD.md`.

## Guardrails

- **Allow-list of sources:** the tool only accepts names from `feeds.json`.
- **No invented links:** every link in the digest is checked against links
  the tool actually returned.
- **Untrusted input:** feed text is labelled as data in the prompt, so an
  instruction hidden in a headline should not be obeyed.
- **Bounded loop:** at most 8 model turns, and feeds are capped at 2 MB.
- **Human in control:** the agent writes a draft file. It posts nothing.

## Changing the industry

Edit `feeds.json`: set `"industry"` to fashion, food, fitness or anything
else, and replace the 5 feeds with RSS or Atom URLs for that industry.

## Limits

- Feed URLs change over time. If a source fails, replace its URL in
  `feeds.json`.
- The digest is only as good as the headlines; it reads summaries, not full
  articles.
