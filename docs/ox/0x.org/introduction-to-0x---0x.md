# Introduction to 0x | 0x

Introduction to 0x | 0x




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
* [Example Projects](https://github.com/0xProject/0x-examples)
* [Upgrading](/docs/upgrading)
* [Liquidity Providers](/docs/category/liquidity-providers)
* [Need Help?](/docs/category/need-help)

* [Introduction](/docs/category/introduction)
* What is 0x?

On this page

# Introduction to 0x

tip

Prefer to watch a video instead? Jump to [0x Videos](/docs/introduction/guides#videos).

## What is 0x?[​](#what-is-0x "Direct link to What is 0x?")

0x allows builders to embed swaps in their onchain apps. Tap into aggregated liquidity from 130+ sources, across 15+ EVM chains with the most efficient trade execution. Our suite of APIs has processed over 60M+ million transactions and $154B+ in volume from more than 9+ million users trading on apps like Matcha.xyz, Coinbase Wallet, Robinhood Wallet, Phantom, Metamask, Zerion, Zapper, and more.

![0x swap widget](/docs/assets/images/swap-widget-7538362651668891622d3cffb2ea5edf.png)

## Why use 0x?[​](#why-use-0x "Direct link to Why use 0x?")

At 0x, we believe all forms of value will eventually be tokenized and settle on-chain. But as more value becomes tokenized, liquidity becomes increasingly fragmented — across chains, across liquidity sources, and across protocols.

0x offers powerful APIs to simplify access to this fragmented liquidity:

* [Swap API](/docs/0x-swap-api/introduction) - The most efficient liquidity aggregator for ERC20 tokens through a single API.
* [Gasless API](/docs/gasless-api/introduction) - Never lose a user trade because of gas. Easily build frictionless apps with end-to-end gasless infra.
* [Trade Analytics API](/docs/trade-analytics-api/introduction) - Programatically access historical trades initiated through your apps via 0x Swap and Gasless APIs.

![0x routing](/docs/assets/images/routing-fce4478b601d3246d22593f25f1e3827.png)

tip

### ELI5 0x[​](#eli5-0x "Direct link to ELI5 0x")

Just like Google Flights compares prices across airlines to help you find the best flight deal, 0x API scans multiple decentralized exchanges to get you the best price when trading tokens. Instead of hopping between exchanges yourself, 0x does the hard work for you — all through a simple API that developers can plug into their apps. It’s fast, secure, and saves you time and money by finding the best route.

## The 0x Ecosystem[​](#the-0x-ecosystem "Direct link to The 0x Ecosystem")

### 0x Tech Stack[​](#0x-tech-stack "Direct link to 0x Tech Stack")

0x’s professional-grade APIs are built on the [0x Settler](/docs/developer-resources/core-concepts/contracts#0x-settler-contracts), a secure, audited smart contract. Builders using these APIs are part of the growing 0x ecosystem.

![0x tech stack v2](/docs/assets/images/0x-tech-stack-v2-b6789b1dcc674de32ceba05b4ac18339.png)

### Makers and Takers[​](#makers-and-takers "Direct link to Makers and Takers")

Within the 0x Ecosystem, there are two sides to a trade - Makers and Takers:

#### Supply Side (Makers)[​](#supply-side-makers "Direct link to Supply Side (Makers)")

This is the entity who creates [0x orders](/docs/developer-resources/core-concepts/order-types) and *provides liquidity* into the system for the Demand side (Takers) to consume. 0x aggregates liquidity from multiple sources including:

* On-chain liquidity - DEXs, AMMs (e.g. Uniswap, Curve, Bancor)
* Off-chain liquidity - Professional Market Makers, 0x's Open Orderbook network

Relevant Docs:

* [Market Makers](/docs/developer-resources/glossary#maker) - Professional Market Making With Limit Orders

#### Demand Side (Takers)[​](#demand-side-takers "Direct link to Demand Side (Takers)")

Takers consume token liquidity from Makers. They are applications or agents that initiate trades using the 0x protocol. This includes:

* Wallets
* Portfolio trackers
* SocialFi platforms
* AI agents
* Token screeners
* And [more](https://0x.org/case-studies)

Relevant Docs:

* [Swap API](/docs/0x-swap-api/introduction) - The most efficient liquidity aggregator for ERC20 tokens through a single API.
* [Gasless API](/docs/gasless-api/introduction) - enable developers to build frictionless apps with end-to-end gasless infrastructure

## How does 0x work?[​](#how-does-0x-work "Direct link to How does 0x work?")

Here's how a 0x order is created and settled:

![how does 0x work](/docs/assets/images/onchainoffchain-52268508d5da884280e98f63efe34ad5.gif)

1. **Order Creation**: A Maker creates a [0x order](/docs/developer-resources/core-concepts/order-types), a JSON object that follows a standard format.
2. **Maker Signature**: The Maker signs the order to cryptographically commit to it.
3. **Order Sharing**: The order is shared with potential Takers (e.g., direcly via an app)
4. **Aggregation**: 0x API aggregates liquidity across all [supply sources](/docs/introduction/introduction-to-0x#supply-aka-makers) and surfaces the best price.
   * This is done using [off-chain relay, on-chain settlement](/docs/developer-resources/core-concepts/glossary#off-chain-relay-on-chain-settlement), saving gas and improving flexibility.
5. **Order Submissions**: A Taker fills the order onchain by signing it and submitting it along with the fill amount.
6. **Order Settlement**: The **0x Settler** verifies the signature, checks trade conditions, and [atomically swaps](/docs/developer-resources/core-concepts/glossary#atomically-swapped) assets between Maker and Taker.

## What can I build on 0x?[​](#what-can-i-build-on-0x "Direct link to What can I build on 0x?")

0x powers a wide variety of web3 applications. Whether you're building a product where trading is central — like an exchange — or adding seamless token swaps to an app where trading is just one feature, 0x makes it easy to plug in liquidity.

> 🔗 For more inspiration, check out this [blog post](https://0x.org/post/inspiration-for-building-with-swap-api) and our [case studies](https://0x.org/case-studies).

### Demand-Side Use Cases (Takers)[​](#demand-side-use-cases-takers "Direct link to Demand-Side Use Cases (Takers)")

**Exchanges & Marketplaces**

* Decentralized exchange for a specific asset or vertical
* eBay-style marketplace for digital goods
* Over-the-counter (OTC) trading desk

**Wallets & Interfaces**

* Crypto wallets that support in-app token swaps
* Portfolio management dashboards
* Token screeners with built-in trade execution

**DeFi Protocols**

* Options, lending, and derivatives platforms needing deep liquidity
* Investment strategies like DeFi index funds or DCA (dollar-cost averaging) tools
* Prediction markets

**Social & Consumer Apps**

* SocialFi platforms with embedded token swaps
* Games with in-game currencies or tradable items
* NFT marketplaces

**Data & Analytics**

* Multi-chain analytics dashboards
* Real-time trade panels

**Agents & Automation**

* AI agents or bots that interact with DeFi
* On-chain automation or smart contract wallets

### Supply-Side Integrations (Makers)[​](#supply-side-integrations-makers "Direct link to Supply-Side Integrations (Makers)")

**Liquidity Sources**

* On-chain order books
* Automated market makers (AMMs)
* Proprietary market-making or arbitrage bots

[Previous

Get Started](/docs/introduction/getting-started)[Next

Learning Resources](/docs/introduction/guides)

* [What is 0x?](#what-is-0x)
* [Why use 0x?](#why-use-0x)
* [The 0x Ecosystem](#the-0x-ecosystem)
  + [0x Tech Stack](#0x-tech-stack)
  + [Makers and Takers](#makers-and-takers)
* [How does 0x work?](#how-does-0x-work)
* [What can I build on 0x?](#what-can-i-build-on-0x)
  + [Demand-Side Use Cases (Takers)](#demand-side-use-cases-takers)
  + [Supply-Side Integrations (Makers)](#supply-side-integrations-makers)

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
[https://0x.org/docs/introduction/introduction-to-0x#docusaurus_skipToContent_fallback](https://0x.org/docs/introduction/introduction-to-0x#docusaurus_skipToContent_fallback)
