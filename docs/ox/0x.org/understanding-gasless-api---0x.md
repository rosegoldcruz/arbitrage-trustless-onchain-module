# Understanding Gasless API | 0x

Understanding Gasless API | 0x




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

    - [Get started with Gasless API](/docs/gasless-api/guides/get-started-with-gasless-api)
    - [Understanding Gasless API](/docs/gasless-api/guides/understanding-gasless-api)
    - [Technical Appendix](/docs/gasless-api/guides/gasless-api-technical-appendix)
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
* Guides
* Understanding Gasless API

On this page

# Understanding Gasless API

**Description:** Learn how 0x’s Gasless API works, including the terminology, mechanics, and how to implement gasless swaps and approvals in your app.

## Why Use the Gasless API?[​](#why-use-the-gasless-api "Direct link to Why Use the Gasless API?")

In typical Web3 flows, users must pay gas fees using the network’s native token (e.g., ETH, POL) during:

1. **Token approval** – granting a contract permission to spend tokens.
2. **Swap execution** – submitting the swap transaction itself.

This requirement increases onboarding friction—especially for new users without native tokens. The **Gasless API removes that hurdle** by allowing a relayer (e.g., 0x) to cover gas costs. Users can then complete swaps without needing the native token in their wallet.

## How It Works[​](#how-it-works "Direct link to How It Works")

