# Changelog | 0x

Changelog | 0x




[Skip to main content](#docusaurus_skipToContent_fallback)

[![0x Docs](/docs/img/0x-logo.png)](/docs/)[Docs](/docs/introduction/welcome)[API Reference](/docs/api)[Changelog](/docs/changelog/)

[Careers](https://0x.org/careers#open-positions)[Dashboard](https://dashboard.0x.org/)

On this page

![Changelog banner](/docs/assets/images/changelog-banner-32f0ee80054e8aa92441f7f0642e671d.png)

Stay updated on [0x API](https://0x.org/) changes and new features — [subscribe to the changelog](https://go.0x.org/subscribe-0x-changelog).

## 2025-06-27[​](#2025-06-27 "Direct link to 2025-06-27")

#### New Liquidity Sources[​](#new-liquidity-sources "Direct link to New Liquidity Sources")

* **Arbitrum**: Added DeltaSwap, SpartaDEX, and Arbswap.
* **Base**: Added Fluid.
* **BSC**: Added BabySwap, FraxSwap, and Dinosaur Eggs.

#### Chores[​](#chores "Direct link to Chores")

* Expanded **Uniswap v4** support:
  + Added Spot hook.
  + Updated Bunni, Clanker, and Flaunch hooks.
  + Enabled support for Zora Creator and Zora Content Coin
* Deprecated support for Orderbook v1
* Improved routing latency across infrastructure

#### Bug Fixes[​](#bug-fixes "Direct link to Bug Fixes")

* Fixed bug that caused 0 bps fills

## 2025-06-02[​](#2025-06-02 "Direct link to 2025-06-02")

#### New Liquidity Sources[​](#new-liquidity-sources-1 "Direct link to New Liquidity Sources")

* **Arbitrum:** Added Swaap.
* **Base:** Added Clanker (Uniswap v4 hook).
* **BSC:** Added Swaap.

#### Chores[​](#chores-1 "Direct link to Chores")

* Improved ZORA token support.
* Improved terminal.co token support.
* Updated settlement contract.

#### Bug Fixes[​](#bug-fixes-1 "Direct link to Bug Fixes")

* Router now returns an explicit error instead of a malformed route.
* Fixed handling of the `sellEntireBalance` flag.

## 2025-05-06[​](#2025-05-06 "Direct link to 2025-05-06")

#### New Chains[​](#new-chains "Direct link to New Chains")

* **Ink (57073)**: Now supported in Swap API.

#### New Liquidity Sources[​](#new-liquidity-sources-2 "Direct link to New Liquidity Sources")

* **Ink:** Added DYOR, InkySwap, SquidSwap, Reservoir v3, Velodrome v2, and Velodrome v3.
* **Berachain:** Added Honeyswap.
* **BSC:** Added BakerySwap.
* **Polygon:** Added Fluid.
* **Mode:** Added DackieSwap v3.

#### Chores[​](#chores-2 "Direct link to Chores")

* **Gasless Token Registry:** Updated registry for tokens eligible for gasless approvals.
* **RFQ Enhancements:** Improved RFQ handling on Arbitrum and Polygon, including support for smart contract takers.
* **Ekubo Upgrade:** Upgraded Ekubo to use the latest Solver actions and enabled VIP settlement.
* **WOOFi Update:** Updated WOOFi v2 Base Vault address.

## 2025-04-03[​](#2025-04-03 "Direct link to 2025-04-03")

#### 📣 Announcements[​](#-announcements "Direct link to 📣 Announcements")

* **Reminder**: API v1 will be sunset on **April 11, 2025**. To avoid service disruptions, migrate to v2 before this date. For more information, see the [Migration Guide](https://0x.org/docs/upgrading).

#### New Liquidity Sources[​](#new-liquidity-sources-3 "Direct link to New Liquidity Sources")

* **Base:** Added Spark PSM, Swaap, and Treble v2
* **Berachain:** Added DackieSwap v2, Kodiak v2, and Memeswap.
* **Ethereum:** Added Ekubo v2.
* **Monad Testnet:** Added Atlantis.
* **Unichain:** Added Velodrome v2 and Velodrome v3.

#### Chores[​](#chores-3 "Direct link to Chores")

* Improved Uniswap v4 support to automatically detect and index new pools.
* Upgraded WooFi integration to use their latest v2 contracts.

## 2025-03-07[​](#2025-03-07 "Direct link to 2025-03-07")

#### 📣 Announcements[​](#-announcements-1 "Direct link to 📣 Announcements")

* **Reminder**: API v1 will be sunset on **April 11, 2025**. To avoid service disruptions, migrate to v2 before this date. For more information, see the [Migration Guide](https://0x.org/docs/upgrading).

#### New Chains[​](#new-chains-1 "Direct link to New Chains")

* **Berachain (80094)**: Now supported in Swap API.
* **Unichain (130)**: Now supported in Swap API.

#### New Liquidity Sources[​](#new-liquidity-sources-4 "Direct link to New Liquidity Sources")

* **Uniswap v4**: Deployed on all supported networks (Ethereum, Arbitrum, Avalanche, Base, Blast, BNB Chain, Optimism, Polygon, World Chain).
* **Arbitrum:** Added Pancake v2.
* **Base:** Added Balancer v3, Bunni, and DackieSwap.
* **Berachain:** Added Bearswap, Bulla Exchange, BurrBear, Holdstation, Kodiak v2, Kodiak v3, and Memeswap.
* **Ethereum:** Added Ekubo and Swaap.

#### Chores[​](#chores-4 "Direct link to Chores")

* **Latency Optimization:** Improved router latency.

## 2025-01-31[​](#2025-01-31 "Direct link to 2025-01-31")

#### 📣 Announcements[​](#-announcements-2 "Direct link to 📣 Announcements")

* **Reminder**: API v1 will be sunset on **April 11, 2025**. To avoid service disruptions, migrate to v2 before this date. For more information, see the [Migration Guide](https://0x.org/docs/upgrading).

#### New Chains[​](#new-chains-2 "Direct link to New Chains")

* **Monad Testnet (10143)**: Added support for Swap API.

#### New Liquidity Sources[​](#new-liquidity-sources-5 "Direct link to New Liquidity Sources")

* **Arbitrum:** Added Fluid and swapr.
* **Base:** Added DeltaSwap, Kim V4, Rocket Swap, and SharkSwap.
* **Ethereum:** Added Sushiswap v3.
* **Linea:** Added Overnight.

#### Chores[​](#chores-5 "Direct link to Chores")

* **Entry Point Contract Update**: The entry point contract address now supports the Uniswap v4 contract. Developers are strongly advised not to hardcode this address. Instead, use the value returned by `transaction.to` (see [API reference](https://0x.org/docs/api#tag/Swap)).
* **Avalanche Uppdated the Cancun hardfork**: This means that the AllowanceHolder address on Avalanche is now `0x0000000000001fF3684f28c67538d4D072C22734` (see [0x Settler changelog](https://github.com/0xProject/0x-settler/blob/master/CHANGELOG.md#2025-01-23)).

## 2024-12-23[​](#2024-12-23 "Direct link to 2024-12-23")

#### 📣 Announcements[​](#-announcements-3 "Direct link to 📣 Announcements")

* **Reminder**: version 1.0 of the API will be sunset on **April 11, 2025**. Please migrate to Version 2.0 before this date to avoid service disruptions. For more information, see the [Migration Guide](https://0x.org/docs/upgrading).

#### New Liquidity Sources[​](#new-liquidity-sources-6 "Direct link to New Liquidity Sources")

* **Swaap v2 Integration**: Initial MVP integration of Swaap v2.
* Improved pricing for Virtuals Protocol (VIRTUAL) tokens.

#### New Chains[​](#new-chains-3 "Direct link to New Chains")

* **Worldchain**: Added support for the Worldchain network for Swap API.

#### Chores[​](#chores-6 "Direct link to Chores")

* Improved routing for small trades in high gas environments

#### Bug Fixes[​](#bug-fixes-2 "Direct link to Bug Fixes")

* Fixed a bug related to **gasless fee calculation**.

#### Documentation & Demos[​](#documentation--demos "Direct link to Documentation & Demos")

* **0x Gasless Trading Bot**: This demo showcases a TypeScript-based CLI trading bot that automates ERC20 token trades using the **0x Gasless API** on the **Base network**. The bot is executes gasless trades with Stop Loss and Take Profit strategies. [View the code](https://github.com/0xProject/0x-examples/tree/main/gasless-v2-trading-bot)
* **Use Swap API in Your Smart Contract with Foundry**: A toy example of the `SimpleTokenSwap` contract for ERC20 token swaps using the **0x Swap API v2**. The example is built and tested using **Foundry**. [View the code](https://github.com/0xProject/0x-examples/tree/main/swap-v2-with-foundry)

## 2024-11-27[​](#2024-11-27 "Direct link to 2024-11-27")

#### New Features[​](#new-features "Direct link to New Features")

* **Trade Analytics API** is now live and available to all integrators.
* Introduced the **`/getChains`** endpoint for Swap and Gasless APIs, allowing you to retrieve the supported chains for each API.

#### New Chains[​](#new-chains-4 "Direct link to New Chains")

* **Mantle** support is now live both Swap and Gasless APIs.

*Note: Interested to build on Mantle? Reach out via our [contact form](https://0x.org/contact)!*

#### New Liquidity Sources[​](#new-liquidity-sources-7 "Direct link to New Liquidity Sources")

* **BSC**: Added Baby Doge Swap, Nomiswap stable, Orion v2, and PancakeSwap stable.
* **Ethereum:** Added Fluid, Ring v2.
* **Polygon:** Added Meshswap, Polycat, Stepn, and Synapse.

## 2024-10-31[​](#2024-10-31 "Direct link to 2024-10-31")

#### New Features[​](#new-features-1 "Direct link to New Features")

* **Trade Analytics API** is now available in limited access. [Contact us](https://0x.org/contact) for early access inquiries.
* **Multi-user Access** for the 0x Dashboard is now live, allowing multiple users to manage account analytics and insights.
* **Detailed API Error Codes** are now displayed in the 0x Dashboard Analytics to streamline error troubleshooting.
* **Sell Entire Balance** option is now supported in Swap API v2. To enable, set `sellEntireBalance` to `true`. Supported for both allowance-holder and permit2 endpoints. [Learn more about implenting this feature](https://0x.org/docs/0x-swap-api/advanced-topics/sell-entire-balance).

#### New Liquidity Sources[​](#new-liquidity-sources-8 "Direct link to New Liquidity Sources")

* **Arbitrum:** Added Angle.
* **Base:** Added Angle and Clober V2.
* **BSC**: Added Maverick V2.
* **Ethereum:** Added Angle, DeFi Swap, Sky Migration (SKY, USDS), and Stepn.
* **Linea:** Added SyncSwap V2.
* **Mantle:** Added Cleopatra V1, Dodo V2, and Stratum Exchange.
* **Mode:** Added Balancer V2, iZiSwap, Kim V2, Kim V4, Morphex, SwapMode V2, SwapMode V3, Supswap V2, and Supswap V3.
* **Scroll:** Added Uni V3 and Wombat.

*Note: Want to add your liquidity source? Please fill out this [request form](https://forms.fillout.com/t/xrsvjHm85Hus).*

#### New Chains[​](#new-chains-5 "Direct link to New Chains")

* **Mantle (Beta)** is now live.
* **Gasless API** support added for **BSC, Avalanche, Mantle, and Mode** chains.

*Note: Interested to build on Mantle or with Gasless API? Reach out via our [contact form](https://0x.org/contact)!*

#### Chores[​](#chores-7 "Direct link to Chores")

* **Latency Optimization:** Shipped a technical rewrite reducing /price endpoint response times—p95 latency dropped from ~1s to ~500ms, and p50 latency decreased from ~550ms to ~340ms—with no impact on pricing performance.

#### Bug Fixes[​](#bug-fixes-3 "Direct link to Bug Fixes")

* **MNT and POL Compliance**: Improved support for MNT and POL tokens, which do not fully adhere to the ERC20 standard.
* **Slippage Handling**: Slippage now correctly caps at the maximum specified basis points (bps).
* **Meta-transaction Settler**: Fixed an RFQ handling issue in the meta-transaction flow.

#### Documentation[​](#documentation "Direct link to Documentation")

* New [guide](https://0x.org/docs/0x-swap-api/guides/smart-contract-wallet-integration) for integrating Smart Contract Wallets and Multi-Sig Wallets with the Permit2 Swap API.
* New [guide](https://0x.org/docs/0x-swap-api/advanced-topics/handling-native-tokens) on best practices for swapping native tokens (e.g., ETH).

## 2024-10-01[​](#2024-10-01 "Direct link to 2024-10-01")

#### New Features[​](#new-features-2 "Direct link to New Features")

* **0x API v2 is now live!** Follow our [migration guide](https://0x.org/docs/category/upgrading) to upgrade your app from v1 to v2.
* **Gasless API support** is now available on **Blast** and **Scroll**.
* **Swap API support** is also live on **Blast**, **Linea**, and **Scroll**.
* **New `slippageBps` parameter for the Gasless API**: This parameter allows you to define the maximum acceptable slippage for `buyToken`, in basis points (Bps). Learn more in the [Gasless API documentation](https://0x.org/docs/api#tag/Gasless).
* **TypeScript SDK**: Our new [TypeScript SDK](https://0x.org/docs/0x-swap-api/swap-ts-sdk) streamlines integration with the 0x v2 Swap and Gasless APIs. It offers full type safety and easy integration with Node.js, Next.js, and React Query.
* **Trade Analytics API**: Coming soon! Stay tuned for more information about how this API will provide key trading metrics and insights for better decision-making.

*Note: Interested to integrate Trade Analytics API when it's live? Contact us out via our [form](https://0x.org/contact)!*

#### New Chains[​](#new-chains-6 "Direct link to New Chains")

* **Mantle support** is coming soon!

*Note: Interested in building on Mantle? Contact us via [form](https://0x.org/contact)!*

## 2024-08-28[​](#2024-08-28 "Direct link to 2024-08-28")

#### New Features[​](#new-features-3 "Direct link to New Features")

* **Buy/Sell Tax Support**: Added support for Fee-on-Transfer tokens, which are subject to buy/sell taxes. Previously, users needed to adjust slippage tolerance manually to account for these taxes, often leading to errors. With the new fee-on-transfer accounting, slippage tolerance adjustments are no longer necessary. Additionally, the buy and sell tax are now returned, allowing users to utilize this information as needed.
* **Smart Contract Wallet Support**: Added support for Smart Contract Wallets in Swap API v2’s Permit2 flow.
* **Gas Optimization**: Implemented gas optimizations for Solidly V3 integration.
* **Routing Improvements**: Significantly improved routing for `amphrETH` and `sDOLA`.

#### New Liquidity Sources[​](#new-liquidity-sources-9 "Direct link to New Liquidity Sources")

* **Arbitrum**: Enabled RFQ on Arbitrum in Swap API v2.
* **Base**: Added `SoSwap` and `Kinetix` as new liquidity sources on Base. Also enabled RFQ on Base in Swap API v2.
* **Ethereum**: Added support for `sDAI` coverage.
* **Optimism Integration**: Added `WOOFi` as a new liquidity source on Optimism.

*Note: Want to add your liquidity source? Please fill out this [request form](https://forms.fillout.com/t/xrsvjHm85Hus).*

#### New Chains[​](#new-chains-7 "Direct link to New Chains")

* Preparation for **Linea** and **Scroll** support.

*Note: Interested to build on Scroll and/or Linea? Reach out via our [contact form](https://0x.org/contact)!*

* [2025-06-27](#2025-06-27)
* [2025-06-02](#2025-06-02)
* [2025-05-06](#2025-05-06)
* [2025-04-03](#2025-04-03)
* [2025-03-07](#2025-03-07)
* [2025-01-31](#2025-01-31)
* [2024-12-23](#2024-12-23)
* [2024-11-27](#2024-11-27)
* [2024-10-31](#2024-10-31)
* [2024-10-01](#2024-10-01)
* [2024-08-28](#2024-08-28)

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
[https://0x.org/docs/changelog/#docusaurus_skipToContent_fallback](https://0x.org/docs/changelog/#docusaurus_skipToContent_fallback)
