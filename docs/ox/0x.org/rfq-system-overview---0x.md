# RFQ System Overview | 0x

RFQ System Overview | 0x




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

  + [Introduction](/docs/0x-swap-api/introduction)
  + [Guides](#)
  + [Advanced Topics](#)

    - [Set a Token Allowance](/docs/0x-swap-api/advanced-topics/how-to-set-your-token-allowances)
    - [Handling Native Tokens](/docs/0x-swap-api/advanced-topics/handling-native-tokens)
    - [Display Final Swapped Amount](/docs/0x-swap-api/advanced-topics/0x-parser)
    - [Sell Entire Balance](/docs/0x-swap-api/advanced-topics/sell-entire-balance)
    - [RFQ System Overview](/docs/0x-swap-api/advanced-topics/about-the-rfq-system)
  + [API Reference](https://0x.org/docs/api#tag/Swap)
* [Gasless API](/docs/category/gasless-api)
* [Trade Analytics API](/docs/category/trade-analytics-api)
* [AI Tools](/docs/category/ai-tools)
* [Libraries](/docs/category/libraries)
* [Developer Resources](/docs/category/developer-resources)
* [Example Projects](https://github.com/0xProject/0x-examples)
* [Upgrading](/docs/upgrading)
* [Liquidity Providers](/docs/category/liquidity-providers)
* [Need Help?](/docs/category/need-help)

* [Swap API](/docs/category/swap-api)
* Advanced Topics
* RFQ System Overview

On this page

# RFQ System Overview

info

This guide is for integrators who would like to **access** 0x RFQ liquidity, via the Swap API. If you represent a trading firm or professional market maker that would like to **supply** RFQ liquidity, please get in touch here: [0x RFQ Interest Form](https://docs.google.com/forms/d/e/1FAIpQLSen019JsWFZHluSgqSaPE_WFVc4YBtNS4EKB8ondJJ40Eh8jw/viewform?usp=sf_link)

## About the RFQ System[​](#about-the-rfq-system "Direct link to About the RFQ System")

*RFQ liquidity is currently available on Mainnet, Polygon, and Arbitrum and Base via Swap API.*

### An Exclusive Source of Liquidity[​](#an-exclusive-source-of-liquidity "Direct link to An Exclusive Source of Liquidity")

In its role as a liquidity aggregator, 0x's APIs integrates both on- and off-chain liquidity. On-chain liquidity is sourced by sampling smart contract liquidity pools, such as Uniswap and Curve. Off-chain liquidity is sourced from professional market makers via the 0x Request-for-Quote (“RFQ”) System.

The RFQ system allows traders to *request* real time quotes from market makers. This source of liquidity is exclusive to 0x, has 0 slippage, and better trade execution.

If integrators request a standard quote from the Swap API, part or all of their quote may be sourced via the **RFQ** system. In this system, the Swap API aggregates quotes from professional market makers, alongside quotes from AMMs. If the market maker quotes are more competitive than AMM quotes, they may be included in the aggregated final price shown to the end-user. The end-user’s liquidity is ultimately provided by a combination of AMMs and professional market makers. *Everything happens under-the-hood!*

![RFQ Diagram](/docs/assets/images/rfq-diagram-a45edbfd0b9805c892991931918adf57.png)

tip

Read a comprehensive analysis of [0x's RFQ performance](https://0x.org/post/a-comprehensive-analysis-of-rfq-performance). In this report, we peel back the curtain on how 0x RFQ the best prices through Swap API for pairs where it’s available.

### Parties in the System[​](#parties-in-the-system "Direct link to Parties in the System")

**Takers**

Takers fill 0x orders by agreeing to trade their asset for the Maker's asset; in other words, consume the 0x liquidity. When making a Swap API request, the RFQ orders must contain the [`taker`](/docs/api#tag/Swap/operation/swap::permit2::getQuote) request parameter. When an order containing this parameter gets hashed and signed by two counterparties, it is exclusive to those two counterparties. This means that the order can only be filled by the taker address specified in the order. This is a security feature that prevents front-running and other types of attacks.

**Market Makers**

As mentioned earlier, 0x API works with specific market makers who participate in the RFQ system. Each maker is identified by an HTTP endpoint URL, and each endpoint has an associated list of asset pairs for which that endpoint will provide quotes. For the instance at `api.0x.org`, the 0x team is maintaining a list of trusted market makers.

## Integrating RFQ Liquidity[​](#integrating-rfq-liquidity "Direct link to Integrating RFQ Liquidity")

RFQ liquidity is included in a quote when `taker` is included in a [`/quote` request](/docs/api#tag/Swap/operation/swap::permit2::getQuote).

## Learn More[​](#learn-more "Direct link to Learn More")

### Video[​](#video "Direct link to Video")

Check out this 0x DevTalks video where we explore:

* What RFQ liquidity is
* Which use cases benefit most from RFQ
* How to unlock optimal trades with RFQ liquidity in 3 simple steps

### Blog[​](#blog "Direct link to Blog")

* [Unlock optimal trades in Swap API with 0x RFQ liquidity](https://0x.org/post/unlock-optimal-trades-in-swap-api-with-0x-rfq-liquidity)
* [A comprehensive analysis of RFQ performance](https://0x.org/post/a-comprehensive-analysis-of-rfq-performance)

[Previous

Sell Entire Balance](/docs/0x-swap-api/advanced-topics/sell-entire-balance)[Next

Gasless API](/docs/category/gasless-api)

* [About the RFQ System](#about-the-rfq-system)
  + [An Exclusive Source of Liquidity](#an-exclusive-source-of-liquidity)
  + [Parties in the System](#parties-in-the-system)
* [Integrating RFQ Liquidity](#integrating-rfq-liquidity)
* [Learn More](#learn-more)
  + [Video](#video)
  + [Blog](#blog)

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
[https://0x.org/docs/0x-swap-api/advanced-topics/about-the-rfq-system#docusaurus_skipToContent_fallback](https://0x.org/docs/0x-swap-api/advanced-topics/about-the-rfq-system#docusaurus_skipToContent_fallback)
