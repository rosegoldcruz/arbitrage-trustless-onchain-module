# Upgrading to Swap API v2 | 0x

Upgrading to Swap API v2 | 0x




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
* [Example Projects](https://github.com/0xProject/0x-examples)
* [Upgrading](/docs/upgrading)

  + [To Swap API v2](/docs/upgrading/upgrading_to_swap_v2)
  + [To Gasless API v2](/docs/upgrading/upgrading_to_gasless_v2)
* [Liquidity Providers](/docs/category/liquidity-providers)
* [Need Help?](/docs/category/need-help)

* [Upgrading](/docs/upgrading)
* To Swap API v2

On this page

# Upgrading to Swap API v2

tip

0x API v1 will be sunset on April 11, 2025. To ensure uninterrupted service, please migrate to v2 before this date. If you have any questions, feel free to [contact support](/docs/introduction/community#contact-support).

0x Swap API has undergone a major upgrade that introduces new features that require a new integration. This new version offers:

* improved swap pricing, especially on large trades
* a new set of 0x smart contracts that offer secure upgradability
* increased security via the [Permit2 contract](/docs/introduction/0x-cheat-sheet#permit2-contract) or [AllowanceHolder contract](/docs/introduction/0x-cheat-sheet#allowanceholder-contract) for allowances
* improved [monetization features](/docs/0x-swap-api/guides/monetize-your-app-using-swap)
* enhanced quote validation to provide accurate gas estimates without a user balance or allowance set
* improved [error handling](/docs/introduction/api-issues)
* new [buy/sell tax support](https://0x.org/docs/developer-resources/buy-sell-tax-support)
* expanded token and chain coverage

tip

⚡️ Quicklinks

* [Demo app code](https://github.com/0xProject/0x-examples/tree/main/swap-v2-next-app)
* [Permit2 headless example](https://github.com/0xProject/0x-examples/tree/main/swap-v2-headless-example)
* [AllowanceHolder headless example](https://github.com/0xProject/0x-examples/tree/main/swap-v2-allowance-holder-headless-example)
* Try the new [Swap TypeScript SDK](https://0x.org/docs/0x-swap-api/swap-ts-sdk) which supports 0x API v2 Swap and Gasless endpoints

## API Reference[​](#api-reference "Direct link to API Reference")

Find the [latest API reference here](/docs/api).

## Summary of Design Changes[​](#summary-of-design-changes "Direct link to Summary of Design Changes")

This section showcases example requests and responses for both the Swap API v1 and v2 endpoints to illustrate updates in the shape of the query and responses made during the API upgrade:

Swap API v1

Swap API v1`/quote`

Request

```
curl --request GET  
--url https://api.0x.org/swap/v1/quote?buyToken=0x6B175474E89094C44Da98b954EedeAC495271d0F&sellToken=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&sellAmount=100000&takerAddress=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045&slippagePercentage=0.03&feeRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e&buyTokenFeePercentage=0.1&feeRecipientTradeSurplus=0xa8aac589a67ecfade31efde49a062cc21d68a64e  
--header '0x-api-key: YOUR_API_KEY'  

```

Response

```
{  
    "chainId": 1,  
    "price": "3004.35342",  
    "grossPrice": "3008.73112",  
    "estimatedPriceImpact": "0.4902",  
    "value": "100000",  
    "gasPrice": "2457320000",  
    "gas": "358839",  
    "estimatedGas": "358839",  
    "protocolFee": "0",  
    "minimumProtocolFee": "0",  
    "buyTokenAddress": "0x6b175474e89094c44da98b954eedeac495271d0f",  
    "buyAmount": "300435342",  
    "grossBuyAmount": "300873112",  
    "sellTokenAddress": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",  
    "sellAmount": "100000",  
    "grossSellAmount": "100000",  
    "sources": [  
        {  
            "name": "0x",  
            "proportion": "0"  
        },  
        {  
            "name": "Uniswap",  
            "proportion": "0"  
        },  
        {"..."}  
    ],  
    "allowanceTarget": "0x0000000000000000000000000000000000000000",  
    "sellTokenToEthRate": "1",  
    "buyTokenToEthRate": "3023.5504768532695617",  
    "to": "0xdef1c0ded9bec7f1a1670819833240f027b25eff",  
    "from": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",  
    "data": "0x415565b0000000000000000000000000eeeeeeeee....000000000000000000000000000000e7be0bf798e96f437b0d6e8",  
    "decodedUniqueId": "0x0e7be0bf798e96f437b0d6e8",  
    "guaranteedPrice": "2914.09148",  
    "orders": [  
        {  
            "type": 0,  
            "source": "Uniswap_V2",  
            "makerToken": "0x6b175474e89094c44da98b954eedeac495271d0f",  
            "takerToken": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
            "makerAmount": "300873112",  
            "takerAmount": "100000",  
            "fillData": {  
                "tokenAddressPath": [  
                    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                    "0x6b175474e89094c44da98b954eedeac495271d0f"  
                ],  
                "router": "0xf164fc0ec4e93095b804a4795bbe1e041497b92a"  
            },  
            "fill": {  
                "input": "100000",  
                "output": "300873112",  
                "adjustedOutput": "1",  
                "gas": 115000  
            }  
        }  
    ],  
    "fees": {  
        "zeroExFee": {  
            "feeType": "volume",  
            "feeToken": "0x6b175474e89094c44da98b954eedeac495271d0f",  
            "feeAmount": "437770",  
            "billingType": "on-chain"  
        }  
    },  
    "auxiliaryChainData": {}  
}  

```

Swap API v2

Swap API v2 `/quote` (Permit2)

Request

```
curl --request GET  
--url https://api.0x.org/swap/permit2/quote?chainId=1&buyToken=0x6B175474E89094C44Da98b954EedeAC495271d0F&sellToken=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&sellAmount=100000&taker=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045&swapFeeBps=10&swapFeeRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e&swapFeeToken=0x6B175474E89094C44Da98b954EedeAC495271d0F&tradeSurplusRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e&slippageBps=100  
--header '0x-api-key: YOUR_API_KEY'  
--header '0x-version: v2'  

```

Response

```
{  
    "blockNumber": "20264686",  
    "buyAmount": "300409869",  
    "buyToken": "0x6b175474e89094c44da98b954eedeac495271d0f",  
    "fees": {  
        "integratorFee": {  
            "amount": "301163",  
            "token": "0x6b175474e89094c44da98b954eedeac495271d0f",  
            "type": "volume"  
        },  
        "zeroExFee": {  
            "amount": "451744",  
            "token": "0x6b175474e89094c44da98b954eedeac495271d0f",  
            "type": "volume"  
        },  
        "gasFee": null  
    },  
    "issues": {  
        "allowance": null,  
        "balance": null,  
        "simulationIncomplete": false,  
        "invalidSourcesPassed": []  
    },  
    "liquidityAvailable": true,  
    "minBuyAmount": "297405770",  
    "permit2": null,  
    "route": {  
        "fills": [  
            {  
                "from": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "to": "0x6b175474e89094c44da98b954eedeac495271d0f",  
                "source": "SushiSwap",  
                "proportionBps": "10000"  
            }  
        ],  
        "tokens": [  
            {  
                "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "symbol": "WETH"  
            },  
            {  
                "address": "0x6b175474e89094c44da98b954eedeac495271d0f",  
                "symbol": "DAI"  
            }  
        ]  
    },  
    "sellAmount": "100000",  
    "sellToken": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",  
    "totalNetworkFee": "415281807360000",  
    "transaction": {  
        "to": "0x7f6cee965959295cc64d0e6c00d99d6532d8e86b",  
        "data": "0x1fff991f000000000000000000000...000000000000",  
        "gas": "221184",  
        "gasPrice": "1877540000",  
        "value": "100000"  
    }  
}  

```

Swap API v2`/quote` (AllowanceHolder)

Request

```
curl --request GET  
--url https://api.0x.org/swap/allowance-holder/quote?chainId=1&buyToken=0x6B175474E89094C44Da98b954EedeAC495271d0F&sellToken=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&sellAmount=100000&taker=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045&swapFeeBps=10&swapFeeRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e&swapFeeToken=0x6B175474E89094C44Da98b954EedeAC495271d0F&tradeSurplusRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e&slippageBps=100  
--header '0x-api-key: YOUR_API_KEY'  
--header '0x-version: v2'  

```

Response

```
{  
    "blockNumber": "20264713",  
    "buyAmount": "300433569",  
    "buyToken": "0x6b175474e89094c44da98b954eedeac495271d0f",  
    "fees": {  
        "integratorFee": {  
            "amount": "301187",  
            "token": "0x6b175474e89094c44da98b954eedeac495271d0f",  
            "type": "volume"  
        },  
        "zeroExFee": {  
            "amount": "451780",  
            "token": "0x6b175474e89094c44da98b954eedeac495271d0f",  
            "type": "volume"  
        },  
        "gasFee": null  
    },  
    "issues": {  
        "allowance": null,  
        "balance": null,  
        "simulationIncomplete": false,  
        "invalidSourcesPassed": []  
    },  
    "liquidityAvailable": true,  
    "minBuyAmount": "297429233",  
    "route": {  
        "fills": [  
            {  
                "from": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "to": "0x6b175474e89094c44da98b954eedeac495271d0f",  
                "source": "Uniswap_V2",  
                "proportionBps": "10000"  
            }  
        ],  
        "tokens": [  
            {  
                "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "symbol": "WETH"  
            },  
            {  
                "address": "0x6b175474e89094c44da98b954eedeac495271d0f",  
                "symbol": "DAI"  
            }  
        ]  
    },  
    "sellAmount": "100000",  
    "sellToken": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",  
    "totalNetworkFee": "783821981250000",  
    "transaction": {  
        "to": "0x0000000000001ff3684f28c67538d4d072c22734",  
        "data": "0x2213bc0b0000000000000000000...00000000",  
        "gas": "233541",  
        "gasPrice": "3356250000",  
        "value": "100000"  
    }  
}  

```

## Things to Note[​](#things-to-note "Direct link to Things to Note")

**Old (v1):**

```
curl --request GET  
https://polygon.api.0x.org/swap/v1/quote&buyTokenAddress=0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270&sellTokenAddress=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174&sellAmount=10000000&takerAddress=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045  
--header '0x-api-key: YOUR_API_KEY'  

```

**New (v2):**

```
curl --request GET  
https://api.0x.org/swap/permit2/quote?chainId=137&buyToken=0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270&sellToken=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174&sellAmount=10000000&taker=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045  
--header '0x-api-key: YOUR_API_KEY'  
--header '0x-version: v2'  

```

### Updated URLs[​](#updated-urls "Direct link to Updated URLs")

#### Unified Endpoint and Chain Designation[​](#unified-endpoint-and-chain-designation "Direct link to Unified Endpoint and Chain Designation")

The chain is no longer designated by the endpoint URL. All chains now use the same [`https://api.0x.org`](https://api.0x.org) endpoint, with the chain set via the new `chainId` query parameter:

* **Old:** `https://polygon.api.0x.org/swap/v1/quote`
* **New:** `https://api.0x.org/swap/permit2/quote?chainId=137`

### API Version Update[​](#api-version-update "Direct link to API Version Update")

The API version is no longer set in the endpoint URL. In v2, the API version is a required header parameter.

```
const headers = {  
    '0x-api-key': '[api-key]',  
    '0x-version': 'v2', // API version is a required header parameter  
};  

```

### Updated Parameter Names[​](#updated-parameter-names "Direct link to Updated Parameter Names")

Note the following parameter names have been updated in v2. See the [API reference](/docs/api) for more parameter details:

* `takerAddress` has been renamed to `taker`
* `sellTokenAddress` has been renamed to `sellToken`
* `buyTokenAddress` has been renamed to `buyToken`

### Deprecated Parameter[​](#deprecated-parameter "Direct link to Deprecated Parameter")

The `buyAmount` parameter has been deprecated in favor of purely `sellAmount` for more deterministic and user-friendly behavior. Using `sellAmount` ensures any unused tokens are refunded, while `buyAmount` can result in over-purchasing due to slippage and inconsistencies across liquidity sources. Additionally, some sources (e.g., Kyber) do not support quoting by `buyAmount`, reducing available liquidity. By transitioning to `sellAmount`, we align with industry trends and offer more predictable execution for users.

### Enhanced Security[​](#enhanced-security "Direct link to Enhanced Security")

0x V2 enhances security by moving away from unlimited approvals and now sets allowances per trade. You can choose between using [Permit2](https://0x.org/docs/api#tag/Swap/operation/swap::permit2::getPrice) (`/swap/permit2`) or [AllowanceHolder](https://0x.org/docs/api#tag/Swap/operation/swap::allowanceHolder::getPrice) (`/swap/allowance-holder`) when making a swap request. Read more about [the difference between using Permit2 and AllowanceHolder for Swap API](https://0x.org/docs/developer-resources/faqs-and-troubleshooting#permit2-and-allowanceholder).

* **Old:** `https://api.0x.org/swap/v1/quote`
* **New:** `https://api.0x.org/swap/permit2/quote` or `https://api.0x.org/swap/allowance-holder/quote`

### Token Allowances[​](#token-allowances "Direct link to Token Allowances")

For token allowances, the allowance target will no longer be the 0x Exchange Proxy, but rather either the Permit2 contract or AllowanceHolder contracts, depending on your preferred token allowance path.

### Permit2 Transactions[​](#permit2-transactions "Direct link to Permit2 Transactions")

For transactions using Permit2, you will need to sign a Permit2 EIP-712 message from the `/quote` response and append the signature length and signature data to calldata before submitting the transaction to the network. You can find a guide to do so [here](/docs/0x-swap-api/guides/swap-tokens-with-0x-swap-api#4-sign-the-permit2-eip-712-message).

### Changes in API Responses[​](#changes-in-api-responses "Direct link to Changes in API Responses")

#### Liquidity Availability[​](#liquidity-availability "Direct link to Liquidity Availability")

There is a new `liquidityAvailable` field that validates the availability of liquidity for a price or quote request. All other parameters will only be returned when this is returned as `true`.

#### Validation Changes[​](#validation-changes "Direct link to Validation Changes")

We have removed the `skipValidation` field and will always validate the quote. We will always attempt to return a valid quote even when the taker has an insufficient balance or doesn’t have a token allowance set in the Swap API.

#### Issues Object[​](#issues-object "Direct link to Issues Object")

To help provide developers a smooth build experience, 0x API v2 will do as much validation as it can and report all issues it finds in the new `issues` object. This object returns a list of potential validation issues detected with the quote. In rare cases where we are unable to validate the quote, we’ll return `true` in `issues.simulationIncomplete`. Learn more about the [new `issues` object](/docs/introduction/api-issues) and how you can use it to provide a better experience for your users.

Note the following about the `issues` object for Price and Quote:

* **Price**

  + `allowance`: If this field is not `null`, prompt the user to set the allowance on `issues.allowance.spender`
  + `balance`: If this field is not `null`, do not proceed to get a `quote`.
  + `simulationIncomplete`: This field can be ignored for `price` since when calling price means aren't close to submitting a transaction (versus calling quote). Typically `simulationIncomplete: true` won't occur if the `taker` address is set and the `taker` has a sufficient balance of the sell token.
* **Quote**

  + `allowance`: This field should not appear if the `quote` is sent after the token allowance is set.
  + `balance`: This field will not be returned if the taker has sufficient balance when the `quote` request is sent.
  + `simulationIncomplete: true`: This field will not be returned if the taker has sufficient balance when the `quote` request is sent.

## Swap TypeScript SDK[​](#swap-typescript-sdk "Direct link to Swap TypeScript SDK")

Starting with v2, we offer a TypeScript client for interacting with the 0x API. The @0x/swap-ts-sdk currently supports the "Swap" and "Gasless" endpoints of the 0x API v2. [Learn more about how to use it here.](https://0x.org/docs/0x-swap-api/swap-ts-sdk)

## Detailed Migration Guide[​](#detailed-migration-guide "Direct link to Detailed Migration Guide")

The following section overviews of how to update Swap API price and quote to handle the new v2 endpoints whether you are [using Permit2](#using-permit2) or [using AllowanceHolder](#using-allowanceholder)

tip

Read more about [What is the difference between using Permit2 and AllowanceHolder for Swap API?](/docs/developer-resources/faqs-and-troubleshooting#parameter-questions).

### Using Permit2[​](#using-permit2 "Direct link to Using Permit2")

tip

⚡️ See these steps in action in the [Permit2 headless example](https://github.com/0xProject/0x-examples/tree/main/swap-v2-headless-example)

#### Step 0. Get 0x API key[​](#step-0-get-0x-api-key "Direct link to Step 0. Get 0x API key")

* [Get a 0x API key](/introduction/getting-started)

#### Step 1. Get indicative price[​](#step-1-get-indicative-price "Direct link to Step 1. Get indicative price")

* Call `/swap/permit2/price` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-headless-example/index.ts#L62-L83))
  + Build required price params
    - Add `chainId` as new param
    - `takerAddress` has changed to `taker`
  + In the response: `sellTokenAddress` changed to `sellToken`, `buyTokenAddress` changed to `buyToken`

#### Step 2. Set token allowance[​](#step-2-set-token-allowance "Direct link to Step 2. Set token allowance")

* Check if `taker` needs to set an allowance for Permit2. If needed, set token allowance ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-headless-example/index.ts#L85-L105))
  + Use the info returned by `issues.allowance` returned by `/price` (if `taker` is set) and `/quote` which contains details of allowances that the `taker` must set for the order to execute successfully

#### Step 3. Get firm quote[​](#step-3-get-firm-quote "Direct link to Step 3. Get firm quote")

* Call `/swap/permit2/quote` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-headless-example/index.ts#L107-L122))
  + Build required quote params (price params + `taker` address)
    - Add `chainId` as new param
    - `takerAddress` has changed to `taker`
  + In the response: `sellTokenAddress` changed to `sellToken`, `buyTokenAddress` changed to `buyToken` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-headless-example/index.ts#L114-L131))

#### Step 4. Sign Permit2 EIP-712 message[​](#step-4-sign-permit2-eip-712-message "Direct link to Step 4. Sign Permit2 EIP-712 message")

* Sign the Permit2 EIP-712 message from `/quote` response
  + `signature = await signTypedDataAsync(quote.permit2.eip712);` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-headless-example/index.ts#L124-L131))
  + Make sure `PriceResponse` and `QuoteResponse` types are up-to-date

#### Step 5. Append signature length and signature data to transaction.data[​](#step-5-append-signature-length-and-signature-data-to-transactiondata "Direct link to Step 5. Append signature length and signature data to transaction.data")

* Append the signature length and signature data to the `transaction.data`([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-headless-example/index.ts#L134-L149))

#### Step 6. Submit transaction with Permit2 signature[​](#step-6-submit-transaction-with-permit2-signature "Direct link to Step 6. Submit transaction with Permit2 signature")

* Submit the transaction with Permit2 signature
  + Use `sendTransaction({account, gas, txOptions, data, value, chain)` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-headless-example/index.ts#L133-L166))
  + Note that the `/quote` response structure has changed from v1 to v2, specifically `to`, `gas` ,`data`, `value`, `gasPrice` → have moved under `quoteResponse.transaction.to`, `quoteResponse.transaction.gas`,`quoteResponse.transaction.data`, `quoteResponse.transaction.value`, `quoteResponse.transaction.gasPrice` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-headless-example/index.ts#L143-L154))

### Using AllowanceHolder[​](#using-allowanceholder "Direct link to Using AllowanceHolder")

tip

⚡️ See these steps in action in the [AllowanceHolder headless example](https://github.com/0xProject/0x-examples/tree/main/swap-v2-allowance-holder-headless-example)

#### Step 0. Get 0x API key[​](#step-0-get-0x-api-key-1 "Direct link to Step 0. Get 0x API key")

* [Get a 0x API key](/introduction/getting-started)

#### Step 1. Get indicative price[​](#step-1-get-indicative-price-1 "Direct link to Step 1. Get indicative price")

* Call `/swap/allowance-holder/price` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-allowance-holder-headless-example/index.ts#L59-L79))
  + Build required price params
    - Add `chainId` as new param
    - `takerAddress` has changed to `taker`
  + In the response: `sellTokenAddress` changed to `sellToken`, `buyTokenAddress` changed to `buyToken`

#### Step 2. Set token allowance[​](#step-2-set-token-allowance-1 "Direct link to Step 2. Set token allowance")

* Check if `taker` needs to set an allowance for AllowanceHolder. If needed, set token allowance ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-allowance-holder-headless-example/index.ts#L81-L100))
  + Use the info returned by `issues.allowance` returned by `/price` (if `taker` is set) and `/quote` which contains details of allowances that the `taker` must set for the order to execute successfully

#### Step 3. Get firm quote[​](#step-3-get-firm-quote-1 "Direct link to Step 3. Get firm quote")

* Call `/swap/allowance-holder/quote` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-allowance-holder-headless-example/index.ts#L102-L117))
  + Build required quote params (price params + `taker` address)
    - Add `chainId` as new param
    - `takerAddress` has changed to `taker`
  + In the response: `sellTokenAddress` changed to `sellToken`, `buyTokenAddress` changed to `buyToken` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-headless-example/index.ts#L114-L131))

#### Step 4. Submit transaction[​](#step-4-submit-transaction "Direct link to Step 4. Submit transaction")

* Submit the transaction using `sendTransaction()` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-allowance-holder-headless-example/index.ts#L119-L127))
  + Note that the `/quote` response structure has changed from v1 to v2, specifically `to`, `gas` ,`data`, `value`, `gasPrice` → have moved under `quoteResponse.transaction.to`, `quoteResponse.transaction.gas`,`quoteResponse.transaction.data`, `quoteResponse.transaction.value`, `quoteResponse.transaction.gasPrice` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-allowance-holder-headless-example/index.ts#L121-L122))

## Migration FAQ[​](#migration-faq "Direct link to Migration FAQ")

Should I use AllowanceHolder or Permit2 for my meta-aggregator project?

The decision when choosing between Permit2 or AllowanceHolder boils down to mainly UX and integration type.

* **AllowanceHolder** is ideal for single-signature use cases and provides a consistent user experience when aggregating across multiple sources. It also closely resembles the 0x Swap v1 integration, making it quicker to implement.
* **Permit2** is a universal standard that allows users to share token approvals across smart contracts (i.e. if users have an infinite allowance via another app, no reset is needed). However, Permit2 requires two signatures per trade (one for approval, one for the trade), which may impact user experience.

Evaluate your project’s needs and the desired user experience to make the best decision.

How can I find the latest address for the AllowanceHolder contract, and how often will it be updated?

The AllowanceHolder contract is deployed at different addresses based on the chain’s latest supported EVM hardfork. You can find the most recent addresses in the [list of deployed addresses.](https://0x.org/docs/introduction/0x-cheat-sheet#allowanceholder-address).

The AllowanceHolder address only changes when a chain adopts a higher hardfork.

In the AllowanceHolder flow, will I ever approve a different contract than where the swap transaction occurs?

No, in the AllowanceHolder flow, the allowance will be set on the AllowanceHolder contract, and the `transaction.to` field will also point to the AllowanceHolder. The only exception is when the sell token is ETH, as no allowance is needed for ETH transactions. In that case, the `transaction.to` field will be the address of the most recent Settler contract.

You will never need to approve one contract and send swap calldata to another. For more information, refer to the [0x Settler documentation](https://github.com/0xProject/0x-settler?tab=readme-ov-file#how-do-i-find-the-most-recent-deployment).

If an allowance is needed when using AllowanceHolder, which contract will `issues.allowance.spender` return back?

The AllowanceHolder contract will be returned.

Can I skip validation for the `/quote` endpoint by leaving the `taker`parameter blank?

No, the `taker` parameter is required in v2 for `/quote`. It enables us to return calldata and any issues that may have caused a failure during quote validation.

Will the `/price` endpoint include RFQ if I leave the `taker` parameter blank?

Yes, RFQ will be included in the response from the `/price` endpoint even if the `taker` parameter is left blank. The `taker` parameter is optional for this endpoint.

[Previous

Upgrading to 0x API v2](/docs/upgrading)[Next

To Gasless API v2](/docs/upgrading/upgrading_to_gasless_v2)

* [API Reference](#api-reference)
* [Summary of Design Changes](#summary-of-design-changes)
* [Things to Note](#things-to-note)
  + [Updated URLs](#updated-urls)
  + [API Version Update](#api-version-update)
  + [Updated Parameter Names](#updated-parameter-names)
  + [Deprecated Parameter](#deprecated-parameter)
  + [Enhanced Security](#enhanced-security)
  + [Token Allowances](#token-allowances)
  + [Permit2 Transactions](#permit2-transactions)
  + [Changes in API Responses](#changes-in-api-responses)
* [Swap TypeScript SDK](#swap-typescript-sdk)
* [Detailed Migration Guide](#detailed-migration-guide)
  + [Using Permit2](#using-permit2)
  + [Using AllowanceHolder](#using-allowanceholder)
* [Migration FAQ](#migration-faq)

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
[https://0x.org/docs/upgrading/upgrading_to_swap_v2#permit2](https://0x.org/docs/upgrading/upgrading_to_swap_v2#permit2)
