# 0x Order Types | 0x

0x Order Types | 0x




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

    - [Contracts](/docs/developer-resources/core-concepts/contracts)
    - [Order Types](/docs/developer-resources/core-concepts/order-types)
    - [Glossary](/docs/developer-resources/core-concepts/glossary)
    - [White Paper](/docs/developer-resources/core-concepts/white-paper)
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
* [Core Concepts](/docs/category/core-concepts)
* Order Types

# 0x Order Types

An order is a message passed into the 0x Settler to facilitate a trade (see [How does 0x work?](/docs/developer-resources/core-concepts/introduction-to-0x#how-does-0x-work)). The order types that we support include:

| **Order Type** | **Summary** | **Order Structure** | **Supported Token Trade Types** |
| --- | --- | --- | --- |
| Limit Orders | These are the standard 0x Order, which encodes a possible trade between a maker and taker at a fixed price. | [Limit Order Structure](/docs/0x-limit-orders/docs/limit-order-structure) | ERC20 <-> ERC20 trade |
| RFQ Orders | These are a stripped down version of standard limit orders, supporting fewer fields and a leaner settlement process. These orders are fielded just-in-time, directly from market makers, during the construction of a swap quote on 0x API, and can be filled through the `fillRfqOrder()` function on the Exchange Proxy. | [RFQ Order Structure](https://docs.0xprotocol.org/en/latest/basics/orders.html#rfq-orders) | ERC20 <-> ERC20 trade |

[Previous

Contracts](/docs/developer-resources/core-concepts/contracts)[Next

Glossary](/docs/developer-resources/core-concepts/glossary)

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
[https://0x.org/docs/developer-resources/core-concepts/order-types#docusaurus_skipToContent_fallback](https://0x.org/docs/developer-resources/core-concepts/order-types#docusaurus_skipToContent_fallback)
