# Handling API Issues and Error Codes | 0x

Handling API Issues and Error Codes | 0x




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

* [Introduction](/docs/category/introduction)
* Issues & Error Codes

On this page

# Handling API Issues and Error Codes

When working with the [0x API v2](/docs/api#tag/Swap), there are two key places to check for errors:

1. [**The `issues` object**](/docs/introduction/api-issues#issues-object): This is returned in the API response when there are validation issues with a quote. It helps identify problems such as insufficient token allowance, low balances, or invalid liquidity sources that could prevent a successful swap execution.
2. [**Error codes**](/docs/introduction/api-issues#issues-object): These are returned when there is an issue making the API request itself, such as invalid input or authorization errors.

---

## Issues Object[​](#issues-object "Direct link to Issues Object")

By examining both the `issues` object for quote validation and the error codes for request failures, developers can troubleshoot and resolve issues more efficiently, ensuring smoother transaction processes.

In rare cases where 0x cannot fully validate a quote, the API returns `true` in `issues.simulationIncomplete`. Developers are encouraged to check and address these issues before proceeding with the swap.

```
// Sample response from /swap/permit2/quote with an issues object  
{  
    "issues": {  
        "allowance": {  
            "actual": "0",  
            "spender": "0x000000000022d473030f116ddee9f6b43ac78ba3"  
        },  
        "balance": {  
            "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  
            "actual": "0",  
            "expected": "100000000"  
        },  
        "simulationIncomplete": false,  
        "invalidSourcesPassed": []  
    }  
}  

```

### Issue Types and Resolutions[​](#issue-types-and-resolutions "Direct link to Issue Types and Resolutions")

Below is a list of the common issues that may arise when using the `/price` or `/quote` endpoints, along with their causes and resolutions:

| **Issue** | **Reason** | **Details** |
| --- | --- | --- |
| **`allowance`** | The `taker` does not have sufficient token allowance to execute the swap. | The response provides the current and required allowance details. Prompt the user to set the correct token allowance. |
| **`balance`** | The `taker` does not have enough of the `sellToken` to complete the swap. | The response provides the actual and expected balances. Advise the user to ensure they have enough tokens to perform the swap. |
| **`simulationIncomplete`** | 0x cannot fully validate the transaction, often due to insufficient balance. | This doesn’t guarantee the swap will fail. Investigate if the user’s balance is low or if other conditions prevent validation. |
| **`invalidSourcesPassed`** | One or more invalid liquidity sources were included in the `excludedSources` list. | The response provides invalid sources. Remove invalid sources or check the valid list using `GET /sources`. |

This table format provides a concise and structured way to convey the relevant information about each issue, helping developers quickly understand the cause and resolution for each one.

### Best Practices for Handling Issues[​](#best-practices-for-handling-issues "Direct link to Best Practices for Handling Issues")

#### Price Requests[​](#price-requests "Direct link to Price Requests")

* **`allowance`**: If returned, prompt the user to set the appropriate token allowance before proceeding.
* **`balance`**: Avoid proceeding to the quote stage if the user does not have enough tokens, as indicated by this field.
* **`simulationIncomplete`**: Safe to ignore for price requests. This issue may arise if the `taker` address is set but has an insufficient token balance.

#### Quote Requests[​](#quote-requests "Direct link to Quote Requests")

* **`allowance`**: Ensure that users complete the allowance setup before proceeding.
* **`balance`**: This field indicates insufficient token balance; prompt the user to check their balance and retry.
* **`simulationIncomplete`**: Advise users that validation could not be completed, but the trade may still succeed.

## Error Codes[​](#error-codes "Direct link to Error Codes")

In addition to the `issues` object, the API may return specific error codes under certain conditions. If the error persists, please [contact support](https://help.0x.org/en/articles/8230055-how-to-get-support-from-the-0x-team) for assistance.

Common Error Codes

### Swap API[​](#swap-api "Direct link to Swap API")

| **Code** | **Reasons** | **Details** |
| --- | --- | --- |
| 400 | INPUT\_INVALID  SWAP\_VALIDATION\_FAILED  TOKEN\_NOT\_SUPPORTED | Ensure the API request is properly formatted.  Check that the `taker`, `sellToken`, and `buyToken` addresses are correct. For [native tokens](/docs/0x-swap-api/advanced-topics/handling-native-tokens) (on any chains we support), you can use the contract address `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`. |
| 403 | TAKER\_NOT\_AUTHORIZED\_FOR\_TRADE | The `taker` address is not authorized to make this trade. Contact [0x API Support](https://help.0x.org/en/articles/8230055-how-to-get-dev-support-from-the-0x-team) to investigate. |
| 422 | BUY\_TOKEN\_NOT\_AUTHORIZED\_FOR\_TRADE  SELL\_TOKEN\_NOT\_AUTHORIZED\_FOR\_TRADE | Ensure the `taker`, `sellToken`, and `buyToken` addresses are accurate. |
| 500 | INTERNAL\_SERVER\_ERROR  UNCATEGORIZED | An unexpected error has occurred.  Contact [0x API Support](https://help.0x.org/en/articles/8230055-how-to-get-dev-support-from-the-0x-team) to investigate. |

### Gasless API[​](#gasless-api "Direct link to Gasless API")

| Code | Reasons | Details |
| --- | --- | --- |
| 400 | INPUT\_INVALID  SWAP\_VALIDATION\_FAILED  TOKEN\_NOT\_SUPPORTED  SELL\_AMOUNT\_TOO\_SMALL  INSUFFICIENT\_BALANCE  UNABLE\_TO\_CALCULATE\_GAS\_FEE | Ensure that the API request was formatted properly.  Check that the `taker`, `sellToken`, and `buyToken` addresses are correct. For [native tokens](/docs/0x-swap-api/advanced-topics/handling-native-tokens) (on any chains we support), you can use the contract address `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`. The provided `sellAmount` may be too small.  Check that the `taker` has enough `sellToken`. |
| 403 | TAKER\_NOT\_AUTHORIZED\_FOR\_TRADE | The `taker` address is not authorized to make this trade. Contact [0x API Support](https://help.0x.org/en/articles/8230055-how-to-get-dev-support-from-the-0x-team) to investigate. |
| 404 | META\_TRANSACTION\_STATUS\_NOT\_FOUND | Check that the trade was submitted correctly. |
| 422 | BUY\_TOKEN\_NOT\_AUTHORIZED\_FOR\_TRADE  SELL\_TOKEN\_NOT\_AUTHORIZED\_FOR\_TRADE | Check that the `taker`, `sellToken`, and `buyToken` addresses are accurate. |
| 500 | INTERNAL\_SERVER\_ERROR  UNCATEGORIZED | An unexpected error has occurred.  [Contact support](https://help.0x.org/en/articles/8230055-how-to-get-dev-support-from-the-0x-team) to resolve the issue. |

[Previous

Support](/docs/introduction/community)[Next

FAQ & Troubleshooting](/docs/developer-resources/faqs-and-troubleshooting)

* [Issues Object](#issues-object)
  + [Issue Types and Resolutions](#issue-types-and-resolutions)
  + [Best Practices for Handling Issues](#best-practices-for-handling-issues)
* [Error Codes](#error-codes)
  + [Swap API](#swap-api)
  + [Gasless API](#gasless-api)

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
[https://0x.org/docs/introduction/api-issues#docusaurus_skipToContent_fallback](https://0x.org/docs/introduction/api-issues#docusaurus_skipToContent_fallback)
