# Rate Limits | 0x

Rate Limits | 0x




[Skip to main content](#docusaurus_skipToContent_fallback)

[![0x Docs](/docs/img/0x-logo.png)](/docs/)[Docs](/docs/introduction/welcome)[API Reference](/docs/api)[Changelog](/docs/changelog/)

[Careers](https://0x.org/careers#open-positions)[Dashboard](https://dashboard.0x.org/)

* [Introduction](/docs/category/introduction)

  + [Welcome](/docs/introduction/welcome)
  + [Get Started](/docs/introduction/getting-started)
  + [What is 0x?](/docs/introduction/introduction-to-0x)
  + [Learning Resources](/docs/introduction/guides)
  + [0x Cheat Sheet](/docs/introduction/0x-cheat-sheet)
  + [Support](/docs/introduction/community)
  + [Issues & Error Codes](/docs/introduction/api-issues)
  + [FAQ & Troubleshooting](/docs/developer-resources/faqs-and-troubleshooting)
* [Swap API](/docs/category/swap-api)
* [Gasless API](/docs/category/gasless-api)
* [Trade Analytics API](/docs/category/trade-analytics-api)
* [AI Tools](/docs/category/ai-tools)
* [Libraries](/docs/category/libraries)
* [Developer Resources](/docs/category/developer-resources)

  + [Core Concepts](/docs/category/core-concepts)
  + [0x Cheat Sheet](/docs/introduction/0x-cheat-sheet)
  + [Supported Chains](/docs/developer-resources/supported-chains)
  + [Issues & Error Codes](/docs/introduction/api-issues)
  + [FAQ & Troubleshooting](/docs/developer-resources/faqs-and-troubleshooting)
  + [Access 0x Transaction Data](/docs/developer-resources/transaction-data)
  + [Buy/Sell Tax Support](/docs/developer-resources/buy-sell-tax-support)
  + [Bounties](/docs/developer-resources/bounties)
  + [Rate Limits](/docs/developer-resources/rate-limits)
  + [System Status](https://status.0x.org/)
* [Example Projects](https://github.com/0xProject/0x-examples)
* [Upgrading](/docs/upgrading)
* [Liquidity Providers](/docs/category/liquidity-providers)
* [Need Help?](/docs/category/need-help)

* [Developer Resources](/docs/category/developer-resources)
* Rate Limits

On this page

# Rate Limits

info

Want higher rate limits? Check out our [available options](https://0x.org/pricing)

## Why do we have rate limits?[​](#why-do-we-have-rate-limits "Direct link to Why do we have rate limits?")

Rate limiting is used by the API to prevent abuse and ensure a reliable experience for all consumers.

## What are the rate limits for the 0x APIs?[​](#what-are-the-rate-limits-for-the-0x-apis "Direct link to What are the rate limits for the 0x APIs?")

The current limit for the Free Tier of our APIs is approximately 10 Requests Per Second (RPS). If you need higher rate limits, contact us on our [pricing page](https://0x.org/pricing) to learn about our custom plans.

## How are rates calculated?[​](#how-are-rates-calculated "Direct link to How are rates calculated?")

The following is shared to help your team to maximize your app setup. The example below uses the 10 RPS Free Tier limit; however, the same logic applies to all tiers.

* The 10 RPS is 10 calls per chain (aka per [endpoint](/docs/introduction/0x-cheat-sheet#swap-api-endpoints))
* The 10 RPS is per fixed 1 second window; in other words, the API has fixed 1 second windows and will allow 10 calls per chain any where within that 1 second window
* You can view your current usage and limits on the [0x API Dashboard](https://dashboard.0x.org/login).

[Previous

Bounties](/docs/developer-resources/bounties)[Next

Upgrading to 0x API v2](/docs/upgrading)

* [Why do we have rate limits?](#why-do-we-have-rate-limits)
* [What are the rate limits for the 0x APIs?](#what-are-the-rate-limits-for-the-0x-apis)
* [How are rates calculated?](#how-are-rates-calculated)

APIs

* [Swap API](/docs/category/swap-api)
* [Gasless API](/docs/category/gasless-api)

Developers

* [Login/Sign Up](https://dashboard.0x.org/)
* [Content Hub](https://www.0x.org/content-hub)
* [FAQs & Troubleshooting](/docs/developer-resources/faqs-and-troubleshooting)
* [0x System Status](https://status.0x.org/)
* [Sepolia Faucet](https://sepoliafaucet.com/)
* [Gwei Calculator](https://www.alchemy.com/gwei-calculator)

Community

* [Twitter](https://twitter.com/0xproject)

Copyright © 2025

---

## Reference
[https://0x.org/docs/developer-resources/rate-limits#docusaurus_skipToContent_fallback](https://0x.org/docs/developer-resources/rate-limits#docusaurus_skipToContent_fallback)
