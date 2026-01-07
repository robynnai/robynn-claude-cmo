# Rory — Your CMO in the Terminal

Hey, I'm Rory. I'm an AI-powered Chief Marketing Officer assistant for Claude Code. Delegate your marketing strategy, research, and content creation to a remote-first expert agent that already knows your brand.

## Installation

### Option 1: Install as Claude Code Plugin (Recommended)

```bash
# Add the Robynn marketplace
/plugin marketplace add robynnai/robynn-claude-cmo

# Install Rory
/plugin install rory@robynn-plugins
```

### Option 2: Install as User Skill (Personal)

```bash
# Clone the repo
git clone https://github.com/robynnai/robynn-claude-cmo.git

# Copy to Claude Code skills directory
cp -r robynn-claude-cmo ~/.claude/skills/rory
```

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Robynn API Key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ROBYNN_API_KEY
   # Get your key at https://app.robynn.ai/settings/api-keys
   ```

3. **Verify connection:**
   ```bash
   rory status
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
