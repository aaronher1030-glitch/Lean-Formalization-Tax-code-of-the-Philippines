# discord-mcp-lite

A read-only Discord MCP server in a single file with zero dependencies. No clone-and-build: download `server.mjs`, set a bot token, point your MCP client at it.

```
server.mjs    ~400 lines, Node >= 20, no npm packages
tests/        runs offline against a mock Discord API
```

## Why another Discord MCP server

Existing Discord MCP servers require `git clone`, `npm install`, and `npm run build`. This one is one file. It is also read-only by design: there is no post or delete tool, so an LLM mistake cannot send anything to anyone.

## Requirements

- Node.js 20 or newer
- A Discord bot that is a member of the servers you want to read

## 1. Create the bot

1. Open https://discord.com/developers/applications and create an application.
2. In **Bot**, reset and copy the token. Treat it like a password.
3. In **Bot**, enable **Message Content Intent**. Without it, Discord sends empty message bodies and the server can only see who spoke, not what they said.
4. Invite the bot with the `bot` scope and these permissions: **View Channels**, **Read Message History**, and **Send Messages** is *not* needed:

   ```
   https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot&permissions=66560
   ```

   66560 = View Channels (1024) + Read Message History (65536).

## 2. Run it

```bash
node server.mjs
```

It speaks JSON-RPC over stdio and prints nothing else to stdout, so it is meant to be launched by an MCP client, not used in a terminal.

Published package (after the maintainer runs `npm publish`):

```bash
npx -y discord-mcp-lite
```

## 3. Configure your MCP client

Qoder: **Settings → MCP → Add**, or your client's `mcpServers` JSON:

```json
{
  "mcpServers": {
    "discord": {
      "command": "node",
      "args": ["C:/path/to/discord-mcp-lite/server.mjs"],
      "env": {
        "DISCORD_TOKEN": "your_bot_token_here"
      }
    }
  }
}
```

Or, with the npm package:

```json
{
  "mcpServers": {
    "discord": {
      "command": "npx",
      "args": ["-y", "discord-mcp-lite"],
      "env": { "DISCORD_TOKEN": "your_bot_token_here" }
    }
  }
}
```

The token belongs in the MCP config or environment. Never in this repository, never in a chat message.

## Tools

| Tool | Arguments | What it does |
| --- | --- | --- |
| `list_guilds` | none | Servers the bot can see. Start here. |
| `list_channels` | `guild_id` | Text, announcement, forum, and thread channels with ids. |
| `find_channel` | `query`, optional `guild_id` | Case-insensitive name search across all guilds. |
| `read_messages` | `channel_id`, optional `limit` (default 100, max 1000), `before`, `since` (ISO date), `oldest_first` | Paginated message history for a channel or thread. |
| `list_threads` | `guild_id`, optional `channel_id` | Active threads; the first 100 archived public threads when a channel is given. |

Typical prompts this enables:

- "Summarize the last 500 messages in #general on the BetterGov server."
- "What has been discussed about taxes since 2026-11-01?"
- "Find the channel about tax and list its most recent threads."

`read_messages` returns messages in chronological order with `Oldest id` and `Newest id` in the footer, so the model can page further back by passing `before`.

Forum channels are read through their threads: call `list_threads` with the forum's `channel_id`, then `read_messages` with a thread id. Discord rejects `read_messages` on a forum channel id itself.

Protocol versions 2024-11-05, 2025-03-26, and 2025-06-18 are supported; any other requested version falls back to 2024-11-05.

## Environment

| Variable | Required | Meaning |
| --- | --- | --- |
| `DISCORD_TOKEN` | yes | Bot token from the developer portal. |
| `DISCORD_API_BASE` | no | Override for tests, e.g. `http://127.0.0.1:8787`. Default `https://discord.com/api/v10`. |

## What it cannot do

- **Post messages.** There is no send tool in this version.
- **Search Discord globally.** Discord does not expose message search to bots over the REST API.
- **Read forum channels directly.** Read their threads instead (see above).
- **Read channels the bot cannot see.** Permissions are enforced by Discord, not by this server.
- **Read DMs.** Not implemented.

## Security model

- Read-only tool surface; no write endpoints are called anywhere in `server.mjs`.
- The token is read from the environment once at startup and sent only to the Discord API base.
- Error messages contain HTTP status and response body from Discord, never the token.
- Rate limits (HTTP 429) are honoured using Discord's `retry_after`, with bounded retries.

## Development

```bash
node --test tests/server.test.mjs
```

The suite spawns the server, speaks JSON-RPC to it, and points it at a local mock of the Discord API. It needs no token and no network access.

## Publishing (maintainer)

The name `discord-mcp-lite` was unclaimed on npm as of 2026-11-19. To publish:

```bash
npm publish --dry-run
npm publish
```

## License

MIT
