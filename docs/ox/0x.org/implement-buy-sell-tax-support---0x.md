# Implement Buy/Sell Tax Support | 0x

Implement Buy/Sell Tax Support | 0x




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
* Buy/Sell Tax Support

On this page

# Implement Buy/Sell Tax Support

## Overview[​](#overview "Direct link to Overview")

Fee-on-Transfer (FoT) tokens, which impose automatic *Transfer Fees* or *Buy/Sell Taxes*, can [complicate transactions](https://0x.org/post/0x-v2-buy-sell-tax-swap-support), leading to inaccurate quotes and failed swaps. This guide explains how 0x v2 addresses these challenges with real-time detection and tax calculation, ensuring accurate quotes and reliable on-chain execution for a smoother user experience.

info

FoT (Fee-on-Transfer) Tokens are a category of tokens with Custom Properties either:

* a **Transfer Fee** (user pays a fee any time the token is transferred to another wallet) or,
* a **Buy/Sell Tax** (user pays a fee as a % of a swap when the token is bought or sold).

## The Problem[​](#the-problem "Direct link to The Problem")

Tokens with buy/sell tax properties disrupt standard token transfer assumptions, leading to:

* Revert rates as high as 30%
* High error rates (the #1 cause of custom token related errors)
* Inaccurate quotes
* A poor user experience

When handling buy/sell tax tokens, integrators face two main challenges:

* **Exact Matching**: The sent amount must match the received amount to avoid transaction reverts, but many tools used for detecting buy/sell tax and other custom token properties provide incomplete or outdated data which complicates this process.
* **User Experience**: Users must know if a token has a buy/sell tax upfront. Without reliable detection, integrators may adjust slippage to account for fees, but setting slippage too low risks reverts, while setting it too high exposes users to MEV attacks, undermining trust in your app.

![](/docs/assets/images/generic-swap-error-058fca8006dae34b76d8f2e9681cca94.png)

## How 0x Solves the Problem[​](#how-0x-solves-the-problem "Direct link to How 0x Solves the Problem")

0x v2 API provides a robust solution:

* **Automatic Detection & Optimized Routing**: 0x detects buy/sell tax tokens and optimizes trade routes, minimizing errors and transaction reverts. The API automatically includes the token’s buy/sell tax in its response.
* **Real-Time Tax Calculation**: 0x simulates each token transfer to provide precise, real-time tax information, ensuring accurate quotes and enhancing the user experience. The API returns valid quotes and calldata for tokens with buy/sell taxes in both `/price` and `/quote` endpoints.
* **User-Friendly Responses**: The API returns tax values in a format that’s easy to display to your end users, making it simple to communicate costs transparently.

## Implementation Best Practices[​](#implementation-best-practices "Direct link to Implementation Best Practices")

tip

⚡️ Explore the Swap API v2 [demo code repo](https://github.com/0xProject/0x-examples/tree/main/swap-v2-next-app) to see how to display the buy/sell tax for a selected token. For the specific code changes, check out this [PR](https://github.com/0xProject/0x-examples/pull/17).

⚡️ See how [Matcha displays buy/sell tax](https://matcha.xyz/tokens/ethereum/eth?sellAmount=1&buyChain=1&buyAddress=0xcf0c122c6b73ff809c693db761e7baebe62b6a2e) in their UI.

### Display Buy/Sell Tax Information[​](#display-buysell-tax-information "Direct link to Display Buy/Sell Tax Information")

To build trust with users, it's crucial to display buy/sell tax information transparently in the UI. Here's how to effectively integrate the buy/sell tax information provided by the 0x API into your application:

Step 1: Decide on UI to Show Buy/Sell Taxes Clearly

Decide how to best display the buy/sell taxes for tokens directly in the UI to improve transparency and user trust. If both the buy and sell tokens have taxes, be sure to indicate this. Below are some UI examples from the [Matcha](https://matcha.xyz/tokens/ethereum/eth?sellAmount=1&buyChain=1&buyAddress=0xcf0c122c6b73ff809c693db761e7baebe62b6a2e) app:

Example 1: Sell token (FLOKI) has a sell tax. See live trade [here](https://matcha.xyz/tokens/ethereum/eth?buyChain=1&buyAddress=0xcf0c122c6b73ff809c693db761e7baebe62b6a2e&sellAmount=1)

![](/docs/assets/images/matcha-buy-tax-ui-a0681c299051eb007f6bd8980996f271.png)

Example 2: Both buy (SMI) and sell tokens (FLOKI) have buy and sell taxes, respectively. See live trade [here](https://matcha.xyz/tokens/ethereum/0xcd7492db29e2ab436e819b249452ee1bbdf52214?sellAmount=1&buyChain=1&buyAddress=0xcf0c122c6b73ff809c693db761e7baebe62b6a2e)

![](/docs/assets/images/matcha-buy-sell-tax-ui-fcb0812b5858ffdf552e2996e37d0896.png)

Step 2: Utilize API Response Parameters

Use the `tokenMetadata` object returned in the `/price` and `/quote` endpoints for both [Swap and Gasless API calls](https://0x.org/docs/api). This object contains the buy/sell tax information for the tokens involved in the swap.

```
Example response:  
  
```json  
"tokenMetadata": {  
  "buyToken": {  
    "buyTaxBps": "200",  
    "sellTaxBps": "147"  
  },  
  "sellToken": {  
    "buyTaxBps": "0",  
    "sellTaxBps": "0"  
  }  
}  
```  

```

**Key Fields**:

* **tokenMetadata**: Contains metadata for the buy and sell tokens in the swap.
* **buyToken/sellToken**: Each contains `buyTaxBps` and `sellTaxBps`, representing the buy/sell tax in basis points for buying or selling the token.
* **buyTaxBps/sellTaxBps**: The buy/sell tax in basis points. If undetermined, this will be set to null.

Step 3: Format and Display Buy/Sell Tax Information

Convert the buy/sell tax basis points to a percentage and display them in the UI.

```
Example code to format and display tax information:  
  
```js  
// Helper function to format tax basis points to percentage  
const formatTax = (taxBps: string) => (parseFloat(taxBps) / 100).toFixed(2);  
  
// Display Tax Information in UI  
<div className="text-slate-400">  
  {quote.tokenMetadata.buyToken.buyTaxBps &&  
    quote.tokenMetadata.buyToken.buyTaxBps !== "0" && (  
      <p>  
        {buyTokenInfo(chainId).symbol +  
          ` Buy Tax: ${formatTax(quote.tokenMetadata.buyToken.buyTaxBps)}%`}  
      </p>  
    )}  
  {quote.tokenMetadata.sellToken.sellTaxBps &&  
    quote.tokenMetadata.sellToken.sellTaxBps !== "0" && (  
      <p>  
        {sellTokenInfo(chainId).symbol +  
          ` Sell Tax: ${formatTax(quote.tokenMetadata.sellToken.sellTaxBps)}%`}  
      </p>  
    )}  
</div>  
```  

```

### Route All Tokens with Buy/Sell Taxes Through 0x[​](#route-all-tokens-with-buysell-taxes-through-0x "Direct link to Route All Tokens with Buy/Sell Taxes Through 0x")

Many of our meta-aggregator integrators automatically route all tokens with buy/sell taxes through 0x by default. The 0x APIs are specifically designed to handle the complexities of tokens with buy/sell taxes by leveraging real-time tax detection and trade route optimization. This ensures accurate fee calculations for each transaction and keeps your application up-to-date with any changes to token tax structures, eliminating the need for manual updates or custom implementations.

### Educating Your Users[​](#educating-your-users "Direct link to Educating Your Users")

Consider including either links or pop-up modals next to buy/sell tax information to direct users to resources explaining these fees. For example, Matcha uses such links to guide users to blog posts or documentation, enhancing transparency and understanding.

This approach helps users grasp the implications of taxes, reduces confusion, and builds trust in your platform.

tip

👉 Try it on Matcha out [here](https://matcha.xyz/tokens/ethereum/eth?buyChain=1&buyAddress=0xcf0c122c6b73ff809c693db761e7baebe62b6a2e&sellAmount=1)

![](/docs/assets/images/matcha-transfer-fee-info-2fed50ddbd78ffbd83ed12a64d994b1c.png)

### Deciding on Terminology[​](#deciding-on-terminology "Direct link to Deciding on Terminology")

There’s no standard for how to label buy/sell token taxes. You may see it referred to as - "fee", "buy/sell tax", "transfer fee" on different platforms. Your choice should fit your project and user base.

* **Be Consistent:** Stick with the same term throughout your app.
* **Know Your Users:** Use terms your audience will easily understand.
* **Educate:** Provide links to explain the impact of buy/sell taxes.
  Clear, consistent terminology builds trust and improves user experience.

## Learn More[​](#learn-more "Direct link to Learn More")

* [(Blog) Introducing State-of-the-art Buy/Sell Tax support](https://0x.org/post/0x-v2-buy-sell-tax-swap-support)

[Previous

Access 0x Transaction Data](/docs/developer-resources/transaction-data)[Next

Bounties](/docs/developer-resources/bounties)

* [Overview](#overview)
* [The Problem](#the-problem)
* [How 0x Solves the Problem](#how-0x-solves-the-problem)
* [Implementation Best Practices](#implementation-best-practices)
  + [Display Buy/Sell Tax Information](#display-buysell-tax-information)
  + [Route All Tokens with Buy/Sell Taxes Through 0x](#route-all-tokens-with-buysell-taxes-through-0x)
  + [Educating Your Users](#educating-your-users)
  + [Deciding on Terminology](#deciding-on-terminology)
* [Learn More](#learn-more)

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
[https://0x.org/docs/developer-resources/buy-sell-tax-support#docusaurus_skipToContent_fallback](https://0x.org/docs/developer-resources/buy-sell-tax-support#docusaurus_skipToContent_fallback)
