# Rory — Your CMO in the Terminal

Hey, I'm Rory. I'm an AI-powered Chief Marketing Officer assistant for Claude Code. Delegate your marketing strategy, research, and content creation to a remote-first expert agent that already knows your brand.

## Quick Start

### 1. Sign Up for Robynn
Go to https://robynn.ai and create an account. You get **20 free tasks per month**.

### 2. Configure Your Brand Hub
Navigate to **Settings → Brand Hub** and add:
- Company name and description
- Product features and differentiators
- Brand voice and tone
- Color palette

### 3. Get Your API Key
Go to **Settings → API Keys** and generate a key.

### 4. Install the Plugin

```bash
curl -fsSL https://raw.githubusercontent.com/robynnai/robynn-claude-cmo/main/install.sh | bash
```

### 5. Configure Rory

```bash
cd ~/.claude/skills/rory
echo "ROBYNN_API_KEY=your_key_here" >> .env
```

### 6. Verify

```bash
.venv/bin/python tools/robynn.py status
```

You should see:
```
✅ Brand Hub connected
   Company: Your Company
   Features: X loaded
   Voice: ✅ Configured
```

## How It Works

Rory uses a **remote-first thin-client architecture**:

1. **You configure your brand** in the Robynn web app (Brand Hub)
2. **You ask Rory** to create content, do research, or manage ads
3. **Rory sends your request** to the Robynn CMO v2 agent
4. **The agent fetches YOUR brand context** automatically
5. **Results come back already on-brand**

**No local brand files.** Your brand context lives in the cloud and is always up-to-date.

## Features

### Content Creation
- LinkedIn posts, tweets, blog outlines
- Cold emails, one-pagers
- All content uses YOUR voice from Brand Hub

### Research
- Company deep-dives
- Competitive intelligence
- People finding (Apollo, Proxycurl)
- Market research

### Ads Management
- Google Ads performance and campaigns
- LinkedIn Ads targeting and analytics
- All campaigns created in DRAFT mode (never auto-activated)

## Usage Examples

Just ask Claude:

```
"Write a LinkedIn post about our new AI feature"
"Roast our landing page at https://my-startup.com"
"Research Stripe and find their marketing team contacts"
"Show me our Google Ads performance for the last 30 days"
```

## Pricing

| Tier | Limit | Price |
|------|-------|-------|
| Free | 20 tasks/month | $0 |
| Pro | 500 tasks/day | See robynn.ai/pricing |

## Commands

| Command | What it does |
|---------|--------------|
| `rory config <key>` | Connect to your Robynn workspace |
| `rory status` | Check connection and Brand Hub |
| `rory usage` | See usage stats |

## Alternative Installation

### Manual Clone

```bash
git clone https://github.com/robynnai/robynn-claude-cmo.git ~/.claude/skills/rory
cd ~/.claude/skills/rory
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ROBYNN_API_KEY
```

## License

MIT

## Support

- Documentation: https://robynn.ai/docs/rory
- Issues: https://github.com/robynnai/robynn-claude-cmo/issues
- Email: support@robynn.ai
