#!/usr/bin/env node
// discord-mcp-lite — a read-only Discord MCP server with no dependencies.
// Speaks JSON-RPC 2.0 over stdio (MCP 2024-11-05 / 2025-06-18 core subset).
import { createInterface } from 'node:readline';

const NAME = 'discord-mcp-lite';
const VERSION = '0.1.0';
const API = (process.env.DISCORD_API_BASE || 'https://discord.com/api/v10').replace(/\/+$/, '');
const TOKEN = process.env.DISCORD_TOKEN || '';
const MAX_MESSAGES_PER_CALL = 1000;
const OUTPUT_LIMIT = 100_000;
const RETRY_AFTER_CAP_MS = 60_000;
const FETCH_TIMEOUT_MS = 30_000;
const DISCORD_EPOCH = 1420070400000n;
const SUPPORTED_PROTOCOLS = new Set(['2024-11-05', '2025-03-26', '2025-06-18']);

const CHANNEL_TYPES = {
  0: 'text',
  2: 'voice',
  4: 'category',
  5: 'announcement',
  10: 'announcement-thread',
  11: 'public-thread',
  12: 'private-thread',
  13: 'stage',
  15: 'forum',
  16: 'media',
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const log = (...args) => process.stderr.write(args.join(' ') + '\n');

function snowflakeFrom(value, label) {
  const s = String(value).trim();
  if (/^\d{1,20}$/.test(s)) return s;
  const ms = Date.parse(s);
  if (Number.isNaN(ms)) {
    throw new Error(`${label} must be a Discord message id or an ISO 8601 date, got "${s}"`);
  }
  return ((BigInt(ms) - DISCORD_EPOCH) << 22n).toString();
}

function timestampOf(id) {
  try {
    const ms = Number((BigInt(id) >> 22n) + DISCORD_EPOCH);
    return new Date(ms).toISOString().replace('T', ' ').replace(/\.\d{3}Z$/, ' UTC');
  } catch {
    return 'unknown-time';
  }
}

async function discordFetch(pathname, params = {}) {
  if (!TOKEN) {
    throw new Error('DISCORD_TOKEN is not set. Put the bot token in the MCP server env (see README).');
  }
  const url = new URL(API + pathname);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, String(v));
  }
  const MAX_ATTEMPTS = 6;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    const res = await fetch(url, {
      headers: { Authorization: `Bot ${TOKEN}`, 'User-Agent': `${NAME}/${VERSION}` },
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });
    if (res.status === 429) {
      const body = await res.json().catch(() => ({}));
      const waitMs = Math.min(Math.ceil(Number(body.retry_after ?? 1) * 1000) + 100, RETRY_AFTER_CAP_MS);
      log(`rate limited on ${pathname}; retrying in ${waitMs}ms`);
      await sleep(waitMs);
      continue;
    }
    if (res.status >= 500 && attempt < MAX_ATTEMPTS) {
      await sleep(300 * attempt);
      continue;
    }
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      const err = new Error(`Discord API ${res.status} for ${pathname}${text ? `: ${text.slice(0, 300)}` : ''}`);
      err.status = res.status;
      throw err;
    }
    return await res.json();
  }
  throw new Error(`Discord API retry limit exceeded for ${pathname}`);
}

function formatMessage(m) {
  const author = m.author?.global_name || m.author?.username || `id:${m.author?.id ?? '?'}`;
  let line = `[${timestampOf(m.id)}] ${author}: ${m.content ?? ''}`;
  if (Array.isArray(m.attachments) && m.attachments.length > 0) {
    line += ` [attachments: ${m.attachments.map((a) => `${a.filename} <${a.url}>`).join(', ')}]`;
  }
  return line;
}

function formatMessages(messages, channelId) {
  if (messages.length === 0) return `No messages found in channel ${channelId}.`;
  const ids = messages.map((m) => m.id);
  const oldest = ids.reduce((a, b) => (BigInt(b) < BigInt(a) ? b : a));
  const newest = ids.reduce((a, b) => (BigInt(b) > BigInt(a) ? b : a));
  const footer =
    `\n\nOldest id: ${oldest} | Newest id: ${newest}` +
    `\nTo page further back, call read_messages with before="${oldest}".`;
  const header = `# ${messages.length} message(s) from channel ${channelId}\n\n`;

  let block = messages.map(formatMessage).join('\n');
  let truncated = false;
  const budget = OUTPUT_LIMIT - header.length - footer.length - 32;
  if (block.length > budget) {
    const cut = block.lastIndexOf('\n', budget);
    block = block.slice(0, cut > 0 ? cut : budget);
    truncated = true;
  }
  return header + block + (truncated ? '\n[... output truncated]' : '') + footer;
}