The Gasless API returns **indicative prices and firm quotes** for swaps. If the user accepts a quote, they sign an [EIP-712](https://eips.ethereum.org/EIPS/eip-712) message authorizing:

* A **gasless token approval** (if supported), and/or
* The **swap transaction** itself.

0x then submits the signed data as a meta-transaction on-chain and pays the gas cost.

> While “gasless” means no upfront gas from the user, gas is still consumed—just paid by a relayer like 0x. Gas fees are usually deducted from the **input token** (the token the user is selling).

**Note:** Gasless swaps work for all **non-native ERC-20 tokens**.

## Supported Tokens[​](#supported-tokens "Direct link to Supported Tokens")

Gasless functionality is split into two categories:

| Feature | Supported Tokens |
| --- | --- |
| **Gasless Approvals** | Tokens that support [EIP-2612](https://eips.ethereum.org/EIPS/eip-2612). Check supported tokens via the [API endpoint](https://0x.org/docs/api#tag/Gasless/operation/gasless::getGaslessApprovalTokens). |
| **Gasless Swaps** | Any **non-native** ERC-20 token. |

## Key Concepts[​](#key-concepts "Direct link to Key Concepts")

### Token Allowances[​](#token-allowances "Direct link to Token Allowances")

A **token allowance** lets a smart contract move a user’s tokens. For tokens that **don’t** support gasless approvals, the user must call `approve()` themselves (gasful). See [how to set token allowances](/docs/0x-swap-api/advanced-topics/how-to-set-your-token-allowances).

For gasless flows, the user **signs an EIP-712 message** instead of broadcasting a transaction.

### EIP-712: Typed Message Signing[​](#eip-712-typed-message-signing "Direct link to EIP-712: Typed Message Signing")

[EIP-712](https://eips.ethereum.org/EIPS/eip-712) enables **human-readable signatures** for structured data. Wallets can show users exactly what they're signing—crucial for both **gasless approvals** and **gasless swaps**.

### EIP-2612: Gasless Approvals[​](#eip-2612-gasless-approvals "Direct link to EIP-2612: Gasless Approvals")

[EIP-2612](https://eips.ethereum.org/EIPS/eip-2612) adds a `permit()` method to ERC-20 tokens, allowing **gasless approvals** using an EIP-712 signature. This avoids needing an `approve()` transaction.

### Permit2[​](#permit2 "Direct link to Permit2")

[Permit2](https://docs.uniswap.org/contracts/permit2/overview) is a smart contract by Uniswap that enables a universal allowance model:

* Deployed to `0x000000000022D473030F116dDEE9F6B43aC78BA3` on all chains.
* Users approve Permit2 once, and it can then authorize other contracts (like 0x’s Settler) to transfer tokens on their behalf using a signed EIP-712 message.

info

[What’s the difference between Permit (EIP-2612) and Permit2?](/docs/gasless-api/gasless-faq)

### Gasless Approvals[​](#gasless-approvals "Direct link to Gasless Approvals")

Supported if the token has `permit()` (EIP-2612). The user signs an EIP-712 message to grant allowance. This is possible for tokens that support the Permit Extension ([EIP-2612](https://eips.ethereum.org/EIPS/eip-2612)).

### Gasless Transactions[​](#gasless-transactions "Direct link to Gasless Transactions")

User signs an EIP-712 message authorizing a swap. 0x pays gas and executes on-chain via metatransactions

### Settler Metatransaction[​](#settler-metatransaction "Direct link to Settler Metatransaction")

Metatransactions are messages that authorize smart contracts to perform actions on your behalf.

Settler Metatransactions, `settler_metatransaction`, represents a type of gasless transactions returned by the Gasless API [`/gasless/quote`](/docs/api#tag/Gasless/operation/gasless::getQuote) endpoint. Settler Metatransaction leverages the [Swap API](/docs/api#tag/Swap) to fetch indicative pricing and quotes. 0x submits these transactions to the blockchain on behalf of the user.

### WETH Example[​](#weth-example "Direct link to WETH Example")

Let’s say the user wants to **sell WETH**:

* **WETH does not support EIP-2612**, so **gasless approvals are not possible**.
* However, **gasless swaps are supported** using an EIP-712 signature.
* First, [set a token allowance](/docs/0x-swap-api/advanced-topics/how-to-set-your-token-allowances) for WETH (this requires gas).
* After Permit2 has spending permission, the user can sign an **EIP-712 trade message** to execute the swap without paying gas.

## Technical Flow Diagrams[​](#technical-flow-diagrams "Direct link to Technical Flow Diagrams")

The **Gasless API** can be combined with the **Swap API** to provide flexible execution options. This allows for a seamless user experience where advanced users can choose to enable or disable Gasless execution without compromising their experience:

* Default to gasless trades when possible.
* Fallback to regular Swap API when:
  + The token is native and unsupported for gasless.
  + There’s not enough input token to cover relayer gas costs.

[Click to expand flowchart](/docs/assets/files/gasless-and-swap-flow-chart-4d17891fe034ab95ba7adbe6ff8d70d9.jpg)

![Gasless + Swap API Flow](/docs/assets/images/gasless-and-swap-flow-chart-4d17891fe034ab95ba7adbe6ff8d70d9.jpg)

## 🔍 Try It Live[​](#-try-it-live "Direct link to 🔍 Try It Live")

Want to explore this in a live app?

* 🧪 **Try Matcha Auto:** <https://matcha.xyz>
* 🎥 **Watch the demo:** [YouTube – Matcha Auto](https://youtu.be/ziV3O9QLE5U?si=orPciAj00iOWKxd4)

[Previous

Get started with Gasless API](/docs/gasless-api/guides/get-started-with-gasless-api)[Next

Technical Appendix](/docs/gasless-api/guides/gasless-api-technical-appendix)

* [Why Use the Gasless API?](#why-use-the-gasless-api)
* [How It Works](#how-it-works)
* [Supported Tokens](#supported-tokens)
* [Key Concepts](#key-concepts)
  + [Token Allowances](#token-allowances)
  + [EIP-712: Typed Message Signing](#eip-712-typed-message-signing)
  + [EIP-2612: Gasless Approvals](#eip-2612-gasless-approvals)
  + [Permit2](#permit2)
  + [Gasless Approvals](#gasless-approvals)
  + [Gasless Transactions](#gasless-transactions)
  + [Settler Metatransaction](#settler-metatransaction)
  + [WETH Example](#weth-example)
* [Technical Flow Diagrams](#technical-flow-diagrams)
* [🔍 Try It Live](#-try-it-live)

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
[https://0x.org/docs/gasless-api/guides/understanding-gasless-api#docusaurus_skipToContent_fallback](https://0x.org/docs/gasless-api/guides/understanding-gasless-api#docusaurus_skipToContent_fallback)
