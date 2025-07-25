# Sell Entire Balance | 0x

Sell Entire Balance | 0x




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
* Sell Entire Balance

On this page

# Sell Entire Balance

When building applications that involve composable smart contract interactions, such as Collateralized Debt Positions and Portfolio Rebalancing, the precise amount to sell via the Swap API is often determined by the output of a preceding onchain transaction. As a result, the actual amount to swap may be unknown at the time of requesting the quote and generating calldata.

The 0x Swap API supports these kinds of transactions through the `sellEntireBalance` parameter. It enables developers to provide an estimate of the sell amount for the quote, and then determines the actual amount to sell based on the balance of the taker at the time of execution.

info

Not building with smart contracts? Look at our [API Reference](/docs/api#tag/Swap) instead

### How it works[​](#how-it-works "Direct link to How it works")

To enable this feature, set the `sellEntireBalance` parameter on the API to `true` . This is supported by both our allowance-holder and permit2 endpoints.

Example:

```
https://api.0x.org/swap/allowance-holder/quote?chainId=1&sellAmount=0xeeeeeeeeeeee&buyAmount=0x124363&taker=0xabcdef&sellEntireBalance=true  

```

When set to true, the taker's balance during execution is used as the `sellAmount`. However, you must provide a `sellAmount` in the request so that we can determine the optimal route for the trade. The `sellAmount` provided should be the maximum estimated value, as close as possible to the actual taker's balance to ensure the best routing. We recommend that the taker's balance does not deviate by more than 1% from the set `sellAmount`. Attempting to sell more than the `sellAmount` may cause the trade to revert.

### How using this feature impacts your swap[​](#how-using-this-feature-impacts-your-swap "Direct link to How using this feature impacts your swap")

* Slippage: Since the taker's balance will be lower than the `sellAmount`, ensure that the slippage tolerance is adjusted for the possible variation.
* **Routing**: Routing will be optimized for the provided `sellAmount`. Ensure to keep the `sellAmount` as close to the taker balance as possible.
* **Fees:** Trade surplus 1 and swap fees will depend on the actual executed sell amount.

We recommend using the `sellEntireBalance` feature only for minor deviations in the intended sell amount. Larger deviations may lead to inefficient routing, inflated surplus fees, or trade reverts.

1 Trade surplus is available only to select integrators on a custom pricing plan. For assistance with setting up a custom plan, please contact support.

[Previous

Display Final Swapped Amount](/docs/0x-swap-api/advanced-topics/0x-parser)[Next

RFQ System Overview](/docs/0x-swap-api/advanced-topics/about-the-rfq-system)

* [How it works](#how-it-works)
* [How using this feature impacts your swap](#how-using-this-feature-impacts-your-swap)

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
[https://0x.org/docs/0x-swap-api/advanced-topics/sell-entire-balance#docusaurus_skipToContent_fallback](https://0x.org/docs/0x-swap-api/advanced-topics/sell-entire-balance#docusaurus_skipToContent_fallback)
