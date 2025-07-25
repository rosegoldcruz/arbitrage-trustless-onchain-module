# Access 0x Transaction Data | 0x

Access 0x Transaction Data | 0x




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
* Access 0x Transaction Data

On this page

# Access 0x Transaction Data

This guide covers two main approaches for accessing trade data from 0x: Trade Analytics API for historical analysis and 0x-parser for real-time transaction parsing.

## Quick Comparison[​](#quick-comparison "Direct link to Quick Comparison")

| Feature | Trade Analytics API | 0x-parser |
| --- | --- | --- |
| Use Case | Historical analysis & business intelligence | Real-time transaction parsing |
| Data Freshness | ~15 min updates, final after 48 hours | Immediate (on-chain) |
| Data Scope | Comprehensive (volumes, fees, slippage, USD values) | Transaction-specific swap amounts |
| Implementation | REST API calls | JavaScript library |
| Reliability | After 48-hour finalization | Direct blockchain data |

## Trade Analytics API[​](#trade-analytics-api "Direct link to Trade Analytics API")

Best for historical analysis and business intelligence. Provides comprehensive trade data including volumes, fees, and USD values.

### Key Points[​](#key-points "Direct link to Key Points")

* Updates every ~15 minutes
* Data finalized after 48 hours
* Includes USD value estimates

[Read more about the Trade Analytics API](https://0x.org/docs/trade-analytics-api/introduction).

## 0x-parser[​](#0x-parser "Direct link to 0x-parser")

Best for real-time transaction data and displaying final swap amounts immediately after settlement.

### Key Points[​](#key-points-1 "Direct link to Key Points")

* Real-time parsing of on-chain data
* Handles AMM slippage calculations
* Available as npm package: [`@0x/0x-parser`](https://www.npmjs.com/package/@0x/0x-parser)

[Read more about the 0x-parser](https://0x.org/docs/0x-swap-api/advanced-topics/0x-parser).

[Previous

FAQ & Troubleshooting](/docs/developer-resources/faqs-and-troubleshooting)[Next

Buy/Sell Tax Support](/docs/developer-resources/buy-sell-tax-support)

* [Quick Comparison](#quick-comparison)
* [Trade Analytics API](#trade-analytics-api)
  + [Key Points](#key-points)
* [0x-parser](#0x-parser)
  + [Key Points](#key-points-1)

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
[https://0x.org/docs/developer-resources/transaction-data#docusaurus_skipToContent_fallback](https://0x.org/docs/developer-resources/transaction-data#docusaurus_skipToContent_fallback)
