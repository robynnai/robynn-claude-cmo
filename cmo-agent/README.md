# CMO Agent Research Tools

This directory contains Python tools for the Research Agent. Each tool wraps an external API or service to provide data gathering capabilities.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy and configure environment
cp ../.env.example ../.env
# Edit .env with your API keys

# 3. Test a tool
python firecrawl.py scrape https://example.com
```

## Tool Inventory

| Tool | Purpose | API Required | Free Tier |
|------|---------|--------------|-----------|
| `firecrawl.py` | Web scraping, screenshots | Firecrawl | ✅ 500 credits/mo |
| `apollo.py` | Contact & company data | Apollo | ✅ 10k credits |
| `proxycurl.py` | LinkedIn profiles | Proxycurl | ✅ 10 credits |
| `clearbit.py` | Company enrichment | Clearbit | ❌ Paid only |
| `crunchbase.py` | Funding data | Crunchbase | ❌ Paid only |
| `builtwith.py` | Tech stack detection | BuiltWith | ✅ Fallback |
| `reviews.py` | G2/Capterra reviews | None (scraping) | ✅ Free |
| `social.py` | Reddit/Twitter | Reddit API | ✅ Free |
| `research.py` | Unified research CLI | Uses above | Varies |

## Tool Details

### firecrawl.py - Web Scraping & Screenshots

```bash
# Scrape webpage to markdown
python firecrawl.py scrape https://example.com

# Take screenshot
python firecrawl.py screenshot https://example.com -o screenshot.png --full-page

# Crawl entire site
python firecrawl.py crawl https://example.com --max-pages 20

# Extract all links
python firecrawl.py links https://example.com
```

**Python Usage:**
```python
from tools.firecrawl import FirecrawlClient

client = FirecrawlClient()
result = client.scrape("https://example.com")
print(result["data"]["markdown"])
```

### apollo.py - Contact & Company Data

```bash
# Search for people
python apollo.py people --titles "VP Marketing" "CMO" --company Stripe --limit 10

# Enrich a contact
python apollo.py enrich --email john@example.com

# Get company data
python apollo.py company stripe.com --employees
```

**Python Usage:**
```python
from tools.apollo import ApolloClient

client = ApolloClient()
contacts = client.people_search(
    titles=["VP Marketing", "CMO"],
    company="Stripe",
    limit=10
)
```

### proxycurl.py - LinkedIn Data

```bash
# Get person profile
python proxycurl.py person "https://linkedin.com/in/username"

# Get profile summary (condensed)
python proxycurl.py person "https://linkedin.com/in/username" --summary

# Get company profile
python proxycurl.py company "https://linkedin.com/company/stripe"

# Lookup by email
python proxycurl.py lookup --email john@stripe.com
```

**Python Usage:**
```python
from tools.proxycurl import ProxycurlClient

client = ProxycurlClient()
profile = client.get_profile_summary("https://linkedin.com/in/username")
```

### clearbit.py - Company Enrichment

```bash
# Enrich company
python clearbit.py company stripe.com

# Get tech stack only
python clearbit.py company stripe.com --tech

# Get metrics only
python clearbit.py company stripe.com --metrics
```

**Python Usage:**
```python
from tools.clearbit import ClearbitClient

client = ClearbitClient()
company = client.enrich_company("stripe.com")
print(f"Employees: {company['metrics']['employees']}")
```

### reviews.py - G2 & Capterra Reviews

```bash
# Get G2 reviews
python reviews.py g2 hubspot-marketing

# Get G2 product info
python reviews.py g2 hubspot-marketing --info

# Get G2 alternatives
python reviews.py g2 hubspot-marketing --alternatives

# Compare on G2
python reviews.py g2 hubspot-marketing --compare salesforce-marketing-cloud

# Get Capterra reviews
python reviews.py capterra hubspot

# Get G2 category
python reviews.py category marketing-automation
```

**Python Usage:**
```python
from tools.reviews import ReviewScraper

