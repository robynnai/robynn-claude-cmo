# Robynn CMO Agent

AI-powered Chief Marketing Officer assistant for Claude Code. Create content, research companies, find contacts, and manage advertising campaigns with built-in safety rails.

## Installation

### Option 1: Install as Claude Code Plugin (Recommended)

```bash
# Add the Robynn marketplace
/plugin marketplace add robynnai/robynn-claude-cmo

# Install the plugin
/plugin install robynn-cmo@robynn-plugins
```

Or install directly from GitHub:

```bash
# Install from GitHub repo
claude plugin install --source github robynnai/robynn-claude-cmo/cmo-agent
```

### Option 2: Install as User Skill (Personal)

Copy to your personal skills directory:

```bash
# Clone the repo
git clone https://github.com/robynnai/robynn-claude-cmo.git

# Copy to Claude Code skills directory
cp -r robynn-claude-cmo/cmo-agent ~/.claude/skills/cmo-agent
```

### Option 3: Install as Project Skill (Team)

Add to your project's `.claude/skills/` directory:

```bash
# In your project root
mkdir -p .claude/skills
cp -r /path/to/robynn-claude-cmo/cmo-agent .claude/skills/cmo-agent
```

## Setup

1. **Install Python dependencies:**
   ```bash
   cd ~/.claude/skills/cmo-agent  # or your installation path
   pip install -r requirements.txt
   ```

2. **Configure API keys:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Verify installation:**
   ```bash
   python tools/ads_unified.py status
   ```

## Features

### Content Agent
- LinkedIn posts, tweets, blog outlines
- Cold emails, one-pagers
- Brand-consistent content with templates

### Research Agent
| Capability | Tools |
|------------|-------|
| Company Research | Clearbit, Apollo, Firecrawl |
| Competitive Intel | G2, Capterra, web scraping |
| People Finding | Apollo, Proxycurl (LinkedIn) |
| Tech Detection | BuiltWith |

### Ads Agent
| Platform | Capabilities |
|----------|--------------|
| Google Ads | Campaigns, ad groups, keywords, GAQL |
| LinkedIn Ads | B2B campaigns, targeting, analytics |

**Safety Features:**
- All campaigns created in DRAFT/PAUSED mode
- Configurable budget limits (default: $0)
- Confirmation required for spending
- Full audit logging

## Usage Examples

Once installed, just ask Claude:

```
"Write a LinkedIn post about our new AI feature"
"Research Stripe and find their marketing team contacts"
"Show me our Google Ads performance for the last 30 days"
"Create a competitive analysis of HubSpot vs Salesforce"
```

## API Keys Required

| Tool | Purpose | Free Tier |
|------|---------|-----------|
| Firecrawl | Web scraping | ✅ 500 credits/mo |
| Apollo | Contact data | ✅ 10k credits |
| Proxycurl | LinkedIn profiles | ✅ 10 credits |
| Clearbit | Company enrichment | ❌ Paid |
| BuiltWith | Tech detection | ✅ Fallback |
| Google Ads | Ad management | ✅ API is free |
| LinkedIn Ads | Ad management | ✅ API is free |

## Tool Reference

### Research Tools

```bash
# Web scraping
python tools/firecrawl.py scrape https://example.com

# Company data
python tools/clearbit.py company stripe.com
python tools/apollo.py company stripe.com

# Contact finding
python tools/apollo.py people --company Stripe --titles "VP Marketing"
python tools/proxycurl.py person "https://linkedin.com/in/username"

# Tech stack
python tools/builtwith.py lookup stripe.com
```

### Ads Tools

```bash
# Check credentials
python tools/ads_unified.py status

# Google Ads
python tools/google_ads.py accounts
python tools/google_ads.py campaigns --customer-id 1234567890
python tools/google_ads.py performance --customer-id 1234567890 --days 30

# LinkedIn Ads
python tools/linkedin_ads.py accounts
python tools/linkedin_ads.py campaigns --account-id 123456789
python tools/linkedin_ads.py analytics --campaign-id 123456 --days 30

# Cross-platform
python tools/ads_unified.py summary
python tools/ads_unified.py compare --days 30
```

## Testing

```bash
# Run all tests
cd cmo-agent
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=tools --cov-report=term-missing
```

## Project Structure

```
cmo-agent/
├── .claude-plugin/
│   ├── plugin.json          # Plugin manifest
│   └── marketplace.json     # Marketplace config
├── skills/                   # Claude Code skills
│   ├── cmo/SKILL.md         # Main orchestrator
│   ├── content/SKILL.md     # Content creation
│   ├── research/SKILL.md    # Market research
│   └── ads/SKILL.md         # Advertising
├── agents/                   # Agent playbooks
│   ├── content/             # Content templates
│   ├── research/            # Research workflows
│   └── ads/                 # Platform guides
├── tools/                    # Python API clients
│   ├── apollo.py            # Contact data
│   ├── firecrawl.py         # Web scraping
│   ├── google_ads.py        # Google Ads API
│   ├── linkedin_ads.py      # LinkedIn Ads API
│   └── ...
├── knowledge/               # Brand context
├── tests/                   # Test suite (136+ tests)
└── .env.example            # API key template
```

## License

MIT

## Contributing

Issues and PRs welcome at [github.com/robynnai/robynn-claude-cmo](https://github.com/robynnai/robynn-claude-cmo)
