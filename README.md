# Rory — Your CMO in the Terminal

Hey, I'm Rory. I'm an AI-powered Chief Marketing Officer assistant for Claude Code. Delegate your marketing strategy, research, and content creation to a remote-first expert agent that already knows your brand.

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/robynnai/robynn-claude-cmo/main/install.sh | bash
```

Then configure your API key:
```bash
cd ~/.claude/skills/rory
# Edit .env and add your ROBYNN_API_KEY
# Get your key at https://robynn.ai/settings/api-keys
```

## Alternative Installation Methods

### Option 1: Manual Clone

```bash
# Clone the repo
git clone https://github.com/robynnai/robynn-claude-cmo.git ~/.claude/skills/rory

# Install dependencies
cd ~/.claude/skills/rory
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your ROBYNN_API_KEY
```

### Option 2: Claude Code Plugin Marketplace (Coming Soon)

```bash
# Add the Robynn marketplace
/plugin marketplace add robynnai/robynn-claude-cmo

# Install Rory
/plugin install rory@robynn-plugins
```

## Verify Installation

```bash
cd ~/.claude/skills/rory
.venv/bin/python tools/robynn.py status
```

## Features (Free & Pro)

### 🚀 Founder Essentials (Free)
- **Landing Page Roast**: Get a conversion audit and copy rewrite for your URL.
- **GTM Sprint**: Generate a tactical 7-day action plan to find your first 100 users.
- **Viral Social Hooks**: Turn your technical updates/git diffs into engaging LinkedIn posts.
- **Competitive Blindspots**: Identify exactly where your competitors are failing in their messaging.

### 📈 Marketing Operations
- **Content Creation**: High-quality LinkedIn posts, blogs, and cold emails.
- **Market Research**: Deep-dive company research and contact finding (Apollo integration).
- **Ads Management**: Performance analysis and draft campaign creation for Google & LinkedIn.

## Usage Examples

Once installed, just ask Claude:

```
"Roast our landing page at https://my-startup.com"
"Write a LinkedIn post about our new AI feature"
"Research Stripe and find their marketing team contacts"
"Show me our Google Ads performance for the last 30 days"
```

## How It Works

Rory uses a **"Thin Client"** architecture. While the local plugin provides the interface, the complex reasoning, system prompts, and tool integrations (Apollo, Clearbit, Firecrawl, etc.) are handled by Robynn's remote infrastructure.

- **Free Tier**: Anonymous, rate-limited access with generic marketing context.
- **Pro Tier**: Connect your Robynn account (`rory config <key>`) to unlock your **Brand Hub** context, ensuring every response follows your specific brand voice and strategy.

## Project Structure

```
robynn-rory/
├── skills/                   # Claude Code skills (Thin Client)
│   ├── cmo/SKILL.md         # Main Rory orchestrator
│   ├── content/SKILL.md     # Content creation redirect
│   ├── research/SKILL.md    # Research redirect
│   └── ads/SKILL.md         # Advertising redirect
├── tools/                    # Python bridge tools
│   ├── remote_cmo.py        # Remote agent execution bridge
│   ├── robynn.py            # Platform connection management
│   └── ...
└── .env.example            # API key template
```

## License

MIT

## Contributing

Issues and PRs welcome at [github.com/robynnai/robynn-claude-cmo](https://github.com/robynnai/robynn-claude-cmo)
