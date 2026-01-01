---
name: ads-manager
description: Advertising campaign manager for Google Ads and LinkedIn Ads. Use when user asks about ad campaigns, ad performance, ROAS, CPC, impressions, or wants to create/manage advertising campaigns. Has safety rails to prevent accidental spend.
---

# Ads Agent

Paid advertising management with built-in safety rails.

## Platforms

| Platform | Status | Capabilities |
|----------|--------|--------------|
| Google Ads | ✅ Active | Campaigns, ad groups, keywords, GAQL queries |
| LinkedIn Ads | ✅ Active | B2B campaigns, targeting, analytics |

## ⚠️ Safety Features (CRITICAL)

1. **Draft-Only Creation**: All campaigns created in PAUSED/DRAFT mode
2. **Budget Limits**: Configurable in `tools/ads_config.yaml` (default: $0)
3. **Confirmation Required**: Destructive actions require `--confirm` flag
4. **Audit Logging**: All operations logged to `ads_audit.log`

## Tool Commands

```bash
# Check credentials status
python tools/ads_unified.py status

# Google Ads
python tools/google_ads.py accounts
python tools/google_ads.py campaigns --customer-id 1234567890
python tools/google_ads.py performance --customer-id 1234567890 --days 30
python tools/google_ads.py create --customer-id 1234567890 --name "Campaign" --budget 0 --confirm

# LinkedIn Ads
python tools/linkedin_ads.py accounts
python tools/linkedin_ads.py campaigns --account-id 123456789
python tools/linkedin_ads.py analytics --campaign-id 123456 --days 30
python tools/linkedin_ads.py create --account-id 123456789 --name "Campaign" --budget 0 --confirm

# Cross-platform
python tools/ads_unified.py summary
python tools/ads_unified.py compare --days 30
```

## Workflow

1. **Load ads agent**: Read `agents/ads/SKILL.md`
2. **Identify operation type**:
   - Analytics → Query performance data
   - Creation → Create in DRAFT mode (⚠️ never ACTIVE)
   - Management → Update existing campaigns
3. **Safety checks**:
   - [ ] Budget within limits?
   - [ ] Creating in DRAFT/PAUSED status?
   - [ ] Destructive action → confirmation required?
4. **Execute and report**:
   - Show metrics with date ranges
   - For new campaigns: remind user to review in platform UI

## Platform Playbooks

- Google Ads: `agents/ads/google-ads.md`
- LinkedIn Ads: `agents/ads/linkedin-ads.md`
