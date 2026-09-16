# agent-infra-digest

A daily digest of AI agent infrastructure news, curated for wes.

## What this is

Every morning, this repo gets a new file in `digests/` covering the last 24-48 hours of news across:

- Agent frameworks and harnesses
- The MCP (Model Context Protocol) ecosystem
- Coding agents
- Agent infrastructure startups and funding
- Session, context, and memory management (the LegCli problem space)

Each story gets one link and one "why it matters" line. Nothing more. The digest is a briefing, not a newspaper.

## Daily runbook

A scheduled run executes every day at 06:30 America/New_York:

1. Search the web for agent infrastructure news from the last 1-2 days (frameworks, MCP, coding agents, funding, session/context memory).
2. Check social channels for what practitioners are posting.
3. Write `digests/YYYY-MM-DD.md` using the template below. Max ~10 stories. Links must be copied verbatim from the search results. Every story gets one "why it matters" line. No em dashes.
4. `git add` and commit locally.
5. Push to `origin` only if the remote repo exists. Never attempt to create the GitHub repo; that is wes's step.

## Manual run

```bash
cd ~/workspace/agent-infra-digest
# research, then write digests/YYYY-MM-DD.md
git add digests/
git commit -m "digest: YYYY-MM-DD"
git push origin main   # only if the remote exists
```

## Digest template

```markdown
# Agent Infra Digest, YYYY-MM-DD

## 1. Headline here
[Source Name](https://...)
Why it matters: one line.

## 2. Next headline
...
```

## License

MIT. See LICENSE.
