# 🤔 FAQ & Troubleshooting | 0x

🤔 FAQ & Troubleshooting | 0x




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

  + [FAQ & Troubleshooting](/docs/developer-resources/faqs-and-troubleshooting)
  + [Contact support](https://help.0x.org/en/articles/8230055-how-to-get-support-from-the-0x-team)
  + [Help center](https://help.0x.org/en/)
  + [Submit a feature request](https://help.0x.org/en/articles/8410844-how-to-submit-a-0x-feature-request)
  + [Contact sales](https://0x.org/contact)

* [Introduction](/docs/category/introduction)
* FAQ & Troubleshooting

On this page

# 🤔 FAQ & Troubleshooting

**Categories**

* [Troubleshooting](/docs/developer-resources/faqs-and-troubleshooting#-troubleshooting)
* [Swap API](/docs/developer-resources/faqs-and-troubleshooting#-swap-api)
  + [About Swap API](/docs/developer-resources/faqs-and-troubleshooting#about-swap-api)
  + [Monetizing your Swap Integration](/docs/developer-resources/faqs-and-troubleshooting#monetizing-your-swap-integration)
  + [Permit2 and AllowanceHolder](/docs/developer-resources/faqs-and-troubleshooting#permit2-and-allowanceholder)
  + [Parameter Questions](/docs/developer-resources/faqs-and-troubleshooting#parameter-questions)
  + [Best Practices](/docs/developer-resources/faqs-and-troubleshooting#best-practices)
* [Gasless API](/docs/developer-resources/faqs-and-troubleshooting#%EF%B8%8F-gasless-api)
* [Trade Analytics API](/docs/developer-resources/faqs-and-troubleshooting#trade-analytics-api)
* [0x Dashboard](/docs/developer-resources/faqs-and-troubleshooting#-0x-dashboard)
* [Smart Contracts](/docs/developer-resources/faqs-and-troubleshooting#-smart-contracts)
* [Building with 0x](/docs/developer-resources/faqs-and-troubleshooting#-building-with-0x)

## Troubleshooting[​](#troubleshooting "Direct link to Troubleshooting")

I received an API issue / error code. Help!

See [Handling API issues and error codes](/docs/introduction/api-issues)  for a full list of common 0x issue types and error codes and how to resolve them.

Why am I getting a CORS error when using the 0x API?

**TL;DR** CORS errors happen because the 0x API enforces strict security policies. Avoid making API calls directly from the browser to prevent CORS issues and exposing your API keys. Instead, use a backend server, serverless functions, or a full-stack framework.

**Error Message**
You might see an error like this:

```
http://localhost:3000 has been blocked by CORS policy: Request header field 0x-version is not allowed by Access-Control-Allow-Headers in preflight response.  

```

**Explanation**

This error occurs because browsers block requests with custom headers (e.g., 0x-version) unless explicitly allowed by the server. Making API calls from a browser is not recommended because it can expose your API keys.

**Recommended Solutions**

1. Use a Backend Server

* Proxy API calls through a backend server.
* Securely handle API keys and requests with libraries like axios (Node.js) or requests (Python).

2. Serverless Functions

* Use platforms like AWS Lambda, Vercel Functions, or Netlify Functions to handle requests securely.

3. Full-Stack Framework

* Implement backend logic in frameworks like Next.js or Remix to manage API calls.

Why does my 0x transaction revert?

If your 0x quote is reverting, besides the standard revert issues related to ETH transactions, we recommend check the following are set correctly:

* Are allowances properly set for the user to trade the `sellToken`?
* Does the user have enough `sellToken` balance to execute the swap?
* Do users have enough to pay the gas?
* The slippage tolerance may be too low if the liquidity is very shallow for the token the user is trying to swap. Read [here](/docs/0x-swap-api/guides/troubleshooting-swap-api#slippage-tolerance) for how to handle this.
* Did the RFQ Quote expire? RFQ quotes from Market Makers are only valid for a short period of time, for example roughly 60s on mainnet. See "Did my order revert because the RFQ quote expired?" below for more details.
* Working in testnet? Only a subset of DEX sources are available. Be aware that token you want to use for testing must have liquidity on at least one of these sources; otherwise, you will receive an error. Read [here](/docs/0x-swap-api/guides/working-in-the-testnet) for how to handle this.

For more details on addressing common issues, read [Troubleshooting](/docs/0x-swap-api/guides/troubleshooting-swap-api).

Did my order revert because the RFQ quote expired?

RFQ quotes from Market Makers are only valid for a short period of time, for example roughly 60s on mainnet.

Two ways to check if this was the reason for your order reverting, you can use the Tenderly debugger on the transaction, search for order info by looking at the `getOTCOrderInfo` step in the trace look for the `expiryAndNonce` field. You may need to reach out to [0x support](https://help.0x.org/en/articles/8230055-how-to-get-support-from-the-0x-team) to help you decode the `expiryAndNonce` field.

Therefore, as a best practice we highly recommend adding an in-app mechanism that refreshes the quotes, approximately every 30s, to make sure RFQ orders don’t expire. See [Matcha.xyz](https://matcha.xyz/) for an example of this in action.

0x orders are reverting but my transaction is fine, what is happening?

Developers may note when analyzing their transactions that some subset of 0x orders may revert (not filled) but the whole transaction is successful. This is expected behavior as implied earlier, some orders due to timing, and the pricing may be filled or expired before a users attempt to fill the order. This would result in a revert and 0x protocol will utilize fallback orders to compensate for the reverted order. This will result in a successful transaction even though reverts occur within the transactions.

How does including `taker`, the address which holds the `sellToken`, in the API call help with catching issues?

By passing a `taker` parameter, 0x API can provide a more bespoke quote and help catch revert issues:

* 0x API will estimate the gas cost for `taker` to execute the provided quote.
* If successfully called, the `gas` parameter in the quote will be an accurate amount of gas needed to execute the swap.
* If unsuccessful for revert reasons suggested above, then 0x API will throw a gas cost estimation error, alluding to an issue with the `taker` executing the quote.

**TLDR** Pass `taker` to get the quote validated before provided to you, assuring that a number of revert cases will not occur.

I received an `INPUT_INVALID` error. Help!

Check that the API request was formatted properly. If the issue persists, [contact support](https://help.0x.org/en/articles/8230055-how-to-get-dev-support-from-the-0x-team) to resolve the issue.

I received an `BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE` or `SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE` error. Help!

The buy token is not authorized for trade due to legal restrictions

I received an `INTERNAL_SERVER_ERROR` error. Help!

An internal server error occurred.

Check that the API request was formatted properly. Check [0x system status](https://0x.statuspal.io/).

If the issue persists, [contact support](https://help.0x.org/en/articles/8230055-how-to-get-dev-support-from-the-0x-team) to resolve the issue.

How will I know if the trade is not possible due to insufficient asset liquidity?

The API will return `liquidityAvailable=false` and not return any of the other response params if there is not enough liquidity avilable for the quote requested.

![liquidityAvailable parameter](/docs/assets/images/liquidityAvailable-b626c3dd924529e2e23aa8e1ce46dccc.png)

What does MEV protection mean?

Use the [getSources](https://0x.org/docs/api#tag/Sources) endpoint.

## Swap API[​](#swap-api "Direct link to Swap API")

### About Swap API[​](#about-swap-api "Direct link to About Swap API")

How do I get a list of all the sources the API is sourcing from?

Use the [getSources](https://0x.org/docs/api#tag/Sources) endpoint.

How do I find a list of support chains for Swap?

Use the [getChains](https://0x.org/docs/api#tag/Swap/operation/swap::chains) endpoint to get a list of supported chains for Swap.

Is there a fee to use Swap API?

We offer two transparent, flexible tiers for Web3 businesses of all sizes. You can get started with them [here])(<https://0x.org/pricing>). If you are a high-volume app or have a unique business model, [please contact us](https://0x.org/contact) to discuss a custom plan.

0x takes an on-chain fee on swaps for select tokens for teams on the Standard tier. This fee is charged on-chain to the users of your app during the transaction. If you are on a custom tier, we can discuss customized options. In cases where we charge a fee, we'll return the value of the fee in the API response in the `zeroExFee` parameter. You can find more details about this parameter in the [Swap API reference](/docs/api#tag/Swap).

How does Swap API select the best orders for me?

Beyond simply sampling each liquidity source for their respective prices, Swap API adjusts for the gas consumption of each liquidity source with the specified gas price (if none is provided Swap API will use ethGasStation's `fast` amount of gwei) and any associated fees with the specific liquidity source. By sampling through varying compositions of liquidity sources, Swap API selects the best set of orders to give you the best price. Swap API also creates another set of fallback orders to ensure that the quote can be executed by users.

Ex: Swap API will adjust the price potentially received from Curve Finance by `gas * gasPrice` and its fees. Because of Curve Finance’s costly gas consumption, its nominal price may not be the best price when settled.

How can I find the tokens that 0x supports for trading?

0x supports all tokens by default except for tokens blocked for compliance reasons.

Is it possible to use the Swap API to trade custom ERC20 tokens or altcoins?

If you would like to trade a custom token, you will need to create the liquidity either by creating a Liquidity Pool for your token on one of the various AMM sources that the API sources from, such as Uniswap, SushiSwap, or Curve.

What does MEV protection mean?

MEV protection applies to [RFQ (Request-for-Quote) orders](/docs/0x-swap-api/advanced-topics/about-the-rfq-system), where quotes are filled privately and atomically to prevent sandwiching or front-running. It does not apply to AMM (Automated Market Maker) trades, which are executed on public mempools and are subject to typical MEV risks.

### Monetizing your Swap Integration[​](#monetizing-your-swap-integration "Direct link to Monetizing your Swap Integration")

I am building a DEX app using Swap API. Can I charge my users a trading fee/commission when using the Swap API? 

You have the option to either collect affiliate fees or collect trade surplus. Read our full guide on [monetizing your swap integration](/docs/0x-swap-api/guides/monetize-your-app-using-swap).

 How is the trading fee/commission I charge returned by Swap API - is it part of the quoted price or is it a separate parameter? 

If the `swapFeeRecipient`, `swapFeeBps`, and `swapFeeToken` parameters are set when making a Swap API request, the returned response will return a `fees.integratorFee` object with the `amount` property that can be displayed to your end user.

The `amount` is calculated from (`swapFeeBps`/10000) \* `sellAmount` (in the `sellToken` base unit).

For example, to take a 1% fee on selling 100 USDC,

* `sellToken=0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` (USDC)
* `swapFeeToken=0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`
* `sellAmount=100000000` (USDC has a base unit of 6 decimals)
* `swapFeeBps=100` (1% fee)

The fee amount would be `1000000`, which is `1` USDC.

```
// Example quote response with fee.integratorFee object  
...  
"fees": {  
    "integratorFee": {  
      "amount": "1000",  
      "token": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",  
      "type": "volume"  
    },  
    ...  

```

For examples and details, read our full guide on [monetizing your swap integration](/docs/0x-swap-api/guides/monetize-your-app-using-swap). In API V2, you can charge opt to take your fee on either the `buyToken` or the `sellToken` in order to aggregate your revenue in a few tokens.

Can I collect trade surplus (a.k.a. positive slippage)?

Collecting trade surplus is only available to select integrators on a custom pricing plan. For
assistance with setting up a custom plan, please [contact
support](https://help.0x.org/en/articles/8230055-how-to-get-dev-support-from-the-0x-team).

Read our full guide on [monetizing your swap integration](/docs/0x-swap-api/guides/monetize-your-app-using-swap).

### Permit2 and AllowanceHolder[​](#permit2-and-allowanceholder "Direct link to Permit2 and AllowanceHolder")

What is the difference between using Permit2 and AllowanceHolder for Swap API?

0x Swap API allows you to choose between two allowance methods: [Permit2](/docs/introduction/0x-cheat-sheet#permit2-contract) or [AllowanceHolder](/docs/introduction/0x-cheat-sheet#allowanceholder-contract).

The decision when choosing between Permit2 or AllowanceHolder boils down to mainly UX and integration type.

**When to Use Permit2**

For most applications, we recommend using Permit2. This method requires two user signatures per trade:

* A signature for limited approval
* A signature for the trade itself

Permit2 is also recommended for setups involving multisig or smart contract wallets, as long as the smart contract supports [EIP-1271](https://eips.ethereum.org/EIPS/eip-1271), which most do.

Additionally, Permit2 is a standard that allows users to share token approvals across smart contracts. If a user has an infinite allowance set on Permite2 via another app, they don't need to reset the allowance.

**When to Use AllowanceHolder**

We recommend using Permit2 for most situations. However, if your integration doesn't support a double-signature flow, such as with smart contracts that aren't compatible with [EIP-1271](https://eips.ethereum.org/EIPS/eip-1271), AllowanceHolder is a better choice. It works best for single-signature use cases, including:

* Projects integrating the Swap API into smart contracts without EIP-1271 support.
* Teams aggregating across multiple sources and aiming for a consistent user experience across all integrations.

If you're concerned about upgrade speed, consider using AllowanceHolder, as it closely resembles the 0x Swap v1 integration. This approach can help streamline the upgrade process for teams that previously used Swap v1.

Read more about using [Permit2 and AllowanceHolder contracts](/docs/introduction/0x-cheat-sheet#permit2-contract).

**Key Points:**

* **Permit2:** Ideal for for most applications. Involves two signatures, one signature for limited approval and one signature for the trade itself. Also recommended for multisig or smart contract wallets.
* **AllowanceHolder:** Best for single-signature use cases, especially in smart contracts that don't support [EIP-1271](https://eips.ethereum.org/EIPS/eip-1271) or meta-aggregators.

**Permit2 Resources**

* Use the [`/swap/permit2`](/docs/api#tag/Swap/operation/swap::permit2::getPrice) endpoints
* Follow our [guide for Swap API with Permit2](/docs/upgrading/upgrading_to_swap_v2#permit2)
* See the [Permit2 headless example](https://github.com/0xProject/0x-examples/tree/main/swap-v2-headless-example)

**AllowanceHolder**

* See the [`/swap/allowance-holder`](/docs/api#tag/Swap/operation/swap::allowanceHolder::getPrice) endpoints
* Follow our [guide for Swap API with AllowanceHolder](/docs/upgrading/upgrading_to_swap_v2#allowanceholder)
* See the [AllowanceHolder headless example](https://github.com/0xProject/0x-examples/tree/main/swap-v2-headless-example)

For more details, check out the [Permit2 and AllowanceHolder contracts](/docs/introduction/0x-cheat-sheet#permit2-contract)

Should I use AllowanceHolder or Permit2 for my meta-aggregator project?

The decision when choosing between Permit2 or AllowanceHolder boils down to mainly UX and integration type.

* **AllowanceHolder** is ideal for single-signature use cases and provides a consistent user experience when aggregating across multiple sources. It also closely resembles the 0x Swap v1 integration, making it quicker to implement.
* **Permit2** is a universal standard that allows users to share token approvals across smart contracts (i.e. if users have an infinite allowance via another app, no reset is needed). However, Permit2 requires two signatures per trade (one for approval, one for the trade), which may impact user experience.

Evaluate your project’s needs and the desired user experience to make the best decision.

If an allowance is needed when using AllowanceHolder, which contract will `issues.allowance.spender` return?

The AllowanceHolder contract will be returned.

How should the signed the Permit2 EIP-712 (`permit2.eip712`) message look?

The standard encoding of a signature in Ethereum decomposes the secp256k1 signature into 3 values: `r`, `s`, and `v`.
*Typically* these are ordered as `v`, `r`, `s`, but Permit2 requires that they be ordered as `r`, `s`, and `v`, where

* `r` is less than `secp256k1n`
* `s` is less than `secp256k1n / 2 + 1`, and
* `v` is either `0` or `1` to indicate the sign (or equivalently the parity) of the `y` coordinate. *However*, the convention on the EVM is that `v` is actually encoded as `27 + v` (i.e. either 27 or 28). Make sure your signature adds 27 to `v`

Then, all 3 values are packed and encoded as 65 bytes (bytes 0 through 31 represent `r`, 32 through 63 represent `s`, and byte 64 represents `v`).

### Parameter Questions[​](#parameter-questions "Direct link to Parameter Questions")

What is gas?

Gas refers to the fee required to successfully conduct a transaction on the Ethereum blockchain. Gas fees are paid in Ether (ETH) and denominated in Gwei, which is a denomination of Ether (1 ETH = 1,000,000,000 Gwei).

What is the significance of this address `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE` ?

The address `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE` is a standardized representation of native tokens in blockchain transactions. Native tokens, such as ETH on Ethereum, BNB on Binance Smart Chain, and POL on Polygon, are the foundational currencies of their respective blockchains. Since native tokens do not inherently have an address (unlike ERC-20 tokens), this address is widely used by dapps to facilitate interactions with native tokens in a standardized way.

* **On Ethereum:** This address represents Ether (ETH), as ETH is not an ERC-20 token.
* **On Mantle Network:** An exception is the native token $MNT, which does have a contract address (`0xdeaddeaddeaddeaddeaddeaddeaddeaddead0000`) for use on the Mantle EVM chain. This address is specific to $MNT on Mantle and does not apply to wrapped or bridged versions of $MNT on other networks. See this guide to understand other [differences between Ethereum and Mantle](https://docs.mantle.xyz/network/for-developers/difference-between-ethereum-and-mantle).

For more details:

* [Discussion on native token address](https://www.reddit.com/r/ethereum/comments/iatr1d/what_is_the_significance_of_this_address/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
* [Stack Exchange explanation](https://ethereum.stackexchange.com/a/87444/85979).

Additionally, refer to the [Handling native tokens with 0x Swap API](/docs/0x-swap-api/advanced-topics/handling-native-tokens) guide, which explains how to manage native tokens when using the 0x Swap API, as their handling differs from that of standard ERC-20 tokens.

Does the 0x API return buyAmount in the base unit of the given token?

Yes. All buyAmounts returned by the 0x API are returned in the base unit of the token.

For example:

* For an ERC20 token with 18 decimals (like WETH or DAI), `buyAmount: 1000000000000000000` represents **1.0 token**.
* For a token with 6 decimals (like USDC), `buyAmount: 1000000` represents **1.0 token**.

You’ll need to account for token decimals in your frontend or application logic if you want to display human-readable values.

Need help handling decimals? You can use utility libraries like:

* [`ethers.js`](https://docs.ethers.org/v5/api/utils/display-logic/#utils-formatUnits) → `formatUnits(amount, decimals)`
* [`viem`](https://viem.sh/docs/utilities/formatUnits.html) → `formatUnits(amount, decimals)`

Is it possible to quote by the `buyAmount`?

No, only quoting by `sellAmount` is supported.

The `buyAmount` parameter has been deprecated starting in v2 in favor of purely `sellAmount` for more deterministic and user-friendly behavior. Using `sellAmount` ensures any unused tokens are refunded, while `buyAmount` can result in over-purchasing due to slippage and inconsistencies across liquidity sources. Additionally, some sources (e.g., Kyber) do not support quoting by `buyAmount`, reducing available liquidity. By transitioning to `sellAmount`, we align with industry trends and offer more predictable execution for users.

Can I skip validation for the `/quote` endpoint by leaving the `taker`parameter blank?

No, the `taker` parameter is required in v2 for `/quote`. It enables us to return calldata and any issues that may have caused a failure during quote validation.

Why does the value of the `to` field in the `/swap/quote` response vary?

The `to` field value varies based on the current Settler contract address. The Settler contract is designed to be redeployed, resulting in different target addresses. See here for how to find the latest Settler address [list of current and future 0x Settler addresses](https://0x.org/docs/introduction/0x-cheat-sheet#finding-addreses-for-0x-settler-contracts).

### Best Practices[​](#best-practices "Direct link to Best Practices")

What is the best way to query swap prices for many asset pairs without exceeding the rate limit?

[Contact 0x](https://0x.org/contact) to discuss a solution that best suits your use case.

How can I display the 0x Swap Fee to my end users?

The 0x fee amount is returned in the `zeroExFee` parameter in the quotes where we charge the fee. You are responsible for ensuring your end users are aware of such fees, and may return the `amount` and `token` to your end users in your app. Read more about the `zeroExFee` parameter in the [`/quote](/docs/api#tag/Swap/operation/swap::permit2::getQuote) response.

The applicable fee for each plan is detailed in our [Pricing Page](https://0x.org/pricing).

Is there a way to sell assets via Swap API if the exact sellToken amount is not known before the transaction is executed?

Not currently, but we are exploring this feature.

How can I get the ABI for an ERC-20 contract via TypeScript?

* Do it "manually" by getting it from the appropriate chain scanner. For example on [Etherscan](https://etherscan.io/) > enter the contract address > click on the Contract in the tab section heading > Scroll down to find the Contract ABI > click on the Copy icon to copy it
* If the source code has been published to Etherscan, use the API to retrieve it: <https://docs.etherscan.io/api-endpoints/contracts>
* If the token has the abi in their github repo, programatically access it from the github repo
* Import the `erc20Abi` constant from viem: <https://wagmi.sh/core/guides/migrate-from-v1-to-v2#removed-abi-exports>

What’s the best way to access 0x trade data?

It depends on your use case — whether you're analyzing past trades or tracking them in real time.

We recommend checking out our [0x transaction data guide](/docs/developer-resources/transaction-data), which walks through two main approaches:

* **[0x Trade Analytics API](/docs/trade-analytics-api/introduction)** — Ideal for historical analysis, usage tracking, and reporting. Query trade data tied to your API key or filter by parameters like token, protocol, or time range.
* **[0x-parser](/docs/0x-swap-api/advanced-topics/0x-parser)** — A TypeScript library for decoding and interpreting real-time 0x transaction data from onchain logs. Great for custom dashboards, bots, or alerting systems.

Whether you're building internal analytics or parsing live activity onchain, this guide will help you choose the right tool for the job.

Can I detect whether a transaction originated from the 0x API by parsing transaction receipts?

It's a common question — and the short answer is: **not directly via onchain data alone.**

While all 0x API trades are settled through the 0x Settler smart contract, these transactions don’t include a unique tag or flag that explicitly ties them to the API.

That said, there are a few ways to approach attribution, depending on what you're trying to track:

**🔍 If you're trying to track your own app's activity**

* The **[0x Trade Analytics API](/docs/trade-analytics-api/introduction)** is the best place to start. It allows you to query detailed trade data associated with your API key.
* Enable onchain tagging. In your [0x Dashboard](https://dashboard.0x.org/), go to your app’s **Settings** and toggle on **“Enable onchain tagging.”** This makes it easier to filter and trace your transactions onchain later.

**🌍 If you're trying to detect any and all transactions routed via the 0x API**

* You can **monitor the 0x Settler contract** for activity, but this includes all transactions — not just those initiated via the 0x API.
* Currently, there is **no canonical event** that maps directly to “this came from the Swap API,” but we’re exploring ways to make API attribution more accessible in the future.
* If you're interested in **aggregated Swap API usage data**, we may be able to share insights or internal tools depending on your use case. [Reach out to us](/docs/introduction/community#contact-support) — we’d love to hear more about what you're trying to build.

We understand attribution is an important use case, whether you're tracking your own usage or seeking broader ecosystem insights. Don’t hesitate to [contact us](/docs/developer-resources/introduction/community#contact-support) to discuss how we can best support you.

## Gasless API[​](#gasless-api "Direct link to Gasless API")

[See here for Gasless API FAQ](/docs/gasless-api/gasless-faq)

## Trade Analytics API[​](#trade-analytics-api "Direct link to Trade Analytics API")

[See here for Trade Analytics API FAQ](/docs/trade-analytics-api/trade-faq)

## 0x Dashboard[​](#0x-dashboard "Direct link to 0x Dashboard")

Does the 0x Dashboard support having multiple user accounts for our team?

For now we only support one user per team account, but we will add support for multiple users in the coming weeks.

What is an App?

An app is a self-contained unit for each individual application that you’re building. You can set up multiple apps, each with its unique API keys and configurations on the [0x Dashboard](https://dashboard.0x.org/).

## Smart Contracts[​](#smart-contracts "Direct link to Smart Contracts")

Are the smart contracts audited?

Yes, see details of the [audits](https://github.com/0xProject/0x-settler/tree/master/audits). Checkout our [bounty program](/docs/developer-resources/bounties).

## Building with 0x[​](#building-with-0x "Direct link to Building with 0x")

My project would like to integrate 0x. How can I contact the 0x team?

We appreciate your interest in building with our APIs. To get an API key and start building for free, please create an account on the [0x Dashboard](https://dashboard.0x.org/). You may also [check out all our available plans](https://0x.org/pricing) and [contact our team](https://www.0x.org/#contact) for more custom needs. Our team will review and respond to you.

My project is interested to apply as a liquidity source in 0x ecosystem. How can I contact the 0x team?

Thank you for your interest in providing liquidity to the 0x ecosystem. Please fill out the relevant form below for our team to review and reach out to you.

* If you are looking provide [AMM Liquidity](https://forms.fillout.com/t/xrsvjHm85Hus)
* If you are looking to provide [RFQ Liquidity](https://docs.google.com/forms/d/e/1FAIpQLSen019JsWFZHluSgqSaPE_WFVc4YBtNS4EKB8ondJJ40Eh8jw/viewform)

[Previous

Issues & Error Codes](/docs/introduction/api-issues)[Next

Swap API](/docs/category/swap-api)

* [Troubleshooting](#troubleshooting)
* [Swap API](#swap-api)
  + [About Swap API](#about-swap-api)
  + [Monetizing your Swap Integration](#monetizing-your-swap-integration)
  + [Permit2 and AllowanceHolder](#permit2-and-allowanceholder)
  + [Parameter Questions](#parameter-questions)
  + [Best Practices](#best-practices)
* [Gasless API](#gasless-api)
* [Trade Analytics API](#trade-analytics-api)
* [0x Dashboard](#0x-dashboard)
* [Smart Contracts](#smart-contracts)
* [Building with 0x](#building-with-0x)

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
[https://0x.org/docs/developer-resources/faqs-and-troubleshooting#docusaurus_skipToContent_fallback](https://0x.org/docs/developer-resources/faqs-and-troubleshooting#docusaurus_skipToContent_fallback)