async function readMessages(args) {
  const channelId = String(args.channel_id ?? '').trim();
  if (!channelId) throw new Error('channel_id is required');
  const max = Math.min(Math.max(Number(args.limit) || 100, 1), MAX_MESSAGES_PER_CALL);
  const sinceId = args.since ? snowflakeFrom(args.since, 'since') : null;
  let cursor = args.before ? snowflakeFrom(args.before, 'before') : null;

  const collected = [];
  while (collected.length < max) {
    const pageSize = Math.min(100, max - collected.length);
    const page = await discordFetch(`/channels/${encodeURIComponent(channelId)}/messages`, {
      limit: pageSize,
      before: cursor ?? undefined,
    });
    if (!Array.isArray(page) || page.length === 0) break;
    for (const m of page.slice(0, pageSize)) collected.push(m);
    cursor = page[page.length - 1].id;
    if (sinceId && BigInt(cursor) <= BigInt(sinceId)) break;
    if (page.length < pageSize) break;
    await sleep(250);
  }

  let messages = collected;
  if (sinceId) messages = messages.filter((m) => BigInt(m.id) > BigInt(sinceId));
  if (args.oldest_first !== false) messages = messages.slice().reverse();
  return formatMessages(messages, channelId);
}

async function listGuilds() {
  const guilds = await discordFetch('/guilds');
  if (!Array.isArray(guilds) || guilds.length === 0) {
    return 'The bot is not in any Discord servers. Invite it with the bot scope and View Channels permission.';
  }
  return guilds.map((g) => `${g.id}  ${g.name}`).join('\n');
}

function channelLine(c, categories) {
  const parent = c.parent_id ? categories.get(c.parent_id) : undefined;
  const type = CHANNEL_TYPES[c.type] ?? `type-${c.type}`;
  return `${c.id}  #${c.name}  (${type}${parent ? `, under ${parent}` : ''})`;
}

async function listChannels(args) {
  const guildId = String(args.guild_id ?? '').trim();
  if (!guildId) throw new Error('guild_id is required');
  const channels = await discordFetch(`/guilds/${encodeURIComponent(guildId)}/channels`);
  const categories = new Map(channels.filter((c) => c.type === 4).map((c) => [c.id, c.name]));
  const visible = channels.filter((c) => [0, 5, 15, 16].includes(c.type));
  if (visible.length === 0) return `No readable channels in guild ${guildId}.`;
  return visible.map((c) => channelLine(c, categories)).join('\n');
}

async function findChannel(args) {
  const query = String(args.query ?? '').trim().toLowerCase();
  if (!query) throw new Error('query is required');
  const guildId = args.guild_id ? String(args.guild_id).trim() : null;

  let guilds;
  if (guildId) {
    guilds = [{ id: guildId, name: '' }];
  } else {
    guilds = await discordFetch('/guilds');
  }

  const results = [];
  for (const guild of guilds) {
    let channels;
    try {
      channels = await discordFetch(`/guilds/${encodeURIComponent(guild.id)}/channels`);
    } catch (e) {
      // While scanning every guild, an inaccessible guild should not abort the
      // search; when the caller named a guild, every failure is theirs to see.
      if (!guildId && (e.status === 403 || e.status === 404)) {
        log(`skipping guild ${guild.id}: ${e.message}`);
        continue;
      }
      throw e;
    }
    const categories = new Map(channels.filter((c) => c.type === 4).map((c) => [c.id, c.name]));
    for (const c of channels) {
      if (!String(c.name ?? '').toLowerCase().includes(query)) continue;
      if (![0, 5, 15, 16].includes(c.type)) continue;
      const prefix = guildId ? '' : `[${guild.name}] `;
      results.push(`${prefix}${channelLine(c, categories)}`);
      if (results.length >= 50) break;
    }
    if (results.length >= 50) break;
    if (!guildId) await sleep(100);
  }
  if (results.length === 0) return `No readable channels match "${args.query}".`;
  return results.join('\n');
}

async function listThreads(args) {
  const guildId = String(args.guild_id ?? '').trim();
  if (!guildId) throw new Error('guild_id is required');
  const lines = [];

  const active = await discordFetch(`/guilds/${encodeURIComponent(guildId)}/threads/active`);
  for (const t of active.threads ?? []) {
    lines.push(`${t.id}  ${t.name}  (active, parent ${t.parent_id})`);
  }

  if (args.channel_id) {
    const channelId = String(args.channel_id).trim();
    const archived = await discordFetch(`/channels/${encodeURIComponent(channelId)}/threads/archived/public`, { limit: 100 });
    for (const t of archived.threads ?? []) {
      lines.push(`${t.id}  ${t.name}  (archived, parent ${t.parent_id})`);
    }
    if (archived.has_more) {
      lines.push('(more archived threads exist; the first 100 are shown)');
    }
  }

  if (lines.length === 0) return `No threads found in guild ${guildId}.`;
  return lines.join('\n');
}

