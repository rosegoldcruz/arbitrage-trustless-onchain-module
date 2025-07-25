# How to monetize your app using 0x Swap API | 0x

How to monetize your app using 0x Swap API | 0x




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

    - [Get started with Swap API](/docs/0x-swap-api/guides/swap-tokens-with-0x-swap-api)
    - [Build a token swap dApp (Next.js)](/docs/0x-swap-api/guides/build-token-swap-dapp-nextjs)
    - [Monetize your app](/docs/0x-swap-api/guides/monetize-your-app-using-swap)
    - [Troubleshooting Swap API](/docs/0x-swap-api/guides/troubleshooting-swap-api)
    - [Smart Wallet & Multi-Sig Wallet Integration](/docs/0x-swap-api/guides/smart-contract-wallet-integration)
  + [Advanced Topics](#)
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
* Guides
* Monetize your app

On this page

# How to monetize your app using 0x Swap API

*This guide covers how you can monetize your app by using the 0x Swap API.*

## Introduction[​](#introduction "Direct link to Introduction")

As you build your DeFi business, it’s likely that you are including swaps directly in-app to help your users conveniently trade at the best price. As your business grows, you may consider low-friction ways to monetize in order to generate revenue and build a sustainable Web3 business.

This guide covers two basic monetization options - collecting *affiliate fees* and collecting *trade surplus*. It also covers pricing considerations, along with code samples and a demo app to help you implement these options.

Collecting *affiliate fees* is available to teams on *all* [pricing plans](https://0x.org/pricing). Collecting *trade surplus* is available only to select integrators on a custom pricing plan. For assistance with setting up a custom plan, please [contact support](https://help.0x.org/en/articles/8230055-how-to-get-dev-support-from-the-0x-team).

tip

### Demo Quicklinks[​](#demo-quicklinks "Direct link to Demo Quicklinks")

⚡️ See these monetization options implemented in a [live demo here](https://0x-swap-v2-demo-app.vercel.app/).

⚡️ Checkout the [demo code](https://github.com/0xProject/0x-examples/tree/main/swap-v2-next-app) to see how to collect affiliate fees and trade surplus.

tip

Check out our [Monetization Report](https://0x.org/reports/monetization-across-defi-report) to see how top DeFi apps are turning trading activity into millions in revenue.

## How to monetize on trades[​](#how-to-monetize-on-trades "Direct link to How to monetize on trades")

Out-of-the-box with 0x Swap API, you have two monetization options:

* [Collect affiliate fees](#option-1-collect-affiliate-fees) (aka trading fee or commission)
* [Collect trade surplus](#option-2-collect-trade-surplus) (aka positive slippage)

![](/docs/assets/images/monetize-swap-ca70aed05826c730fd86d16de8754287.png)

## Option 1: Collect affiliate fees[​](#option-1-collect-affiliate-fees "Direct link to Option 1: Collect affiliate fees")

As a 0x Swap API integrator, you have full flexibility to collect an affiliate fee on any trade made through your application.

Setup requires including the following three parameters when making a [Swap API request](/docs/api#tag/Swap/operation/swap::permit2::getQuote):

* `swapFeeRecipient` - The wallet address to receive the specified trading fees.
* `swapFeeBps` - The amount in Bps (Basis points) of the `swapFeeToken` to charge and deliver to the `swapFeeRecipient`. Denoted as an integer between 0 - 1000 where 1000 Bps represents 10%.
* `swapFeeToken` - The contract address of the token to receive trading fees in. This must be set to either the value of `buyToken` or the `sellToken`.

### Example API call[​](#example-api-call "Direct link to Example API call")

```
https://api.0x.org/swap/permit2/quote                 // Request a firm quote  
?chainId=1                                            // Ethereum Mainnet  
&sellToken=0x6B175474E89094C44Da98b954EedeAC495271d0F // Sell DAI  
&sellAmount=4000000000000000000000                    // Sell amount: 4000 (18 decimal)  
&buyToken=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE  // Buy ETH  
&taker=$USER_TAKER_ADDRESS                            // Address that will make the trade  
&swapFeeRecipient=$INTEGRATOR_WALLET_ADDRESS // Wallet address that should receive the affiliate fees  
&swapFeeBps=100                              // Percentage of buyAmount that should be attributed as affiliate fees  
&swapFeeToken=0x6B175474E89094C44Da98b954EedeAC495271d0F // Receive trading fee in sellToken (DAI)  
--header '0x-api-key: [API_KEY]' // Replace with your own API key  
--header '0x-version: v2' // API version  

```

When the transaction has gone through, the fee amount indicated by `swapFeeBps` will be sent to the `swapFeeRecipient` address you've set. The fee is received in the `swapFeeToken`.
If you would like to receive a specific type of token (e.g. USDC), you will need to convert those on your own.

### Displaying fees in the UI[​](#displaying-fees-in-the-ui "Direct link to Displaying fees in the UI")

The fee `amount` is returned in the `fees.integratorFee` object. Two recommended methods to display the fees are:

* display the `fee.integratorFee.amount` (make sure to consider the token's base units)
* display the `swapFeeBps` and the `swapFeeToken` separately

info

A note on how `fee.integratorFee.amount` is calculated

The `amount` is calculated from (`swapFeeBps`/10000) \* `sellAmount` (in the `sellToken` base unit).

For example, to take a 1% fee on selling 100 USDC,

* `sellToken=0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` (USDC)
* `sellAmount=100000000` (USDC has a base unit of 6 decimals)
* `swapFeeBps=100` (1% fee)

The fee amount would be `1000000`, which is `1` USDC.

```
...  
"fees": {  
    "integratorFee": {  
      "amount": "1000000",  
      "token": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",  
      "type": "volume"  
    },  
...  

```

The following are examples from different apps that show these two options.

![](/docs/assets/images/affiliate-fee-example-3-0cd98392e1c44f8a6f65512ea00282b6.png)![](/docs/assets/images/affiliate-fee-example-2-aff4ef164ac8e8224db972051030a2c1.png)

### Pricing considerations[​](#pricing-considerations "Direct link to Pricing considerations")

When deciding how much to set your fee amount, consider the following. We recommend setting your pricing in a way that strengthens your bottom line, aligning it with the value you provide to customers while considering any transaction costs. Note that the additional affiliate fee will impact the price for the end user, so find that sweet spot where your solution remains competitive and impactful.

Be aware that `swapFee` has a default limit of 1000 Bps. If your application requires a higher value, [please reach out to us](https://help.0x.org/en/articles/8230055-how-to-get-dev-support-from-the-0x-team).

## Option 2: Collect trade surplus[​](#option-2-collect-trade-surplus "Direct link to Option 2: Collect trade surplus")

*Collecting trade surplus is only available to select integrators on a custom pricing plan. For
assistance with setting up a custom plan, please [contact
support](https://help.0x.org/en/articles/8230055-how-to-get-dev-support-from-the-0x-team).*

Trade surplus, also known as positive slippage, occurs when the user ends up receiving more tokens than their quoted amount. 0x Swap API can be easily configured so that you collect the trade surplus and send that to a specified address.

This can be done by setting the `tradeSurplusRecipient` parameter in a [Swap API request](/docs/api#tag/Swap/operation/swap::permit2::getQuote).

`tradeSurplusRecipient` represents the wallet address that will receive any trade surplus. When a transaction produces trade surplus, 100% of it will be collected in that wallet.

The surplus is received in the `buyToken` (the token that the user will receive). If you would like to receive a specific type of token (e.g. USDC), you will need to make that conversion on your own.

When `tradeSurplusRecipient` is not specified, the feature is effectively OFF and all trade surplus will be passed back to the `taker`.

### Example API call[​](#example-api-call-1 "Direct link to Example API call")

```
https://api.0x.org/swap/permit2/quote                 // Request a firm quote  
?chainId=1                                            // Ethereum Mainnet  
&sellToken=0x6B175474E89094C44Da98b954EedeAC495271d0F // Sell DAI  
&sellAmount=4000000000000000000000                    // Sell amount: 4000 (18 decimal)  
&buyToken=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE  // Buy ETH  
&taker=$USER_TAKER_ADDRESS                            // Address that will make the trade  
&tradeSurplusRecipient=$INTEGRATOR_WALLET_ADDRESS     // The recipient of any trade surplus fees  
--header '0x-api-key: [API_KEY]'                     // Replace with your own API key  
--header '0x-version: v2'                            // Replace with your own API key  
  

```

[Previous

Build a token swap dApp (Next.js)](/docs/0x-swap-api/guides/build-token-swap-dapp-nextjs)[Next

Troubleshooting Swap API](/docs/0x-swap-api/guides/troubleshooting-swap-api)

* [Introduction](#introduction)
* [How to monetize on trades](#how-to-monetize-on-trades)
* [Option 1: Collect affiliate fees](#option-1-collect-affiliate-fees)
  + [Example API call](#example-api-call)
  + [Displaying fees in the UI](#displaying-fees-in-the-ui)
  + [Pricing considerations](#pricing-considerations)
* [Option 2: Collect trade surplus](#option-2-collect-trade-surplus)
  + [Example API call](#example-api-call-1)

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
[https://0x.org/docs/0x-swap-api/guides/monetize-your-app-using-swap#docusaurus_skipToContent_fallback](https://0x.org/docs/0x-swap-api/guides/monetize-your-app-using-swap#docusaurus_skipToContent_fallback)
