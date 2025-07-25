# Upgrading to Gasless API v2 | 0x

Upgrading to Gasless API v2 | 0x




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
* To Gasless API v2

On this page

# Upgrading to Gasless API v2

tip

0x API v1 will be sunset on April 11, 2025. To ensure uninterrupted service, please migrate to v2 before this date. If you have any questions, feel free to [contact support](/docs/introduction/community#contact-support).

0x Gasless API has undergone a major upgrade that introduces new features that require a new integration. This new version offers:

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

* [Gasless v2 headless example](https://github.com/0xProject/0x-examples/tree/main/gasless-v2-headless-example)
* Try the new [Swap TypeScript SDK](https://0x.org/docs/0x-swap-api/swap-ts-sdk) which supports 0x API v2 Swap and Gasless endpoints

## API Reference[​](#api-reference "Direct link to API Reference")

Find the [latest API reference here](/docs/api).

## Summary of Design Changes[​](#summary-of-design-changes "Direct link to Summary of Design Changes")

This section showcases example requests and responses for both the v1 and v2 endpoints to illustrate updates in the shape of the query and responses made during the API upgrade:

Gasless API v1 `/quote`

Request

```
curl --request GET  
--url https://api.0x.org/tx-relay/v1/swap/quote?buyToken=0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270&sellAmount=100000000&sellToken=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174&takerAddress=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045&feeSellTokenPercentage=0.01&feeRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e&feeRecipientTradeSurplus=0xa8aac589a67ecfade31efde49a062cc21d68a64e  
--header '0x-api-key: <API_KEY>' \  
--header '0x-chain-id: 137'  

```

Response

```
{  
    "allowanceTarget": "0xdef1c0ded9bec7f1a1670819833240f027b25eff",  
    "buyAmount": "199374163715665946737",  
    "buyTokenAddress": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",  
    "estimatedPriceImpact": "0.1035",  
    "fees": {  
        "zeroExFee": {  
            "billingType": "on-chain",  
            "feeAmount": "150000",  
            "feeToken": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
            "feeType": "volume"  
        },  
        "gasFee": {  
            "billingType": "on-chain",  
            "feeAmount": "6786",  
            "feeToken": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
            "feeType": "gas"  
        }  
    },  
    "grossBuyAmount": "199687245360176352833",  
    "grossEstimatedPriceImpact": "0.1035",  
    "grossPrice": "1.996872453601763528",  
    "grossSellAmount": "100000000",  
    "liquidityAvailable": true,  
    "price": "1.993741637156659467",  
    "sellAmount": "100000000",  
    "sellTokenAddress": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",  
    "sources": [  
        {  
            "name": "Uniswap_V3",  
            "proportion": "1"  
        }  
    ]  
}  

```

Gasless API v2 `/quote`

Request

```
curl --request GET  
https://api.0x.org/gasless/quote?chainId=137&buyToken=0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270&sellToken=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174&sellAmount=10000000&taker=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045&swapFeeBps=10&swapFeeRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e&swapFeeToken=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174&tradeSurplusRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e  
--header '0x-api-key: YOUR_API_KEY'  
--header '0x-version: v2'  

```

Response

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

## Things to Note[​](#things-to-note "Direct link to Things to Note")

### Updated URLs[​](#updated-urls "Direct link to Updated URLs")

#### Unified Endpoint and Chain Designation[​](#unified-endpoint-and-chain-designation "Direct link to Unified Endpoint and Chain Designation")

The chain is no longer designated in the header. All chains now use the same [`https://api.0x.org`](https://api.0x.org) endpoint, with the chain set via the new `chainId` query parameter.

#### API Version Update[​](#api-version-update "Direct link to API Version Update")

The API version is no longer set in the endpoint URL. In v2, the API version is a required header parameter.

#### Endpoint Name Change[​](#endpoint-name-change "Direct link to Endpoint Name Change")

The endpoint is now `/gasless/` instead of `tx-relay/`.

#### Updated Parameter Names[​](#updated-parameter-names "Direct link to Updated Parameter Names")

Note the following parameter names have been updated in v2. See the [API reference](/docs/api) for more parameter details:

* `takerAddress` has been renamed to `taker`
* `sellTokenAddress` has been renamed to `sellToken`
* `buyTokenAddress` has been renamed to `buyToken`

### Deprecated Parameter[​](#deprecated-parameter "Direct link to Deprecated Parameter")

The `buyAmount` query parameter has been deprecated in favor of purely `sellAmount` for more deterministic behavior. When using `sellAmount`, any unused tokens are refunded to the user, whereas using `buyAmount` can lead to over-buying due to slippage and varying liquidity source behaviors. Additionally, some liquidity sources (e.g., Kyber) do not support quoting by `buyAmount`, which limits available liquidity.

**Old (v1):**

```
curl --request GET  
--url https://api.0x.org/tx-relay/v1/swap/quote?buyToken=0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270&sellAmount=100000000&sellToken=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174&takerAddress=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045&feeSellTokenPercentage=0.01&feeRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e&feeRecipientTradeSurplus=0xa8aac589a67ecfade31efde49a062cc21d68a64e  
--header '0x-api-key: <API_KEY>'  
--header '0x-chain-id: 137'  

```

**New (v2):**

```
curl --request GET  
https://api.0x.org/gasless/quote?chainId=137&buyToken=0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270&sellToken=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174&sellAmount=10000000&taker=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045&swapFeeBps=10&swapFeeRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e&swapFeeToken=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174&tradeSurplusRecipient=0xa8aac589a67ecfade31efde49a062cc21d68a64e  
--header '0x-api-key: YOUR_API_KEY'  
--header '0x-version: v2'  

```

### Changes in API Responses[​](#changes-in-api-responses "Direct link to Changes in API Responses")

#### Liquidity Availability[​](#liquidity-availability "Direct link to Liquidity Availability")

There is a new `liquidityAvailable` field that validates the availability of liquidity for a price or quote request. All other parameters will only be returned when this is returned as `true`.

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

### Gasless Approval[​](#gasless-approval "Direct link to Gasless Approval")

With the introduction of the `issues.allowance` field in Gasless API v2, some fields in `approval` field in Gasless API v1 become unnecessary. Specifically, `approval.isRequired` and `approval.isGaslessAvailable` fields have been deprecated in v2. Here is how to translate between the new fields in v2 and the old fields in v1.

| In Gasless v1 | In Gasless v2 |
| --- | --- |
| `approval.isRequired = false` | `issues.allowance = null && approval = null` |
| `approval.isRequired = true && approval.isGaslessAvailable = false` | `issues.allowance != null && approval = null` |
| `approval.isRequired = true && approval.isGaslessAvailable = true` | `issues.allowance != null && approval != null` |

## Swap TypeScript SDK[​](#swap-typescript-sdk "Direct link to Swap TypeScript SDK")

Starting with v2, we offer a TypeScript client for interacting with the 0x API. The @0x/swap-ts-sdk currently supports the "Swap" and "Gasless" endpoints of the 0x API v2. [Learn more about how to use it here.](https://0x.org/docs/0x-swap-api/swap-ts-sdk)

## Detailed Migration Guide[​](#detailed-migration-guide "Direct link to Detailed Migration Guide")

Overview of how to update Gasless API price and quote to handle the new v2 endpoints.

tip

⚡️ See these steps in action in the [Gasless headless example](https://github.com/0xProject/0x-examples/tree/main/gasless-v2-headless-example)

#### Step 0. Get 0x API key[​](#step-0-get-0x-api-key "Direct link to Step 0. Get 0x API key")

* [Get a 0x API key](/introduction/getting-started)

#### Step 1. Get indicative price[​](#step-1-get-indicative-price "Direct link to Step 1. Get indicative price")

* Call `/gasless/price` ([code](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L61-L82))
  + Build required price params
    - Add `chainId` as new param (no longer in the header)
    - `takerAddress` has changed to `taker`
  + In the response: `sellTokenAddress` changed to `sellToken`, `buyTokenAddress` changed to `buyToken`

#### Step 2. Get firm quote[​](#step-2-get-firm-quote "Direct link to Step 2. Get firm quote")

* Call `/gasless/quote` ([code](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L84-L102))
  + Build required quote params (price params + `taker` address)
    - Add `chainId` as new param (no longer in the header)
    - `takerAddress` has changed to `taker`
  + In the response: `sellTokenAddress` changed to `sellToken`, `buyTokenAddress` changed to `buyToken` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-headless-example/index.ts#L114-L131))

#### Step 3. Check if token approval is required & if gasless approval is available[​](#step-3-check-if-token-approval-is-required--if-gasless-approval-is-available "Direct link to Step 3. Check if token approval is required & if gasless approval is available")

* Check if token approval is required using `issues.allowance != null;` ([code](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L105))
* Check if gasless approval is available using `approval != null;` ([code](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L106))

#### Step 4. Sign the gasless approval oject (if available)[​](#step-4-sign-the-gasless-approval-oject-if-available "Direct link to Step 4. Sign the gasless approval oject (if available)")

* If a token approval is required and gasless approval is available, sign the approval object ([code](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L129))
* If gasless approval is not available, use the standard approval route ([code](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L131))

#### Step 5. Sign the gasless trade object[​](#step-5-sign-the-gasless-trade-object "Direct link to Step 5. Sign the gasless trade object")

* Sign the trade object ([code](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L141))

#### Step 6. Split the signatures[​](#step-6-split-the-signatures "Direct link to Step 6. Split the signatures")

* Split gasless approval signature, if available ([code](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L135-L137))
* Split gasless trade object ([code](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L142))

#### Step 7. Package signed objects and submit transaction[​](#step-7-package-signed-objects-and-submit-transaction "Direct link to Step 7. Package signed objects and submit transaction")

* Package the signed objects in a format that can be POST to `/gasless/submit` ([code](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L227-L256))

#### Step 8. Compute trade hash[​](#step-8-compute-trade-hash "Direct link to Step 8. Compute trade hash")

* If the submission is successful, `/gasless/submit` will return `tradeHash` which is the `hash` for the trade according to [EIP-712](https://eips.ethereum.org/EIPS/eip-712)
  + You may choose to verify on your own that the `tradeHash` returned matches the `settler_metatransaction` provided

#### Step 9. Check trade status[​](#step-9-check-trade-status "Direct link to Step 9. Check trade status")

* Use the `tradeHash` returned by `/submit` to poll `/gasless/status/{tradeHash}` to confirm if the trade has been successfully submitted ([code](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L258-L302))

[Previous

To Swap API v2](/docs/upgrading/upgrading_to_swap_v2)[Next

Liquidity Providers](/docs/category/liquidity-providers)

* [API Reference](#api-reference)
* [Summary of Design Changes](#summary-of-design-changes)
* [Things to Note](#things-to-note)
  + [Updated URLs](#updated-urls)
  + [Deprecated Parameter](#deprecated-parameter)
  + [Changes in API Responses](#changes-in-api-responses)
  + [Gasless Approval](#gasless-approval)
* [Swap TypeScript SDK](#swap-typescript-sdk)
* [Detailed Migration Guide](#detailed-migration-guide)

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
[https://0x.org/docs/upgrading/upgrading_to_gasless_v2#docusaurus_skipToContent_fallback](https://0x.org/docs/upgrading/upgrading_to_gasless_v2#docusaurus_skipToContent_fallback)
