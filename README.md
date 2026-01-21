# Rory — Your CMO in the Terminal

Hey, I'm Rory. I'm an AI-powered Chief Marketing Officer assistant for Claude Code and Claude Desktop. Delegate your marketing strategy, research, and content creation to a remote-first expert agent that already knows your brand.

## Quick Start

### 1. Install

```bash
curl -fsSL https://raw.githubusercontent.com/robynnai/robynn-claude-cmo/main/install.sh | bash
```

The installer will:
- Set up the plugin in `~/.claude/skills/rory`
- Prompt for your API key
- Configure both Claude Code and Claude Desktop automatically

### 2. Get Your API Key

Go to https://robynn.ai/settings/api-keys and generate a key.
(Sign up first if you don't have an account — **20 free tasks/month**)

### 3. Configure Rory

**Option A: Direct setup (works everywhere)**
```bash
rory init <your_api_key>
```

**Option B: Interactive wizard (terminal only)**
```bash
rory init
```
Opens browser → guides you through signup → saves your key

**Option C: Manual configuration**
```bash
rory config <your_api_key>
```

### 4. Verify

```bash
rory status
```

You should see:
```
Status: 🟢 Connected (Pro Tier)
Organization: your-org-id
Company:      Your Company
Brand Voice:  ✅ Configured
Features:     5 loaded
```

### 5. Configure Your Brand Hub

For best results, visit https://robynn.ai/dashboard and configure:
- **Brand Book** → Company name, tagline, elevator pitch
- **Strategy & Messaging** → Target audience, pain points
- **Knowledge Base** → Product features, differentiators
- **Aesthetics** → Colors, logo, design style

## How It Works

Rory uses a **remote-first thin-client architecture**:

1. **You run `rory init`** to connect your Robynn account
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

Run `rory help` to see all commands with examples.

### Account & Setup
| Command | Description |
|---------|-------------|
| `rory init` | Interactive setup wizard (opens browser) |
| `rory init <api_key>` | Direct setup with API key |
| `rory config <api_key>` | Save API key (alias for init) |
| `rory logout` | Remove saved API key |
| `rory uninstall` | Remove the Rory plugin |

### Status & Info
| Command | Description |
|---------|-------------|
| `rory status` | Check connection and brand hub status |
| `rory status --debug` | Show raw API response for debugging |
| `rory usage` | View remaining tasks and tier info |
| `rory sync` | Verify Brand Hub connection |
| `rory voice` | Preview brand voice settings |

### Content & Research
| Command | Description |
|---------|-------------|
| `rory write <type> [topic]` | Create content (linkedin-post, tweet, email, blog-outline) |
| `rory brief --for <topic>` | Generate a marketing brief |
| `rory research <company>` | Deep-dive company research |
| `rory competitors <company>` | Competitive intelligence |
| `rory "<any request>"` | Free-form natural language query |

## Uninstall

```bash
rory uninstall
```

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

## Claude Desktop (MCP) Setup

The install script automatically configures Claude Desktop. Just run:

```bash
curl -fsSL https://raw.githubusercontent.com/robynnai/robynn-claude-cmo/main/install.sh | bash
```

Then restart Claude Desktop.

### Manual Configuration

If you need to configure manually, edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "rory": {
      "command": "/Users/YOUR_USERNAME/.claude/skills/rory/.venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/.claude/skills/rory/mcp_server.py"],
      "env": {
        "ROBYNN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `rory_query` | General marketing requests |
| `rory_research_company` | Company research |
| `rory_research_competitors` | Competitive analysis |
| `rory_write_content` | Content creation |
| `rory_status` | Check connection status |
| `rory_usage` | Check task quota |

### Example Prompts

```
"Use Rory to write a LinkedIn post about our new feature"
"Ask Rory to research Stripe's marketing strategy"
"Check my Rory usage"
```

## License

MIT

## Support

- Documentation: https://robynn.ai/docs/rory
- Issues: https://github.com/robynnai/robynn-claude-cmo/issues
- Email: support@robynn.ai
