# Troubleshooting Swap API | 0x

Troubleshooting Swap API | 0x




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
* Troubleshooting Swap API

On this page

# Troubleshooting Swap API

## Swap Requirements[​](#swap-requirements "Direct link to Swap Requirements")

Here's a quick pre-flight checklist of things that need to be in order for a swap to properly execute.

## API Issues[​](#api-issues "Direct link to API Issues")

See [API Issues](/docs/introduction/api-issues) for a full list of common 0x issues and how to resolve them.

## Sufficient Liquidity[​](#sufficient-liquidity "Direct link to Sufficient Liquidity")

Check the value returned by the `liquidityAvailable` field that validates the availability of liquidity for a price or quote request. All other parameters will only be returned when this is returned as `true`.

## Balances and Allowances[​](#balances-and-allowances "Direct link to Balances and Allowances")

The taker (the address which holds the `sellToken` balance and is executing the swap transaction) should hold at *least* the `sellAmount` of `sellToken`. The taker also should approve the `issues.allowance.spender` (typically the Permit2 contract) to spend at least the same amount for that token.

## Gas Limits[​](#gas-limits "Direct link to Gas Limits")

The transaction needs to be submitted with enough gas. Due to the nondeterministic nature of the on-chain settlement process, the swap may require more than what an `eth_estimateGas` RPC call returns. The quoted response will return `transacation.gas` which is the estimated limit that should be used to send the transaction to guarntee settlement. Any unused gas will be refunded to the transaction submitter.

## Gas Price[​](#gas-price "Direct link to Gas Price")

Swap quotes are based off liquidity available at quote time and the transactions are designed to revert if a change in liquidity causes the price to drop below a chosen threshold. This is more likely to happen as the the delay increases between generating a quote and the transaction being mined. Submitting with a "fast" gas price will typically give your transaction priority with miners so the price has less chance of moving.

## Slippage Tolerance[​](#slippage-tolerance "Direct link to Slippage Tolerance")

The slippage tolerance is determined by the `slippageBps` query parameter, whose possible values are [0...10000]. It indicates the maximum acceptable slippage of the `buyToken` in Bps. If this parameter is set to 0, no slippage will be tolerated. If not provided, the default slippage tolerance is 100Bps (= 1% slippage tolerance).

Depending on the network/chain you're using and tokens you're swapping, liquidity may be more shallow or volatile and the default 1% slippage tolerance may be too low. You can experiment with higher `slippageBps` values until the transaction succeeds, but understand that this also exposes your swap to potentially settling at what may no longer be considered a fair price.

## Generated Signature[​](#generated-signature "Direct link to Generated Signature")

Before submitting the quote order to the blockchain, you need to sign the `permit2.eip712` object from your quote response. Make sure the generated siganture is formatted properly.

The standard encoding of a signature in Ethereum decomposes the secp256k1 signature into 3 values: `r`, `s`, and `v`.
*Typically* these are ordered as `v`, `r`, `s`, but Permit2 requires that they be ordered as `r`, `s`, and `v`, where

* `r` is less than `secp256k1n`
* `s` is less than `secp256k1n / 2 + 1`, and
* `v` is either `0` or `1` to indicate the sign (or equivalently the parity) of the `y` coordinate. *However*, the convention on the EVM is that `v` is actually encoded as `27 + v` (i.e. either 27 or 28). Make sure your signature adds 27 to `v`

Then, all 3 values are packed and encoded as 65 bytes (bytes 0 through 31 represent `r`, 32 through 63 represent `s`, and byte 64 represents `v`).

## More Resources[​](#more-resources "Direct link to More Resources")

For the Troubleshooting list, see [FAQs & Troubleshooting](/docs/developer-resources/faqs-and-troubleshooting)

[Previous

Monetize your app](/docs/0x-swap-api/guides/monetize-your-app-using-swap)[Next

Smart Wallet & Multi-Sig Wallet Integration](/docs/0x-swap-api/guides/smart-contract-wallet-integration)

* [Swap Requirements](#swap-requirements)
* [API Issues](#api-issues)
* [Sufficient Liquidity](#sufficient-liquidity)
* [Balances and Allowances](#balances-and-allowances)
* [Gas Limits](#gas-limits)
* [Gas Price](#gas-price)
* [Slippage Tolerance](#slippage-tolerance)
* [Generated Signature](#generated-signature)
* [More Resources](#more-resources)

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
[https://0x.org/docs/0x-swap-api/guides/troubleshooting-swap-api#docusaurus_skipToContent_fallback](https://0x.org/docs/0x-swap-api/guides/troubleshooting-swap-api#docusaurus_skipToContent_fallback)
