# 📘 Glossary | 0x

📘 Glossary | 0x




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
* Glossary

On this page

# 📘 Glossary

### 0x[​](#0x "Direct link to 0x")

0x is the company that created 0x API, 0x Settler smart contracts, and previously 0x Protocol.

### 0x API[​](#0x-api "Direct link to 0x API")

The 0x API is a collection of services and endpoints that sit on top of the 0x Settler contracts. It allows users to access aggregated liquidity from dozens of on-chain and off-chain decentralized exchange networks and across multiple blockchains. It comes with many parameters to customize your requests for your application and your users.

### 0x Settler[​](#0x-settler "Direct link to 0x Settler")

[0x Settler](https://github.com/0xProject/0x-settler/tree/master?tab=readme-ov-file) are the settlement contracts that settle 0x swaps on the blockchain. It uses [Permit2](https://github.com/Uniswap/permit2) to perform swaps without any passive allowances to the contract.

Here is a link to the 0x Settler Smart Contracts: <https://github.com/0xProject/0x-settler/tree/master/src>

### Atomically Swapped[​](#atomically-swapped "Direct link to Atomically Swapped")

Atomically swapped means the entire trade - the Maker’s asset going to the Taker and the Taker's asset going to the Maker - happens within one smart contract interaction.

### Automatic Market Maker (AMM)[​](#automatic-market-maker-amm "Direct link to Automatic Market Maker (AMM)")

An Automatic Market Maker (AMM) is the protocol that provides liquidity to the exchange it operates in through automated trading.

These protocols use smart contracts to define the price of digital assets and provide liquidity. Here, the protocol pools liquidity into smart contracts. In essence, users are not technically trading against counterparties – instead, they are trading against the liquidity locked inside smart contracts. These smart contracts are often called liquidity pools.

Examples of AMMs include Uniswap, Sushiswap, Curve, Balancer, Bancor, and many others.

### Buys and Sells[​](#buys-and-sells "Direct link to Buys and Sells")

When we say “buys” vs “sells” in the context of Swap API, this is what we mean:

* *Imagine a user is trading **token A for token B**.*
  + **Sell**: a sell is when the user is specifying the units of token A that they **would like to send**
  + **Buy**: a buy is when the user is specifying the units of token B that they **would like to receive**
* In both cases, the user is selling A for B. The terminology of "sells" vs "buys" in our `/swap` endpoint simply means "are you specifying an **input amount** or an **output amount**"?
* Generally in the UI, a "sell" is triggered when the user sets the field for token A and a "buy" is triggered when the user sets the field for token B. But in both cases, they're going from A → B.
* While these are commonly used terms, "buys" are a less commonly used feature.

### Call Data[​](#call-data "Direct link to Call Data")

When you send a transaction to an Ethereum smart contract for execution against a function, you must also send “data” or “call data”. The [first four bytes](https://www.4byte.directory/) of this call data, also known as the **function selector** (see below), determine the function, that the rest of the data is run against. The rest of the data is pretty much just the parameters passed to the function.

### CFMM[​](#cfmm "Direct link to CFMM")

Constant Function Market Makers - another term for Automatic Market Makers (AMMs)

### cURL[​](#curl "Direct link to cURL")

cURL, often just referred to as "curl", is a command-line tool for getting or sending data including files using URL syntax. It stands for "Client URL" and is widely used for various purposes involving data transfer over a network.

Most operating systems come bundled with curl. Learn more about installing an using curl [here](https://everything.curl.dev/install/index.html).

### EOA[​](#eoa "Direct link to EOA")

Externally Owned Account - this is an “end user” address, which is in contrast to a “smart contract” address.

### Function Selector[​](#function-selector "Direct link to Function Selector")

This is the first 4 bytes of the [**call data**](#call-data) that determine which function in a smart contract the transaction will run against. The function selector is the first 4 bytes of the `keccak256` hash of the function signature. Because hashing is only done on the function signature, all contracts that implement the same method (i.e. ERC-20s) have consistent function selectors (i.e. `0xa9059cbb` is always the Transfer function across contracts).

### Impermanent Loss (IL)[​](#impermanent-loss-il "Direct link to Impermanent Loss (IL)")

When the two assets in a pool start to diverge drastically in price (one becomes relatively expensive compared to the other), liquidity pools incur an opportunity cost where they would be better off simply holding each asset, as opposed to providing liquidity to the pool. This is also known as **Divergence Loss**.

### Maker[​](#maker "Direct link to Maker")

This is the Supply side of the the ecosystem. Makers create 0x orders, in other words, *provide the 0x liquidity*. 0x aggregates liquidity across a number of sources including - public DEX liquidity (e.g. Uniswap, Curve, Bancor), Professional MMs, 0x's Open Orderbook, AMM Liquidity Pools. This liquidity is put into the system to be consumed by Takers

### Off-chain infrastructure, on-chain settlement[​](#off-chain-infrastructure-on-chain-settlement "Direct link to Off-chain infrastructure, on-chain settlement")

Unlike other decentralized exchanges that function entirely on-chain, 0x does not store orders on the blockchain; instead, orders are stored off-chain and only trade settlement occurs on-chain.

### Permit2 Contract[​](#permit2-contract "Direct link to Permit2 Contract")

[Permit2](https://blog.uniswap.org/permit2-and-universal-router) is a standard from Uniswap and is the allowance-target (aka spender, aka operator) for any ERC20 traded via 0x's [`/swap/permit2`](/docs/api#tag/Swap) endpoints.

0x’s API v2 transactions are settled by the 0x Settler smart contracts. The 0x Settler smart contracts leverage [Permit2](https://blog.uniswap.org/permit2-and-universal-router) & AllowanceHolder to eliminate allowance risk and bake in protection at the ground level.

Read a [great explanation of the Permit2 contract and example usage](https://github.com/dragonfly-xyz/useful-solidity-patterns/tree/main/patterns/permit2).

### Request For Quotes (RFQ)[​](#request-for-quotes-rfq "Direct link to Request For Quotes (RFQ)")

RFQ stands for Request for Quote. It is a design pattern that allows traders to get real time quotes from Market Makers. We make API calls to Market Makers when they request a price from the 0x API. This source of liquidity is exclusive to 0x, has 0 slippage, and better trade execution.

### Slippage[​](#slippage "Direct link to Slippage")

The price difference between when a transaction is submitted and when the transaction is confirmed on the blockchain.

This occurs because AMMs price their assets along bonding curves that are a function of the size of the relative amounts of each asset, and this price can change if the relative trade size is large.

### Smart Order Routing[​](#smart-order-routing "Direct link to Smart Order Routing")

The 0x API helps users get the best price on their swap via Smart Order Routing splits a fill up up across the different sources to maximize the overall return on your swap. Checkout [this article](https://0x.org/post/0x-smart-order-routing)for details on how it works.

### Taker[​](#taker "Direct link to Taker")

This is the Demand side of the the ecosystem. Takers fill 0x orders by agreeing to trade their asset for the Maker's asset; in other words, *consume the 0x liquidity*. Examples of Takers include Metamask, Coinbase, Zapper, dydx, Matcha, etc.

[Previous

Order Types](/docs/developer-resources/core-concepts/order-types)[Next

White Paper](/docs/developer-resources/core-concepts/white-paper)

* [0x](#0x)
* [0x API](#0x-api)
* [0x Settler](#0x-settler)
* [Atomically Swapped](#atomically-swapped)
* [Automatic Market Maker (AMM)](#automatic-market-maker-amm)
* [Buys and Sells](#buys-and-sells)
* [Call Data](#call-data)
* [CFMM](#cfmm)
* [cURL](#curl)
* [EOA](#eoa)
* [Function Selector](#function-selector)
* [Impermanent Loss (IL)](#impermanent-loss-il)
* [Maker](#maker)
* [Off-chain infrastructure, on-chain settlement](#off-chain-infrastructure-on-chain-settlement)
* [Permit2 Contract](#permit2-contract)
* [Request For Quotes (RFQ)](#request-for-quotes-rfq)
* [Slippage](#slippage)
* [Smart Order Routing](#smart-order-routing)
* [Taker](#taker)

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
[https://0x.org/docs/developer-resources/core-concepts/glossary#off-chain-relay-on-chain-settlement](https://0x.org/docs/developer-resources/core-concepts/glossary#off-chain-relay-on-chain-settlement)
