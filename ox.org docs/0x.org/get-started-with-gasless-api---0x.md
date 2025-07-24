# Get started with Gasless API | 0x

Get started with Gasless API | 0x




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
* Get started with Gasless API

On this page

# Get started with Gasless API

*Learn how to send your first Gasless API request.*

## About Gasless API[​](#about-gasless-api "Direct link to About Gasless API")

[Gasless API](/docs/gasless-api/introduction) allows developers to create the smoothest trading experience in DeFi by abstracting away the complexities related to approvals, allowances, and swaps for their users.

Enabling Gasless API in your app allows you to:

* build more intuitive user interfaces and user flows in your applications
* improve your conversion funnel drop-offs due to insufficient gas, and
* set yourself up to easily onboard the next wave of users into Web3.

Make sure to read [Understanding Gasless API](/docs/gasless-api/guides/understanding-gasless-api) for an in-depth understanding of how it works, key terms, and technical flow charts for how to implement in-app.

## Playground[​](#playground "Direct link to Playground")

Try this code example directly in your browser—no installation needed!

## Gasless swaps in 4 Steps[​](#gasless-swaps-in-4-steps "Direct link to Gasless swaps in 4 Steps")

0. Get a 0x API key
1. Get an indicative price using `/gasless/price`
2. Get a firm quote using `/gasless/quote`
3. Submit the transaction using `/gasless/submit`
   a. Sign the gasless approval object (if applicable)
   b. Sign the trade object
   c. Split the signatures
   d. Package signed objects into a format that can be POST to /submit
   e. Compute trade hash
4. Check the trade status using `/gasless/status/{tradeHash}`

tip

