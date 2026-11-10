---
title: "Agent integrations"
description: "Install the ibkr-httpapi skill in Claude Code, Codex or OpenClaw, or bridge the /mcp endpoint to stdio-only MCP clients with the OpenClaw plugin."
nav_order: 9
---

# Agent integrations

There are two ways for an agent to use a running ibkr-httpapi server:

- The **skill** in [`.agents/skills/ibkr-httpapi/`](https://github.com/psyb0t/ibkr-httpapi/tree/main/.agents/skills/ibkr-httpapi) teaches the agent the REST API with curl, including the confirmation rules for anything that touches the account. Any agent that reads `.agents/skills/` picks it up, [peen](https://github.com/psyb0t/peen) for example.
- The **MCP endpoint** at `/mcp` gives the agent typed tools. Clients that support remote HTTP MCP servers connect to it directly ([MCP server](mcp.md)); stdio-only clients go through the OpenClaw plugin below.

Neither one starts a server or holds IBKR credentials. They need the URL of a stack you already run and, if auth is on, its API token.

## Claude Code

```bash
claude plugin marketplace add psyb0t/agents
claude plugin install ibkr-httpapi@psyb0t
```

Claude Code asks for the server URL, including the `/v1` prefix (for example `http://localhost:8889/v1`), which becomes `IBKR_HTTPAPI_URL`, and the API token, which becomes `API_TOKEN` and goes into the OS keychain. The manifest is [`.agents/.claude-plugin/plugin.json`](https://github.com/psyb0t/ibkr-httpapi/blob/main/.agents/.claude-plugin/plugin.json).

## Codex

```bash
codex plugin marketplace add psyb0t/agents
codex plugin add ibkr-httpapi@psyb0t
```

Installed from the marketplace, the skill is invoked as `$ibkr-httpapi:ibkr-httpapi`. Codex also loads it without any install in a checkout of this repository, where it is plain `$ibkr-httpapi`. Set `IBKR_HTTPAPI_URL` and `API_TOKEN` in the environment.

## OpenClaw skill

Every release publishes the skill to ClawHub:

```bash
openclaw skills install @psyb0t/ibkr-httpapi
```

The skill reads `IBKR_HTTPAPI_URL` (with `/v1`) and `API_TOKEN` from the environment.

## OpenClaw plugin

The [`@psyb0t/ibkr-httpapi`](https://github.com/psyb0t/ibkr-httpapi/tree/main/.agents/plugins/ibkr-httpapi) plugin is a small Node.js wrapper around [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) that turns the server's `/mcp` endpoint into a local stdio MCP server. It is also published to ClawHub on every release.

```bash
openclaw plugins install clawhub:@psyb0t/ibkr-httpapi
```

| Variable | Required | Meaning |
| --- | --- | --- |
| `IBKR_HTTPAPI_URL` | yes | The server root, for example `http://localhost:8889`. A trailing `/v1` is stripped, then the bridge appends `/mcp/`. |
| `IBKR_HTTPAPI_TOKEN` | when auth is on | Sent as `Authorization: Bearer <token>`. The same token that guards REST. |

The skill and the Claude Code plugin need the URL with `/v1`. The bridge accepts either form, so one `IBKR_HTTPAPI_URL` value can serve both.

## Safety

The skill tells the agent to confirm every order, cancel and exercise with you, one action at a time, to show which account and server it is about to touch, and never to read tokens from repository files. The MCP tool descriptions carry the same warning. Those are instructions to a model, not a lock. Give an agent a paper login, or set `READ_ONLY_API=yes` in `.env.ibkr`, if it must not be able to trade.
