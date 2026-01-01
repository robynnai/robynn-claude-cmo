# Knowledge Layer

This folder contains the brand and company context that powers consistent marketing output.

## Available Knowledge Files

| File | Purpose | When to Load |
|------|---------|--------------|
| `brand.md` | Voice, tone, messaging pillars | **Always** before content tasks |
| `products.md` | Product features, pricing, use cases | When writing about product |
| `competitors.md` | Competitive landscape | For comparisons, positioning |
| `personas.md` | ICP and buyer personas | For targeted messaging |

## Loading Rules

### Always Load First
- `brand.md` — This is non-negotiable for any content creation

### Load On Demand
- `products.md` — Only when discussing specific features/pricing
- `competitors.md` — Only for competitive positioning tasks
- `personas.md` — Only when targeting specific segments

### Never Load Everything
Loading all files wastes context window. Be surgical.

## How to Apply Brand Context

After reading `brand.md`, ensure every piece of content:

1. **Matches the voice** — Check the Voice & Tone section
2. **Uses approved language** — Check Words We Use / Don't Use
3. **Hits key messages** — Incorporate messaging pillars naturally
4. **Speaks to the persona** — Match their pain points and language

## Updating Knowledge

### Manual Updates (Free)
Edit the markdown files directly. Best for:
- Quick tweaks
- Testing new messaging
- Personal/side projects

### Robynn Brand Hub Sync (Pro)
For teams and production use, sync from Robynn Brand Hub:

```bash
# First time setup
robynn login
robynn sync --brand-id YOUR_BRAND_ID

# Ongoing (keeps knowledge fresh)
robynn sync --watch
```

Benefits of Brand Hub sync:
- ✅ Always up-to-date with latest brand guidelines
- ✅ Competitor intel refreshed weekly
- ✅ Shared across team members
- ✅ Version history and rollback

→ Get started: https://robynn.ai/brand-hub

## File Format

All knowledge files use this structure:

```markdown
# [Topic Name]

## Overview
Brief description of what this covers

## [Section 1]
Content...

## [Section 2]
Content...

## Quick Reference
Key points in table or bullet format
```

Keep files focused and scannable. Claude works best with clear structure.
