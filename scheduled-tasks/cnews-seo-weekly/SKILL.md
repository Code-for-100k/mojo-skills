---
name: cnews-seo-weekly
description: Weekly SEO audit for cnews.dev — crawl errors, indexing, technical checks
---

You are the SEO audit agent for cnews.dev (Canton Network news site). Run a weekly SEO health check.

## 1. Technical Health Check
- curl https://cnews.dev and verify HTTP 200
- curl https://cnews.dev/sitemap.xml and count total URLs
- curl https://cnews.dev/robots.txt and verify sitemap directive points to cnews.dev
- Check 5 random pages from the sitemap for HTTP 200 status
- Verify canonical tags point to cnews.dev (not Railway URL)
- Verify JSON-LD structured data is present on homepage

## 2. Check for Broken Pages
- Test key pages: /, /learn, /ecosystem, /validators, /convert/cc-to-usd, /prices/canton-coin
- Flag any 404s or 500s

## 3. Performance Check
- Measure TTFB for homepage and 2 subpages
- Check cache headers (should have s-maxage)

## 4. Content Freshness
- Check if any new pages were added since last audit
- Count total pages in sitemap vs last week

## 5. Report
Write a concise report with:
- ✅ What's healthy
- ⚠️ Warnings
- ❌ Critical issues needing immediate fix

If critical issues are found, fix them if possible (update code, redeploy via /tmp/railway CLI).

Project path: /Users/mayank/Desktop/_CNews/cnews-cc
Railway CLI: /tmp/railway (may need re-download if expired)
Cloudflare Zone ID: b892a31822ad65e4e0a9e8cb9da3f744
Cloudflare DNS Token: $CLOUDFLARE_DNS_TOKEN  # stored in 1Password / Vaultwarden