Checkout the [Gasless API Runnable Headless Example](https://github.com/0xProject/0x-examples/tree/main/gasless-v2-headless-example) to see these steps in action

## 0. Before you begin[​](#0-before-you-begin "Direct link to 0. Before you begin")

### Get a 0x API key[​](#get-a-0x-api-key "Direct link to Get a 0x API key")

Every call to a 0x API must include a 0x API key. Get one from the [0x Dashboard](https://go.0x.org/create-account-txrelay-z).

### Enable Gasless API from your dashboard[​](#enable-gasless-api-from-your-dashboard "Direct link to Enable Gasless API from your dashboard")

You will be able to enable Gasless API in your app from "App Settings" in your [0x dashboard](https://dashboard.0x.org/). You can enable it for any active apps you have (see screenshot).

![](/docs/assets/images/0x-dashboard-create-app-screen-edb0e80ff32b7c681a1df68a9120fd9c.png)

## 1. Get an indicative price[​](#1-get-an-indicative-price "Direct link to 1. Get an indicative price")

Use [`/gasless/price`](/docs/api#tag/Gasless/operation/gasless::getPrice) to get the indicative price. This is used when the user is just *browsing* for the price they could receive on the specified asset pair, but they are not ready to submit the quote yet.

This endpoint responds with pricing information, but the response does not contain a full 0x order, so it does not constitute a full transaction that can be submitted to the Ethereum network (you must use [`/gasless/quote`](/docs/api#tag/Gasless/operation/gasless::getQuote) for this). Think of `/price` as the the "read-only" version of `/quote`.

See other user flows [here](/docs/gasless-api/guides/understanding-gasless-api#technical-flow-charts).

### Example request[​](#example-request "Direct link to Example request")

Here is an example indicative price request to sell 100 [USDC](https://basescan.org/address/0x833589fcd6edb6e08f4c7c32d4f71b54bda02913) for [WETH](https://basescan.org/token/0x4200000000000000000000000000000000000006) using `/price` on Base (8453):

```
https://api.0x.org/gasless/price                      // Request an indicative price  
?sellToken=0x833589fcd6edb6e08f4c7c32d4f71b54bda02913 // Sell USDC  
&sellAmount=100000000                                 // Sell amount 100 USDC (6 decimals)  
&buyToken=0x4200000000000000000000000000000000000006  // Buy WETH  
&takerAddress=$USER_TAKER_ADDRESS                     // Address that will make the trade  
--header '0x-api-key: [API_KEY]'                      // Replace with your own API key  
--header '0x-version: v2'                             // API version  

```

### Sample cURL request[​](#sample-curl-request "Direct link to Sample cURL request")

```
curl --request GET \  
  --url 'https://api.0x.org/gasless/price?chainId=8453&sellToken=0x833589fcd6edb6e08f4c7c32d4f71b54bda02913&buyToken=0x4200000000000000000000000000000000000006&sellAmount=100000&taker=<TAKER_ADDRESS>' \  
  --header '0x-api-key: <API_KEY>'  
  --header '0x-version: v2'  

```

### Example response[​](#example-response "Direct link to Example response")

```
{  
    "blockNumber": "17225085",  
    "buyAmount": "24516376467802",  
    "buyToken": "0x4200000000000000000000000000000000000006",  
    "fees": {  
        "integratorFee": null,  
        "zeroExFee": {  
            "amount": "150",  
            "token": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",  
            "type": "volume"  
        },  
        "gasFee": {  
            "amount": "16279",  
            "token": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",  
            "type": "gas"  
        }  
    },  
    "issues": {  
        "allowance": {  
            "actual": "0",  
            "spender": "0x000000000022d473030f116ddee9f6b43ac78ba3"  
        },  
        "balance": null,  
        "simulationIncomplete": false,  
        "invalidSourcesPassed": []  
    },  
    "liquidityAvailable": true,  
    "minBuyAmount": "24442827338399",  
    "route": {  
        "fills": [  
            {  
                "from": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",  
                "to": "0x4200000000000000000000000000000000000006",  
                "source": "PancakeSwap_V2",  
                "proportionBps": "10000"  
            }  
        ],  
        "tokens": [  
            {  
                "address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",  
                "symbol": "USDC"  
            },  
            {  
                "address": "0x4200000000000000000000000000000000000006",  
                "symbol": "WETH"  
            }  
        ]  
    },  
    "sellAmount": "99850",  
    "sellToken": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",  
    "target": "0xca11bde05977b3631167028862be2a173976ca11",  
    "zid": "0x0428a9c5f42998e4e00237fe"  
}  

```

## 2. Get a firm quote[​](#2-get-a-firm-quote "Direct link to 2. Get a firm quote")

When the user has found a price they are happy with and are ready to fill a quote, they should request a firm quote from Gasless API using the [`/gasless/quote`](/docs/api#tag/Gasless/operation/gasless::getQuote) endpoint. At this point, the taker is making a soft commitment to fill the suggested orders, and understands they may be penalized by the [Market Maker](/docs/developer-resources/glossary#maker) if they do not.

tip

Quotes expire in ~ 30s in order to ensure freshness. Make sure to take this into account when building your app with a timer and/or automatic refresh.

### Example request[​](#example-request-1 "Direct link to Example request")

Here is an example to fetch a firm quote to sell 100 USDC (supports Permit) for WETH (does not support Permit) using `/quote` on Polygon (137):

```
https://api.0x.org/gasless/quote                       // Request a fiirm quote  
?sellToken=0x833589fcd6edb6e08f4c7c32d4f71b54bda02913  // Sell USDC  
&sellAmount=100000000                                  // Sell amount 100 USDC (6 decimals)  
&buyToken=0x4200000000000000000000000000000000000006   // Buy WETH  
&takerAddress=$USER_TAKER_ADDRESS                      // Address that will make the trade  
--header '0x-api-key: [API_KEY]'                       // Replace with your own API key  
--header '0x-version: v2'                              // API version  

```

### Sample cURL request[​](#sample-curl-request-1 "Direct link to Sample cURL request")

```
curl --request GET  
https://api.0x.org/gasless/quote?chainId=137&buyToken=0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270&sellToken=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174&sellAmount=10000000&taker=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045&swapFeeBps=10&swapFeeRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e&swapFeeToken=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174&tradeSurplusRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e  
--header '0x-api-key: YOUR_API_KEY'  
--header '0x-version: v2'  
  

```

### Example response[​](#example-response-1 "Direct link to Example response")

```
{  
    "approval": {  
        "type": "permit",  
        "hash": "0xbf16458c9666dea26c2c810a64a5e9525d3fe79790038cd86a50608ae2dcd764",  
        "eip712": {  
            "types": {  
                "EIP712Domain": [  
                    {  
                        "name": "name",  
                        "type": "string"  
                    },  
                    {  
                        "name": "version",  
                        "type": "string"  
                    },  
                    {  
                        "name": "verifyingContract",  
                        "type": "address"  
                    },  
                    {  
                        "name": "salt",  
                        "type": "bytes32"  
                    }  
                ],  
                "Permit": [  
                    {  
                        "name": "owner",  
                        "type": "address"  
                    },  
                    {  
                        "name": "spender",  
                        "type": "address"  
                    },  
                    {  
                        "name": "value",  
                        "type": "uint256"  
                    },  
                    {  
                        "name": "nonce",  
                        "type": "uint256"  
                    },  
                    {  
                        "name": "deadline",  
                        "type": "uint256"  
                    }  
                ]  
            },  
            "domain": {  
                "name": "USD Coin (PoS)",  
                "version": "1",  
                "verifyingContract": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
                "salt": "0x0000000000000000000000000000000000000000000000000000000000000089"  
            },  
            "message": {  
                "owner": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",  
                "spender": "0x000000000022d473030f116ddee9f6b43ac78ba3",  
                "value": "115792089237316195423570985008687907853269984665640564039457584007913129639935",  
                "nonce": 0,  
                "deadline": "1720478400"  
            },  
            "primaryType": "Permit"  
        }  
    },  
    "blockNumber": "59125336",  
    "buyAmount": "19821286934697663036",  
    "buyToken": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",  
    "fees": {  
        "integratorFee": {  
            "amount": "10000",  
            "token": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
            "type": "volume"  
        },  
        "zeroExFee": {  
            "amount": "15000",  
            "token": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
            "type": "volume"  
        },  
        "gasFee": {  
            "amount": "11585",  
            "token": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
            "type": "gas"  
        }  
    },  
    "issues": {  
        "allowance": {  
            "actual": "0",  
            "spender": "0x000000000022d473030f116ddee9f6b43ac78ba3"  
        },  
        "balance": null,  
        "simulationIncomplete": false,  
        "invalidSourcesPassed": []  
    },  
    "liquidityAvailable": true,  
    "minBuyAmount": "19761823073893570047",  
    "route": {  
        "fills": [  
            {  
                "from": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
                "to": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",  
                "source": "Dfyn",  
                "proportionBps": "250"  
            },  
            {  
                "from": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
                "to": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",  
                "source": "Uniswap_V3",  
                "proportionBps": "9750"  
            },  
            {  
                "from": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",  
                "to": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",  
                "source": "WOOFi_V2",  
                "proportionBps": "9306"  
            },  
            {  
                "from": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",  
                "to": "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619",  
                "source": "Uniswap_V3",  
                "proportionBps": "444"  
            },  
            {  
                "from": "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619",  
                "to": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",  
                "source": "Uniswap_V3",  
                "proportionBps": "444"  
            }  
        ],  
        "tokens": [  
            {  
                "address": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
                "symbol": "USDC"  
            },  
            {  
                "address": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",  
                "symbol": "USDC"  
            },  
            {  
                "address": "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619",  
                "symbol": "WETH"  
            },  
            {  
                "address": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",  
                "symbol": "WMATIC"  
            }  
        ]  
    },  
    "sellAmount": "9975000",  
    "sellToken": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
    "target": "0xca11bde05977b3631167028862be2a173976ca11",  
    "trade": {  
        "type": "settler_metatransaction",  
        "hash": "0x102c2f33fb20988e171393bc5d7a497705a69b57e6d3116337b0b254adf481a7",  
        "eip712": {  
            "types": {  
                "PermitWitnessTransferFrom": [  
                    {  
                        "name": "permitted",  
                        "type": "TokenPermissions"  
                    },  
                    {  
                        "name": "spender",  
                        "type": "address"  
                    },  
                    {  
                        "name": "nonce",  
                        "type": "uint256"  
                    },  
                    {  
                        "name": "deadline",  
                        "type": "uint256"  
                    },  
                    {  
                        "name": "slippageAndActions",  
                        "type": "SlippageAndActions"  
                    }  
                ],  
                "TokenPermissions": [  
                    {  
                        "name": "token",  
                        "type": "address"  
                    },  
                    {  
                        "name": "amount",  
                        "type": "uint256"  
                    }  
                ],  
                "SlippageAndActions": [  
                    {  
                        "name": "recipient",  
                        "type": "address"  
                    },  
                    {  
                        "name": "buyToken",  
                        "type": "address"  
                    },  
                    {  
                        "name": "minAmountOut",  
                        "type": "uint256"  
                    },  
                    {  
                        "name": "actions",  
                        "type": "bytes[]"  
                    }  
                ],  
                "EIP712Domain": [  
                    {  
                        "name": "name",  
                        "type": "string"  
                    },  
                    {  
                        "name": "chainId",  
                        "type": "uint256"  
                    },  
                    {  
                        "name": "verifyingContract",  
                        "type": "address"  
                    }  
                ]  
            },  
            "domain": {  
                "name": "Permit2",  
                "chainId": 137,  
                "verifyingContract": "0x000000000022d473030f116ddee9f6b43ac78ba3"  
            },  
            "message": {  
                "permitted": {  
                    "token": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
                    "amount": "10000000"  
                },  
                "spender": "0xf9332450385291b6dce301917af6905e28e8f35f",  
                "nonce": "2241959297937691820908574931991585",  
                "deadline": "1720478100",  
                "slippageAndActions": {  
                    "recipient": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",  
                    "buyToken": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",  
                    "minAmountOut": "19761823073893570047",  
                    "actions": [  
                        "0x0dfeb419000000000000000000000000f9332450385291b6dce301917af6905e28e8f35f0000000000000000000000002791bca1f2de4661ed88a30c99a7a9449aa8417400000000000000000000000000000000000000000000000000000000009896800000000000000000000000000000000000006e898131631616b1779bad70bc2100000000000000000000000000000000000000000000000000000000668c6994",  
                        "0x38c9c1470000000000000000000000002791bca1f2de4661ed88a30c99a7a9449aa84174000000000000000000000000000000000000000000000000000000000000000b0000000000000000000000002791bca1f2de4661ed88a30c99a7a9449aa84174000000000000000000000000000000000000000000000000000000000000002400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000044a9059cbb0000000000000000000000009f6601854dee374b1bfaf6350ffd27a97309d431000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  
                        "0x38c9c1470000000000000000000000002791bca1f2de4661ed88a30c99a7a9449aa84174000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000002791bca1f2de4661ed88a30c99a7a9449aa84174000000000000000000000000000000000000000000000000000000000000002400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000044a9059cbb000000000000000000000000a8aac589a67ecfade31efde49a062cc21d68a64e000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  
                        "0x38c9c1470000000000000000000000002791bca1f2de4661ed88a30c99a7a9449aa84174000000000000000000000000000000000000000000000000000000000000000f0000000000000000000000002791bca1f2de4661ed88a30c99a7a9449aa84174000000000000000000000000000000000000000000000000000000000000002400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000044a9059cbb0000000000000000000000009f6601854dee374b1bfaf6350ffd27a97309d431000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  
                        "0x103b48be000000000000000000000000f9332450385291b6dce301917af6905e28e8f35f0000000000000000000000002791bca1f2de4661ed88a30c99a7a9449aa8417400000000000000000000000000000000000000000000000000000000000000fa000000000000000000000000d776c65b2a7a5832b4172742bf8c40cc062c678e0000000000000000000000000000000000000000000000000000000000001e000000000000000000000000000000000000000000000000000000000000000000",  
                        "0x8d68a156000000000000000000000000f9332450385291b6dce301917af6905e28e8f35f000000000000000000000000000000000000000000000000000000000000271000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002c2791bca1f2de4661ed88a30c99a7a9449aa84174000000643c499c542cef5e3811e1192ce70d8cc03d5c33590000000000000000000000000000000000000000",  
                        "0x38c9c1470000000000000000000000003c499c542cef5e3811e1192ce70d8cc03d5c335900000000000000000000000000000000000000000000000000000000000025490000000000000000000000004c4af8dbc524681930a27b2f1af5bcc8062e6fb7000000000000000000000000000000000000000000000000000000000000004400000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000c47dc203820000000000000000000000003c499c542cef5e3811e1192ce70d8cc03d5c33590000000000000000000000000d500b1d8e8ef31e21c99d1db9a6444d3adf127000000000000000000000000000000000000000000000000000000000008da4f70000000000000000000000000000000000000000000000000000000000000000000000000000000000000000f9332450385291b6dce301917af6905e28e8f35f0000000000000000000000005e01d320e95133d80dd59a2191c95728fa69036d00000000000000000000000000000000000000000000000000000000",  
                        "0x8d68a156000000000000000000000000f9332450385291b6dce301917af6905e28e8f35f000000000000000000000000000000000000000000000000000000000000271000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002c3c499c542cef5e3811e1192ce70d8cc03d5c3359000000647ceb23fd6bc0add59e62ac25578270cff1b9f6190000000000000000000000000000000000000000",  
                        "0x8d68a156000000000000000000000000f9332450385291b6dce301917af6905e28e8f35f000000000000000000000000000000000000000000000000000000000000271000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002c7ceb23fd6bc0add59e62ac25578270cff1b9f619000001f40d500b1d8e8ef31e21c99d1db9a6444d3adf12700000000000000000000000000000000000000000",  
                        "0xc876d21d000000000000000000000000a8aac589a67ecfade31efde49a062cc21d68a64e0000000000000000000000000d500b1d8e8ef31e21c99d1db9a6444d3adf1270000000000000000000000000000000000000000000000001136817746ac32f00"  
                    ]  
                }  
            },  
            "primaryType": "PermitWitnessTransferFrom"  
        }  
    }  
}  

```

### Response details[​](#response-details "Direct link to Response details")

If liquidity is available, 2 objects may be returned:

* `approval`: This is the "approval" object. If we are able to initiate a gasless approval for the sell token, this object will contain the necessary information to process a gasless approval. See the quote response [here](/docs/api#tag/Gasless/operation/gasless::getQuote).
* `trade`: This is the "trade" object which contains the necessary information to process a gasless trade. See the quote response [here](/docs/api#tag/Gasless/operation/gasless::getQuote).

## 3. Submit transaction[​](#3-submit-transaction "Direct link to 3. Submit transaction")

When user accepts the quote and wants to submit the trade, use [`/gasless/submit`](/docs/api#tag/Gasless/operation/gasless::submit) to send both signatures back along with the payload from `/gasless/quote`.

In order to submit the trade, we must complete the following:

* [Sign the gasless approval](/docs/gasless-api/guides/gasless-api-technical-appendix#sign-gasless-approval-object)
* [Sign the gasless trade object](/docs/gasless-api/guides/gasless-api-technical-appendix#sign-trade-object)
* [Split signatures for both signed objects](/docs/gasless-api/guides/gasless-api-technical-appendix#splitting-signatures)
* [Package both signed objects in a format that is acceptable to POST to /submit](/docs/gasless-api/guides/gasless-api-technical-appendix#post-the-split-signatures-to-)

### Example request[​](#example-request-2 "Direct link to Example request")

```
curl -X POST '<https://api.0x.org/gasless/submit>' --header '0x-api-key: <API_KEY>' --header '0x-version: v2' --data '{  
 "trade": {  
   "type": "settler_metatransaction", // this is trade.type from the /quote endpoint  
   "eip712": { /* this is trade.eip712 from the /quote endpoint */ },  
   "signature": {  
     "v": 28,  
     "r": "0xeaad7568c0d17ad9e1043a4dd41ce294ed51792a0fb8bed3a3318f7e1df3ff88",  
     "s": "0x09444d25869d91946d7c26f9e5448c7fea369ba9c90deac1d761261565c487d2",  
     "signatureType": 2  
    }  
  },  
 "approval":{  
     "type": "permit", // this is approval.type from the /quote endpoint  
     "eip712": {/* this is approval.eip712 from the /quote endpoint */},  
     "signature": {  
       "v": 27,  
       "r": "0xa1be4e6177d95f7e634d7cf8f93021b96e5e4f3d4d8605e85204b97d4a4060eb",  
       "s": "0x371e85adcfa9a5d0f53cc9f467a4230305899e4a18c0174466b8da784a4f9c81",  
       "signatureType": 2  
    }  
  }  
}'  

```

### Example response[​](#example-response-2 "Direct link to Example response")

```
{  
    "tradeHash": "0xcb3285b35c024fca76037bea9ea4cb68645fed3bdd84030956577de2f1592aa9",  
    "type": "settler_metatransaction",  
    "zid": "0x111111111111111111111111"  
}  

```

## 4. Check trade status[​](#4-check-trade-status "Direct link to 4. Check trade status")

Once the user has signed, split, and submitted both signatures - gasless approval (if applicable) and gasless trade - and a `tradeHash` is returned from `/submit`, you can poll [`/gasless/status/{tradeHash}`](/docs/api#tag/Gasless/operation/gasless::getStatus) to check the status of the trade.

### Example request[​](#example-request-3 "Direct link to Example request")

```
curl '<https://api.0x.org/gasless/status/0x955f2009cc0fafa4f37de4ff5220a3d9028b4cf47f66bbeb09a916cc09fefbc7>' \\  
--header '0x-api-key: <API_KEY>' --header '0x-version: v2'  

```

### Example response[​](#example-response-3 "Direct link to Example response")

```
// succeeded means it has been included in a block  
checks:  {  
  status: "succeeded",  
  transactions: [  
    {  
      hash: "0xc619aae86b1fbbb7418ab09cd849a21e4f0c07a316f87ec991ee6639fec67f5b",  
      timestamp: 1721085056563,  
    }  
  ],  
  zid: "0xd480bf2cca5769626b4549c7",  
}  
  
// confirmed means it has at least 3 confirmations onchain  
checks:  {  
  status: "confirmed",  
  transactions: [  
    {  
      hash: "0xc619aae86b1fbbb7418ab09cd849a21e4f0c07a316f87ec991ee6639fec67f5b",  
      timestamp: 1721085056563,  
    }  
  ],  
  zid: "0x67e11e02ba701a762e58ebe4",  
}  

```

If you receive an error response, see the [`/status` response in the Gasless API reference](/docs/api#tag/Gasless/operation/gasless::getStatus)

Once the trade is successful, you can display the transaction confirmation to your user.

## Learn more[​](#learn-more "Direct link to Learn more")

* 👉 Try this runnable [(Code) Gasless Headless Example](https://github.com/0xProject/0x-examples/tree/main/gasless-v2-headless-example) to see all these steps in action
* [(Guide) How to integrate Gasless API](/docs/tx-relay-api/guides/build-a-dapp-with-tx-relay-api)
* [(Code) Next.js 0x Gasless Demo App](https://github.com/0xProject/0x-examples/tree/main/tx-relay-next-app)
* [(Guide) Understanding Gasless API](/docs/gasless-api/guides/understanding-gasless-api)
* [Gasless FAQ](/docs/gasless-api/tx-relay-faq)

[Previous

Introduction](/docs/gasless-api/introduction)[Next

Understanding Gasless API](/docs/gasless-api/guides/understanding-gasless-api)

* [About Gasless API](#about-gasless-api)
* [Playground](#playground)
* [Gasless swaps in 4 Steps](#gasless-swaps-in-4-steps)
* [0. Before you begin](#0-before-you-begin)
  + [Get a 0x API key](#get-a-0x-api-key)
  + [Enable Gasless API from your dashboard](#enable-gasless-api-from-your-dashboard)
* [1. Get an indicative price](#1-get-an-indicative-price)
  + [Example request](#example-request)
  + [Sample cURL request](#sample-curl-request)
  + [Example response](#example-response)
* [2. Get a firm quote](#2-get-a-firm-quote)
  + [Example request](#example-request-1)
  + [Sample cURL request](#sample-curl-request-1)
  + [Example response](#example-response-1)
  + [Response details](#response-details)
* [3. Submit transaction](#3-submit-transaction)
  + [Example request](#example-request-2)
  + [Example response](#example-response-2)
* [4. Check trade status](#4-check-trade-status)
  + [Example request](#example-request-3)
  + [Example response](#example-response-3)
* [Learn more](#learn-more)

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
[https://0x.org/docs/gasless-api/guides/get-started-with-gasless-api#docusaurus_skipToContent_fallback](https://0x.org/docs/gasless-api/guides/get-started-with-gasless-api#docusaurus_skipToContent_fallback)
