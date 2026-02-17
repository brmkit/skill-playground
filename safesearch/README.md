# skill-playground

# safesearch

A Docker-based web search tool for Claude Code. Searches using Lite DuckDuckGo from an ephemeral container and screens results for prompt injection before presenting them.

Simply use it when you do not fully trust links or resources.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)

## Installation

Download the zip file and extract it to your `.claude/skills/` directory.

The `/safesearch` skill auto-registers via `.claude/skills/` — no additional setup needed.

## Usage

Inside Claude Code, run:

```
/safesearch your search query here
```

The first invocation builds the Docker image (cached for subsequent runs), then returns formatted search results.

## How It Works

```
/safesearch query
        │
        ▼
┌─ Docker Container ──────────────────────┐
│  search.sh                              │
│    ├─ curl lite.duckduckgo.com          │
│    └─ pipe HTML to parse_results.py     │
│         └─ extract title, URL, snippet  │
└─────────────────────────────────────────┘
        │
        ▼
  Regex pre-filter (flags suspicious patterns)
        │
        ▼
  Haiku classifier (CLEAN / SUSPICIOUS / BLOCKED)
        │
        ▼
  Sanitized results presented to user
```

## Security

Results pass through two layers of prompt-injection screening:

1. **Regex pre-filter** — `parse_results.py` flags patterns like role hijacking, instruction overrides, encoded payloads, and jailbreak phrases with `[⚠ FLAGGED: ...]` markers
2. **Haiku classifier** — A Claude Haiku subagent reviews flagged results and returns a verdict (CLEAN, SUSPICIOUS, or BLOCKED), stripping or redacting injected content

The Docker container uses default bridge networking (no `--network host`), preventing access to host localhost services.

## Customization

- **Result count**: Change the `15` in `parse_results.py` (line ~182) to return more or fewer results
- **Bot detection strings**: Update the checks in `search.sh` if DuckDuckGo changes their CAPTCHA markup
- **Injection patterns**: Add or modify regex patterns in `docker/injection_patterns.py` — changes take effect after rebuilding the Docker image with `docker build -t safesearch docker/`
- **Search engine**: To use a different search backend, modify the URL and POST parameters in `docker/search.sh`

## License

[MIT](LICENSE)
