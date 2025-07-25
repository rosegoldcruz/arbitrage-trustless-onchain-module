# Gasless API FAQ | 0x

Gasless API FAQ | 0x




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

  + [Introduction](/docs/gasless-api/introduction)
  + [Guides](#)
  + [API Reference](https://0x.org/docs/api#tag/Gasless)
  + [FAQ](/docs/gasless-api/gasless-faq)
* [Trade Analytics API](/docs/category/trade-analytics-api)
* [AI Tools](/docs/category/ai-tools)
* [Libraries](/docs/category/libraries)
* [Developer Resources](/docs/category/developer-resources)
* [Example Projects](https://github.com/0xProject/0x-examples)
* [Upgrading](/docs/upgrading)
* [Liquidity Providers](/docs/category/liquidity-providers)
* [Need Help?](/docs/category/need-help)

* [Gasless API](/docs/category/gasless-api)
* FAQ

# Gasless API FAQ

How do I get a list of sources the API is sourcing from?

Use the [getSources](https://0x.org/docs/api#tag/Sources) endpoint.

What chains does Gasless API support?

See the [full list of supported chains](/docs/introduction/0x-cheat-sheet#-chain-support).

Which tokens are supported by Gasless API?

**Short answer:**

Gasless API provides a gasless experience at two points of the trade experience where the user normally needs to pay gas:

* **Gasless approvals** work only for tokens listed in our [Gasless Approval Token endpoint](https://0x.org/docs/api#tag/Gasless/operation/gasless::getGaslessApprovalTokens). These are tokens that support [EIP-2612](https://eips.ethereum.org/EIPS/eip-2612).
* **Gasless swaps** work for selling any non‑native token (anything that’s an ERC‑20 or similar).

**What doesn’t work:**

* You can’t use Gasless API to sell the chain’s native coin (e.g., ETH on Mainnet, POL on Polygon). Native coins aren’t ERC‑20s, so they lack the `transferFrom` function which the metatransaction relay system underlying Gasless API utilizes. In this case, we’d recommend using the [Swap API](/docs/api#tag/Swap), wherein the user will pay for the gas of the transaction, with the chain’s native token. Otherwise, you can recommend your users to wrap their ETH into WETH (or equivalent, in other chains).

**Work‑arounds for tokens not supported by Gasles API:**

1. Use the regular Swap API instead—the user just pays gas in the native coin.
2. Or wrap the coin first (e.g., turn ETH into WETH) and then use Gasless API.

Who pays for the gas fees to allow those swaps to happen?

0x covers the gas fee up front. This cost is then wrapped into the trade and paid for in the form of the token the user is trading.

Applications may choose to sponsor transactions, in which case they will pay 0x directly, and users will not be billed on chain

Can I monetize using Gasless API?

You have full flexibility on the fees you collect on your trades.

Setup requires including the following three parameters when making a [Gasless API](/docs/api#tag/Gasless) request:

* `swapFeeRecipient` - The wallet address to receive the specified trading fees.
* `swapFeeBps` - The amount in Bps (Basis points) of the `swapFeeToken` to charge and deliver to the `swapFeeRecipient`. Denoted as an integer between 0 - 1000 where 1000 Bps represents 10%.
* `swapFeeToken` - The contract address of the token to receive trading fees in. This must be set to either the value of `buyToken` or the `sellToken`.

```
https://api.0x.org/gasless/quote                          // Request a firm quote  
?chainId=1                                                // Ethereum Mainnet  
&sellToken=0x6B175474E89094C44Da98b954EedeAC495271d0F     // Sell DAI  
&sellAmount=4000000000000000000000                        // Sell amount: 4000 (18 decimal)  
&buyToken=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE      // Buy ETH  
&taker=$USER_TAKER_ADDRESS                                // Address that will make the trade  
&swapFeeRecipient=$INTEGRATOR_WALLET_ADDRESS              // Wallet address that should receive the affiliate fees  
&swapFeeBps=100                                           // Percentage of buyAmount that should be attributed as affiliate fees  
&swapFeeToken=0x6B175474E89094C44Da98b954EedeAC495271d0F  // Receive trading fee in sellToken (DAI)  
--header '0x-api-key: [API_KEY]'                          // Replace with your own API key  
--header '0x-version: v2'                                 // API version  

```

What if my user wants to sell a native token, e.g. swap ETH for USDC, on Mainnet?

In this case, we’d recommend using the [Swap API](/docs/api#tag/Swap), wherein the user will pay for the gas of the transaction, with the chain’s native token. Otherwise, you can recommend your users to wrap their ETH into WETH (or equivalent, in other chains).

What tokens work with gasless approvals?

Gasless approvals are only supported for tokens that are listed in the [gasless approval token endpoint](https://0x.org/docs/api#tag/Gasless/operation/gasless::getGaslessApprovalTokens) we provided.

What if my user is selling a token that doesn’t support gasless approvals?

In this case, your user would need to do a standard approval transaction with Permit2. See [intructions for how to set token allowance](/docs/0x-swap-api/advanced-topics/how-to-set-your-token-allowances). If you user doesn’t have sufficient native token to pay for the approval transaction, they can use Gasless API to swap a popular token (e.g. USDC) for ETH (or the equivalent native token) on Mainnet, MATIC on Polygon, etc. Please note that the approval transaction is a one-time transaction for each new token the user sells. Once the approval transaction is mined, the user can still do gasless swaps with that token.

  

Some UIs may choose not to support tokens that do not [support gasless approvals](https://0x.org/docs/api#tag/Gasless/operation/gasless::getGaslessApprovalTokens) in order to guarantee a 100% gasless experience. However, Gasless API does not limit anyone in this manner and is strictly a choice of the developer.

How do I know if an approval is required?

Check the response from [`/gasless/quote`](/docs/api#tag/Gasless/operation/gasless::getQuote),

* If the `issues.allowance` object is not null, an allowance approval is required
* If the `approval` object is returned is not null, then a gasless approval is possible

My user is doing a swap and needs an approval - are these separate transactions? Do I need 2 signatures?

Although gasless approvals and gasless swap are bundled in the same transaction, they each require a signature for the corresponding EIP-712 object. However, you may elect to create a front-end experience wherein it appears to the user that they are signing only 1 transaction.

What does a gasless approve + swap happy path look like, using Gasless API?

See the flow charts [here](/docs/gasless-api/guides/understanding-gasless-api#technical-flow-charts).

What is the minimum amount users can trade with Gasless API?

The minimum amount will vary across chains, trade sizes and current gas conditions. When attempting to trade an amount that is too small, the API response will return an error message with the estimated minimum amount for that trade. In general, we recommend setting a minimum of $10 on Mainnet, and $1 on other chains for the best experience.

I received one of these error messages: INPUT\_INVALID, BUY\_TOKEN\_NOT\_AUTHORIZED\_FOR\_TRADE, INTERNAL\_SERVER\_ERROR. Help!

Read more about [Status Codes](/docs/gasless-api/guides/gasless-api-technical-appendix#status-code).

What’s the difference between Permit (EIP-2612) and Permit2?

While both Permit (EIP-2612) and Permit2 enable gasless-like user experiences, they serve different purposes and work under different assumptions.

**In short**: **Permit (EIP-2612)** is an extension of the ERC-20 token standard that allows gasless approvals via the Gasless API. **Permit2** is a contract that enables gasless token transfers by allowing other contracts (like 0x Settler) to move tokens on a user's behalf—once given allowance and an EIP-712 signature.

**Permit**, defined in [EIP-2612](https://eips.ethereum.org/EIPS/eip-2612), is an extension to the ERC-20 token standard that allows users to set token allowances using an EIP-712 signature—**without sending an on-chain transaction**. This means the entire approval process can be gasless. However, **Permit only works if the token explicitly supports EIP-2612**. Many older tokens, such as WETH, do not support this feature and thus require users to perform a regular `approve()` transaction that consumes gas.

On the other hand, **Permit2** is a universal approval contract created by Uniswap Labs. It allows any ERC-20 token to participate in a meta-transaction flow, even if the token doesn’t support EIP-2612. With Permit2, the user must first perform a **standard `approve()` call** (which is gasful) to give Permit2 permission to spend tokens. After that, the user can **sign EIP-712 messages** to authorize future token movements without needing additional on-chain approvals. This enables **gasless swaps going forward**, even though the initial setup requires a gasful transaction.

Permit2 is especially useful in gasless trading scenarios involving tokens that don’t support `permit()`, because it creates a consistent interface for applications like 0x to move tokens on behalf of users. It’s deployed at the same address (`0x000000000022D473030F116dDEE9F6B43aC78BA3`) across all major chains.

[Previous

Technical Appendix](/docs/gasless-api/guides/gasless-api-technical-appendix)[Next

Trade Analytics API](/docs/category/trade-analytics-api)

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
[https://0x.org/docs/gasless-api/gasless-faq#docusaurus_skipToContent_fallback](https://0x.org/docs/gasless-api/gasless-faq#docusaurus_skipToContent_fallback)