const TOOLS = [
  {
    name: 'list_guilds',
    description: 'List the Discord servers (guilds) this bot can see. Start here when you do not know any ids.',
    annotations: { readOnlyHint: true },
    inputSchema: { type: 'object', properties: {}, additionalProperties: false },
  },
  {
    name: 'list_channels',
    description:
      'List readable text, announcement, forum, and media channels in a guild. Threads are not included; use list_threads.',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        guild_id: { type: 'string', description: 'Guild id from list_guilds.' },
      },
      required: ['guild_id'],
      additionalProperties: false,
    },
  },
  {
    name: 'find_channel',
    description: 'Find channels by name (case-insensitive substring). Searches every guild when guild_id is omitted.',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Part of a channel name, e.g. "tax".' },
        guild_id: { type: 'string', description: 'Optional: restrict the search to one guild.' },
      },
      required: ['query'],
      additionalProperties: false,
    },
  },
  {
    name: 'read_messages',
    description:
      'Read channel or thread messages, newest first by default. Paginates past 100 up to 1000 per call. ' +
      'Works on thread ids too; forum channels must be read through their threads (list_threads first). ' +
      'Read-only: this server cannot post.',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        channel_id: { type: 'string', description: 'Channel or thread id.' },
        limit: { type: 'integer', minimum: 1, maximum: 1000, description: 'How many messages to read, default 100.' },
        before: { type: 'string', description: 'Message id (or ISO date) to start before; use the oldest id from a previous call to page back.' },
        since: { type: 'string', description: 'ISO 8601 date; return only messages newer than this.' },
        oldest_first: { type: 'boolean', description: 'Return in chronological order, default true.' },
      },
      required: ['channel_id'],
      additionalProperties: false,
    },
  },
  {
    name: 'list_threads',
    description: 'List a guild\'s active threads, plus archived public threads when channel_id is given.',
    annotations: { readOnlyHint: true },
    inputSchema: {
      type: 'object',
      properties: {
        guild_id: { type: 'string', description: 'Guild id.' },
        channel_id: { type: 'string', description: 'Optional: also list archived public threads of this channel.' },
      },
      required: ['guild_id'],
      additionalProperties: false,
    },
  },
];

async function callTool(name, args) {
  switch (name) {
    case 'list_guilds':
      return listGuilds();
    case 'list_channels':
      return listChannels(args);
    case 'find_channel':
      return findChannel(args);
    case 'read_messages':
      return readMessages(args);
    case 'list_threads':
      return listThreads(args);
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

async function dispatch(method, params) {
  switch (method) {
    case 'initialize': {
      const requested = params.protocolVersion;
      return {
        protocolVersion: SUPPORTED_PROTOCOLS.has(requested) ? requested : '2024-11-05',
        capabilities: { tools: {} },
        serverInfo: { name: NAME, version: VERSION },
        instructions:
          'Read-only Discord access. Typical flow: list_guilds -> list_channels -> read_messages. ' +
          'Message bodies require the Message Content intent to be enabled in the Discord developer portal.',
      };
    }
    case 'ping':
      return {};
    case 'tools/list':
      return { tools: TOOLS };
    case 'tools/call': {
      const { name, arguments: args = {} } = params;
      if (!TOOLS.some((t) => t.name === name)) {
        throw Object.assign(new Error(`Unknown tool: ${name}`), { code: -32602 });
      }
      try {
        const text = await callTool(name, args);
        return { content: [{ type: 'text', text }] };
      } catch (e) {
        return { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true };
      }
    }
    default:
      throw Object.assign(new Error(`Method not found: ${method}`), { code: -32601 });
  }
}

function send(message) {
  process.stdout.write(JSON.stringify(message) + '\n');
}

async function handleLine(line) {
  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    send({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } });
    return;
  }
  if (!msg || typeof msg !== 'object' || Array.isArray(msg)) {
    send({ jsonrpc: '2.0', id: null, error: { code: -32600, message: 'Invalid Request' } });
    return;
  }
  if (msg.id === undefined || msg.id === null) return; // notification
  if (typeof msg.method !== 'string') {
    send({ jsonrpc: '2.0', id: msg.id, error: { code: -32600, message: 'Invalid Request' } });
    return;
  }
  try {
    const result = await dispatch(msg.method, msg.params ?? {});
    send({ jsonrpc: '2.0', id: msg.id, result });
  } catch (e) {
    send({ jsonrpc: '2.0', id: msg.id, error: { code: e.code ?? -32603, message: e.message } });
  }
}

const rl = createInterface({ input: process.stdin, crlfDelay: Infinity });
rl.on('line', (line) => {
  const trimmed = line.trim();
  if (trimmed) handleLine(trimmed).catch((e) => log('internal error:', e?.stack ?? e));
});
process.stdout.on('error', () => process.exit(0));