scraper = ReviewScraper()
reviews = scraper.get_g2_reviews("hubspot-marketing")
comparison = scraper.compare_on_g2("hubspot-marketing", "salesforce-marketing-cloud")
```

### social.py - Reddit & Twitter

```bash
# Search Reddit
python social.py reddit "hubspot vs salesforce" --subreddit marketing

# Get subreddit posts
python social.py subreddit SaaS --sort hot --limit 25

# Get post comments
python social.py comments "https://reddit.com/r/SaaS/comments/..."

# Search Twitter (limited without API)
python social.py twitter "brand mention"
```

**Python Usage:**
```python
from tools.social import RedditClient

reddit = RedditClient()
results = reddit.search("hubspot problems", subreddit="SaaS", limit=20)
```

### builtwith.py - Technology Detection

```bash
# Lookup tech stack
python builtwith.py lookup stripe.com

# Quick detection (no API needed)
python builtwith.py lookup stripe.com --quick

# Compare tech stacks
python builtwith.py compare stripe.com paypal.com
```

**Python Usage:**
```python
from tools.builtwith import BuiltWithClient

client = BuiltWithClient()
tech = client.lookup("stripe.com")
comparison = client.compare_tech_stacks("stripe.com", "paypal.com")
```

### crunchbase.py - Funding Data

```bash
# Lookup company
python crunchbase.py lookup stripe

# Search companies
python crunchbase.py search "AI marketing" --limit 20
```

**Python Usage:**
```python
from tools.crunchbase import CrunchbaseClient

client = CrunchbaseClient()
company = client.lookup("stripe")
print(f"Total funding: {company['funding_total']}")
```

### research.py - Unified Research CLI

The main entry point that combines all tools for common research workflows.

```bash
# Company research
python research.py company notion.com --depth deep

# Competitor research
python research.py competitor hubspot --vs-us robynn.ai

# Find people
python research.py people --company Stripe --titles "VP Marketing" "CMO"

# Topic research
python research.py topic "AI marketing automation" --sources reddit g2
```

## Error Handling

All tools handle common errors gracefully:

```python
from tools.apollo import ApolloClient
from tools.base import has_credential

# Check if credentials exist before using
if has_credential("apollo"):
    client = ApolloClient()
    results = client.people_search(...)
else:
    print("Apollo API key not configured")
```

## Rate Limiting

Tools automatically handle rate limiting with exponential backoff:

- 429 responses trigger automatic retry with `Retry-After` header
- Server errors (5xx) retry up to 3 times
- Network errors retry with exponential backoff

## Adding New Tools

To add a new API integration:

1. Create `tools/new_tool.py`
2. Inherit from `BaseAPIClient`
3. Implement `_get_headers()` for authentication
4. Add CLI interface with `main()`

Example:
```python
from tools.base import BaseAPIClient, get_credential

class NewToolClient(BaseAPIClient):
    BASE_URL = "https://api.newtool.com/v1"
    
    def _get_headers(self):
        api_key = get_credential("newtool", "api_key")
        return {"Authorization": f"Bearer {api_key}"}
    
    def some_method(self, param):
        return self.get(f"/endpoint?param={param}")

def main():
    # CLI implementation
    pass

if __name__ == "__main__":
    main()
```

## Credential Management

Credentials are loaded from environment variables:

1. Check `TOOL_API_KEY` environment variable
2. Check `.env` file in project root
3. Try alternate formats: `TOOL_KEY`, `TOOL_TOKEN`

The `CredentialBroker` class in `base.py` handles all credential loading.

## Testing Tools

```bash
# Test Firecrawl
python -c "from tools.firecrawl import FirecrawlClient; c = FirecrawlClient(); print(c.scrape('https://example.com'))"

# Test Apollo (requires API key)
python -c "from tools.apollo import ApolloClient; c = ApolloClient(); print(c.people_search(titles=['CEO'], limit=1))"

# Test with has_credential check
python -c "from tools.base import has_credential; print('Apollo:', has_credential('apollo')); print('Firecrawl:', has_credential('firecrawl'))"
```
