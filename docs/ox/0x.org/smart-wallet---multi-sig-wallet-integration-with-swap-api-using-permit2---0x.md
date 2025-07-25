# Smart Wallet & Multi-Sig Wallet Integration with Swap API using Permit2 | 0x

Smart Wallet & Multi-Sig Wallet Integration with Swap API using Permit2 | 0x




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
* Smart Wallet & Multi-Sig Wallet Integration

On this page

# Smart Wallet & Multi-Sig Wallet Integration with Swap API using Permit2

This guide helps developers integrate smart wallets and multi-sig wallets with the [Swap API using Permit2](/docs/introduction/0x-cheat-sheet#permit2-contract) to provide a secure token swapping experience.

Permit2 is recommended for most applications, especially those using multi-sig or smart wallets that support EIP-1271. It requires two user signatures per trade: one for limited approval and one for the trade itself.

For more details, see [Permit2 vs. AllowanceHolder](https://0x.org/docs/developer-resources/faqs-and-troubleshooting#permit2-and-allowanceholder).

## Integration Overview[​](#integration-overview "Direct link to Integration Overview")

The Swap API Permit2 integration enables secure token approvals and swaps for smart and multi-sig wallets. This guide walks you through appending Permit2 data and submitting transactions to the blockchain.

tip

⚡ Check out the [live demo and code](https://github.com/0xProject/0x-examples/tree/main/swap-v2-next-app) showcasing a [Coinbase Smart Wallet](https://www.smartwallet.dev/why) integration using [RainbowKit](https://docs.base.org/tutorials/smart-wallet-and-rainbowkit/).

## Integration Steps[​](#integration-steps "Direct link to Integration Steps")

0. Get a 0x API key
1. Integrate a Smart Wallet or Mult-Sig Wallet
2. Get an indicative price
3. (If needed) Set token allowance
4. Fetch a firm quote
5. Sign the Permit2 EIP-712 message
6. Append signature length and signature data to calldata
7. Submit the transaction with Permit2 signature

## 0. Get a 0x API key[​](#0-get-a-0x-api-key "Direct link to 0. Get a 0x API key")

You’ll need an API key for all 0x API calls. [Create a 0x account](https://dashboard.0x.org/) and follow the [setup guide](/docs/introduction/getting-started) for details.

## 1. Integrate a Smart Wallet or Mult-Sig Wallet[​](#1-integrate-a-smart-wallet-or-mult-sig-wallet "Direct link to 1. Integrate a Smart Wallet or Mult-Sig Wallet")

Configure your integration to allow users to connect a smart wallet (e.g., Coinbase Smart Wallet) or multi-sig wallet.

Code example to integrate Coinbase Smart Wallet

View the [full example](https://github.com/0xProject/0x-examples/blob/main/swap-v2-next-app/app/providers.tsx) for integrating Coinbase Smart Wallet with [RainbowKit](https://docs.base.org/tutorials/smart-wallet-and-rainbowkit/).

```
'use client';  
  
import { RainbowKitProvider, connectorsForWallets } from '@rainbow-me/rainbowkit';  
import {  
    argentWallet,  
    coinbaseWallet,  
    ledgerWallet,  
    metaMaskWallet,  
    rainbowWallet,  
    trustWallet,  
} from '@rainbow-me/rainbowkit/wallets';  
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';  
import * as React from 'react';  
import { WagmiProvider, createConfig, http } from 'wagmi';  
import { mainnet } from 'wagmi/chains';  
  
const projectId = process.env.NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID as string;  
coinbaseWallet.preference = 'smartWalletOnly';  
  
const connectors = connectorsForWallets(  
    [  
        {  
            groupName: 'Recommended Wallet',  
            wallets: [coinbaseWallet],  
        },  
        {  
            groupName: 'Other',  
            wallets: [rainbowWallet, metaMaskWallet, argentWallet, trustWallet, ledgerWallet],  
        },  
    ],  
    {  
        appName: '0x Swap Demo App',  
        projectId,  
    },  
);  
  
const config = createConfig({  
    chains: [mainnet],  
    // turn off injected provider discovery  
    multiInjectedProviderDiscovery: false,  
    connectors,  
    ssr: true,  
    transports: { [mainnet.id]: http() },  
});  
  
const queryClient = new QueryClient();  
  
export function Providers({ children }: { children: React.ReactNode }) {  
    return (  
        <div  
            style={{  
                padding: '20px',  
            }}  
        >  
            <WagmiProvider config={config}>  
                <QueryClientProvider client={queryClient}>  
                    <RainbowKitProvider>{children}</RainbowKitProvider>{' '}  
                </QueryClientProvider>  
            </WagmiProvider>  
        </div>  
    );  
}  

```

UX if user does not have Coinbase Wallet installed:

![Coinbase Smart Wallet integration](/docs/assets/images/coinbase-smart-wallet-integration-8bc5fc68328ead530c8380a67637081b.png)

UX if user does have Coinbase Wallet installed:

![Coinbase Smart Wallet integration](/docs/assets/images/coinbase-smart-wallet-connected-564a8308f7a2df1247bd03aebb090380.png)

## 2. Get an Indicative Price[​](#2-get-an-indicative-price "Direct link to 2. Get an Indicative Price")

Use the `/swap/permit2/price` endpoint to get an indicative price for an asset pair. This returns pricing information without creating a full order or transaction, allowing the user to browse potential prices before committing.

Think of `/price` as the "read-only" version of `/quote`, which you'll use in step 3.

### Example Request[​](#example-request "Direct link to Example Request")

Here is an example request to sell 100 WETH for DAI using `/price` ([code](https://github.com/0xProject/0x-examples/blob/main/swap-v2-headless-example/index.ts#L60-L77)):

```
const priceParams = new URLSearchParams({  
    chainId: '1', // / Ethereum mainnet. See the 0x Cheat Sheet for all supported endpoints: https://0x.org/docs/introduction/0x-cheat-sheet  
    sellToken: '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', //ETH  
    buyToken: '0x6b175474e89094c44da98b954eedeac495271d0f', //DAI  
    sellAmount: '100000000000000000000', // Note that the WETH token uses 18 decimal places, so `sellAmount` is `100 * 10^18`.  
    taker: '$USER_TAKER_ADDRESS', //Address that will make the trade  
});  
  
const headers = {  
    '0x-api-key': '[api-key]', // Get your live API key from the 0x Dashboard (https://dashboard.0x.org/apps)  
    '0x-version': 'v2',  
};  
  
const priceResponse = await fetch('https://api.0x.org/swap/permit2/price?' + priceParams.toString(), { headers });  
  
console.log(await priceResponse.json());  

```

### Example Response[​](#example-response "Direct link to Example Response")

You will receive a response that looks like this:

Expand to see response

```
{  
    "blockNumber": "20170903",  
    "buyAmount": "340843848647293527128015",  
    "buyToken": "0x6b175474e89094c44da98b954eedeac495271d0f",  
    "fees": {  
        "integratorFee": null,  
        "zeroExFee": {  
            "amount": "512033823706500040753",  
            "token": "0x6b175474e89094c44da98b954eedeac495271d0f",  
            "type": "volume"  
        },  
        "gasFee": null  
    },  
    "gas": "522732",  
    "gasPrice": "14551300000",  
    "issues": {  
        "allowance": {  
            "actual": "0",  
            "spender": "0x000000000022d473030f116ddee9f6b43ac78ba3"  
        },  
        "balance": {  
            "token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
            "actual": "0",  
            "expected": "100000000000000000000"  
        },  
        "simulationIncomplete": false,  
        "invalidSourcesPassed": []  
    },  
    "liquidityAvailable": true,  
    "minBuyAmount": "337435410160820591856735",  
    "route": {  
        "fills": [  
            {  
                "from": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "to": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  
                "source": "Uniswap_V3",  
                "proportionBps": "10000"  
            },  
            {  
                "from": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  
                "to": "0x6b175474e89094c44da98b954eedeac495271d0f",  
                "source": "Maker_PSM",  
                "proportionBps": "10000"  
            }  
        ],  
        "tokens": [  
            {  
                "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "symbol": "WETH"  
            },  
            {  
                "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  
                "symbol": "USDC"  
            },  
            {  
                "address": "0x6b175474e89094c44da98b954eedeac495271d0f",  
                "symbol": "DAI"  
            }  
        ]  
    },  
    "sellAmount": "100000000000000000000",  
    "sellToken": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
    "totalNetworkFee": "7606430151600000"  
}  

```

## 3. Set a Token Allowance[​](#3-set-a-token-allowance "Direct link to 3. Set a Token Allowance")

Before swapping, you must approve the Permit2 contract to transfer your tokens. See [How to Set Token Allowances](/docs/0x-swap-api/advanced-topics/how-to-set-your-token-allowances) for details.

tip

When setting the token allowance, make sure to provide enough allowance for the buy or sell amount *as well as the gas;* otherwise, you may receive a 'Gas estimation failed' error.

### Example Code[​](#example-code "Direct link to Example Code")

Here is an example of how to check and set token approvals using viem's [`getContract`](https://viem.sh/docs/contract/getContract.html).

```
import { getContract } from 'viem';  
...  
// Set up contracts. Note abi and client setup not show in this snippet  
const Permit2 = getContract({  
    address: '0x000000000022D473030F116dDEE9F6B43aC78BA3',  
    abi: exchangeProxyAbi,  
    client,  
});  
const usdc = getContract({  
    address: '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913',  
    abi: erc20Abi,  
    client,  
});  
  
// Check allowance is enough for Permit2 to spend sellToken  
if (sellAmount > (await usdc.read.allowance([client.account.address, Permit2.address])))  
    try {  
        const { request } = await usdc.simulate.approve([Permit2.address, maxUint256]);  
        console.log('Approving Permit2 to spend USDC...', request);  
        // If not, write approval  
        const hash = await usdc.write.approve(request.args);  
        console.log('Approved Permit2 to spend USDC.', await client.waitForTransactionReceipt({ hash }));  
    } catch (error) {  
        console.log('Error approving Permit2:', error);  
    }  
else {  
    console.log('USDC already approved for Permit2');  
}  

```

## 4. Fetch a Firm Quote[​](#4-fetch-a-firm-quote "Direct link to 4. Fetch a Firm Quote")

When you're ready to execute a trade, request a firm quote from the Swap API using the `/swap/permit2/quote endpoint`. This signals a soft commitment to complete the trade/

The `/swap/permit2/quote` response includes a full 0x order, ready for submission to the network. The Market Maker is expected to have reserved the necessary assets, reducing the likelihood of order reversion.

### Example request[​](#example-request-1 "Direct link to Example request")

Here is an example to fetch a firm quote sell 100 WETH for DAI using `/quote`:

```
const qs = require('qs');  
  
const params = {  
    sellToken: '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', //WETH  
    buyToken: '0x6b175474e89094c44da98b954eedeac495271d0f', //DAI  
    sellAmount: '100000000000000000000', // Note that the WETH token uses 18 decimal places, so `sellAmount` is `100 * 10^18`.  
    taker: '$USER_TAKER_ADDRESS', //Address that will make the trade  
    chainId: '1', // / Ethereum mainnet. See the 0x Cheat Sheet for all supported endpoints: https://0x.org/docs/introduction/0x-cheat-sheet  
};  
  
const headers = {  
    '0x-api-key': '[api-key]',  // Get your live API key from the 0x Dashboard (https://dashboard.0x.org/apps)  
    '0x-version': 'v2',         // Add the version header  
};  
  
const response = await fetch(  
    `https://api.0x.org/swap/permit2/quote?${qs.stringify(params)}`, { headers }  
); /  
  
console.log(await response.json());  

```

### Example Response[​](#example-response-1 "Direct link to Example Response")

You will receive a response that looks like this:

Expand to see response

```
{  
    "blockNumber": "20171314",  
    "buyAmount": "340079984242963924184466",  
    "buyToken": "0x6b175474e89094c44da98b954eedeac495271d0f",  
    "fees": {  
        "integratorFee": null,  
        "zeroExFee": {  
            "amount": "510886305823180657262",  
            "token": "0x6b175474e89094c44da98b954eedeac495271d0f",  
            "type": "volume"  
        },  
        "gasFee": null  
    },  
    "issues": {  
        "allowance": {  
            "actual": "0",  
            "spender": "0x000000000022d473030f116ddee9f6b43ac78ba3"  
        },  
        "balance": {  
            "token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
            "actual": "0",  
            "expected": "100000000000000000000"  
        },  
        "simulationIncomplete": false,  
        "invalidSourcesPassed": []  
    },  
    "liquidityAvailable": true,  
    "minBuyAmount": "336679184400534284942622",  
    "permit2": {  
        "type": "Permit2",  
        "hash": "0x6d1dc295a179c196be29ba86ecdfea1eb6cd6f3486ee9ff56ecf208c5b2c231b",  
        "eip712": {  
            "types": {  
                "PermitTransferFrom": [  
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
                ]  
            },  
            "domain": {  
                "name": "Permit2",  
                "chainId": 1,  
                "verifyingContract": "0x000000000022d473030f116ddee9f6b43ac78ba3"  
            },  
            "message": {  
                "permitted": {  
                    "token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                    "amount": "100000000000000000000"  
                },  
                "spender": "0x7f6cee965959295cc64d0e6c00d99d6532d8e86b",  
                "nonce": "2241959297937691820908574931991569",  
                "deadline": "1719353695"  
            },  
            "primaryType": "PermitTransferFrom"  
        }  
    },  
    "route": {  
        "fills": [  
            {  
                "from": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "to": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  
                "source": "Integral",  
                "proportionBps": "1250"  
            },  
            {  
                "from": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "to": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  
                "source": "Uniswap_V3",  
                "proportionBps": "7250"  
            },  
            {  
                "from": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "to": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  
                "source": "Uniswap_V2",  
                "proportionBps": "250"  
            },  
            {  
                "from": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "to": "0xdac17f958d2ee523a2206206994597c13d831ec7",  
                "source": "Uniswap_V2",  
                "proportionBps": "500"  
            },  
            {  
                "from": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "to": "0xdac17f958d2ee523a2206206994597c13d831ec7",  
                "source": "PancakeSwap_V3",  
                "proportionBps": "750"  
            },  
            {  
                "from": "0xdac17f958d2ee523a2206206994597c13d831ec7",  
                "to": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  
                "source": "DODO_V1",  
                "proportionBps": "1250"  
            },  
            {  
                "from": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  
                "to": "0x6b175474e89094c44da98b954eedeac495271d0f",  
                "source": "Maker_PSM",  
                "proportionBps": "10000"  
            }  
        ],  
        "tokens": [  
            {  
                "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
                "symbol": "WETH"  
            },  
            {  
                "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",  
                "symbol": "USDT"  
            },  
            {  
                "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  
                "symbol": "USDC"  
            },  
            {  
                "address": "0x6b175474e89094c44da98b954eedeac495271d0f",  
                "symbol": "DAI"  
            }  
        ]  
    },  
    "sellAmount": "100000000000000000000",  
    "sellToken": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  
    "totalNetworkFee": "6468973864320000",  
    "transaction": {  
        "to": "0x7f6cee965959295cc64d0e6c00d99d6532d8e86b",  
        "data": "0x1fff991f000000000000000000000000a423c7be031e988b25fb7ec39b7906582f6858c60000000000000000000000006b175474e89094c44da98b954eedeac495271d0f00000000000000000000000000000000000000000000474b6a47c98442ae3d1e00000000000000000000000000000000000000000000000000000000000000a07563abae22f6c91576af12c800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000000002a000000000000000000000000000000000000000000000000000000000000004a000000000000000000000000000000000000000000000000000000000000005c000000000000000000000000000000000000000000000000000000000000006c000000000000000000000000000000000000000000000000000000000000007c00000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000ae00000000000000000000000000000000000000000000000000000000000000bc00000000000000000000000000000000000000000000000000000000000000144c1fb425e0000000000000000000000007f6cee965959295cc64d0e6c00d99d6532d8e86b000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000056bc75e2d631000000000000000000000000000000000000000006e898131631616b1779bad70bc1100000000000000000000000000000000000000000000000000000000667b415f00000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000041ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001c438c9c147000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc200000000000000000000000000000000000000000000000000000000000004e2000000000000000000000000d17b3c9784510e33cd5b87b490e79253bcd81e2e000000000000000000000000000000000000000000000000000000000000004400000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000e458d30ac9000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000ad78ebc5ac620000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007f6cee965959295cc64d0e6c00d99d6532d8e86b00000000000000000000000000000000000000000000000000000000667b415f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e48d68a1560000000000000000000000007f6cee965959295cc64d0e6c00d99d6532d8e86b000000000000000000000000000000000000000000000000000000000000205d00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002cc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000001f4a0b86991c6218b36c1d19d4a2e9eb0ce3606eb4800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c4103b48be0000000000000000000000007f6cee965959295cc64d0e6c00d99d6532d8e86b000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000682000000000000000000000000b4e16d0168e52d35cacd2c6185b44281ec28c9dc0000000000000000000000000000000000000000000000000000000000001e0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c4103b48be0000000000000000000000007f6cee965959295cc64d0e6c00d99d6532d8e86b000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000fa00000000000000000000000000d4a11d5eeaac28ec3f61d100daf4d40471f18520000000000000000000000000000000000000000000000000000000000001e01000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020438c9c147000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc200000000000000000000000000000000000000000000000000000000000027100000000000000000000000001b81d678ffb9c0263b24a97847620c99d213eb14000000000000000000000000000000000000000000000000000000000000008400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000124c04b8d59000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000007f6cee965959295cc64d0e6c00d99d6532d8e86b00000000000000000000000000000000000000000000000000000000667b415f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002bc02aaa39b223fe8d0a0e5c4f27ead9083c756cc20001f4dac17f958d2ee523a2206206994597c13d831ec7000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a4b8df6d4d000000000000000000000000dac17f958d2ee523a2206206994597c13d831ec70000000000000000000000000000000000000000000000000000000000002710000000000000000000000000c9f93163c99695c6526b799ebca2207fdf7d61ad000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a4e12b0f130000000000000000000000007f6cee965959295cc64d0e6c00d99d6532d8e86b000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000000000000000271000000000000000000000000089b78cfa322f6c5de0abceecab66aee45393cc5a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000012438c9c1470000000000000000000000006b175474e89094c44da98b954eedeac495271d0f000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000006b175474e89094c44da98b954eedeac495271d0f000000000000000000000000000000000000000000000000000000000000002400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000044a9059cbb000000000000000000000000ad01c20d5886137e056775af56915de824c8fce500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  
        "gas": "1247642",  
        "gasPrice": "5184960000",  
        "value": "0"  
    }  
}  

```

## 5. Sign the Permit2 EIP-712 Message[​](#5-sign-the-permit2-eip-712-message "Direct link to 5. Sign the Permit2 EIP-712 Message")

After obtaining the quote, the next step is to sign the Permit2 EIP-712 message. Smart wallets and multi-sig wallets need to sign this message securely to authorize the swap.

Here’s how to sign the `permit2.eip712` object returned from the quote:

```
// Sign permit2.eip712 returned from quote  
let signature: Hex;  
signature = await signTypedData(quote.permit2.eip712);  

```

This signature will be included in the transaction data to authenticate the user's intent.

## 6. Append Signature Length and Data to Transaction[​](#6-append-signature-length-and-data-to-transaction "Direct link to 6. Append Signature Length and Data to Transaction")

Once the `permit2.eip712` object is signed, the signature must be appended to the transaction. The transaction data should include the signature's length and the signature itself, ensuring that all necessary information is included when submitting the transaction to the blockchain.

Here's how you can append the signature length and data to `transaction.data`:

```
import { concat, numberToHex, size } from 'viem';  
  
// Check if permit2.eip712 is present  
if (permit2?.eip712) {  
    const signature = await signTypedDataAsync(permit2.eip712);  
    const signatureLengthInHex = numberToHex(size(signature), {  
        signed: false,  
        size: 32,  
    });  
  
    // Append signature length and data to transaction  
    transaction.data = concat([transaction.data, signatureLengthInHex, signature]);  
}  

```

In this code:

* `<sig len>` is a 32-byte unsigned big-endian integer representing the length of the signature.
* `<sig data>` is the actual signature data.

Appending the signature data ensures that the transaction contains all the necessary components to be processed securely on-chain.

## 7. Submit the Transaction with Permit2 Signature[​](#7-submit-the-transaction-with-permit2-signature "Direct link to 7. Submit the Transaction with Permit2 Signature")

After appending the signature, the transaction is ready to be submitted to the blockchain. Smart wallets or multi-sig wallets will handle the transaction signing and submission according to their respective architectures. In production, ensure you handle any errors or edge cases related to signature verification or gas estimation before submission.

You can submit the transaction using your preferred web3 library (e.g. wagmi, viem, ethers.js, web3.js).In this example, we use wagmi's [`useSendTransaction`](https://wagmi.sh/react/api/hooks/useSendTransaction).

```
sendTransaction({  
    account: walletClient?.account.address,  
    gas: !!quote?.transaction.gas ? BigInt(quote?.transaction.gas) : undefined,  
    to: quote?.transaction.to,  
    data: quote?.transaction.data,  
    chainId: chainId,  
});  

```

## Conclusion[​](#conclusion "Direct link to Conclusion")

By following this guide, you can securely integrate smart and multi-sig wallets with the Permit2 Swap API, ensuring safe and efficient token swaps.

[Previous

Troubleshooting Swap API](/docs/0x-swap-api/guides/troubleshooting-swap-api)[Next

Set a Token Allowance](/docs/0x-swap-api/advanced-topics/how-to-set-your-token-allowances)

* [Integration Overview](#integration-overview)
* [Integration Steps](#integration-steps)
* [0. Get a 0x API key](#0-get-a-0x-api-key)
* [1. Integrate a Smart Wallet or Mult-Sig Wallet](#1-integrate-a-smart-wallet-or-mult-sig-wallet)
* [2. Get an Indicative Price](#2-get-an-indicative-price)
  + [Example Request](#example-request)
  + [Example Response](#example-response)
* [3. Set a Token Allowance](#3-set-a-token-allowance)
  + [Example Code](#example-code)
* [4. Fetch a Firm Quote](#4-fetch-a-firm-quote)
  + [Example request](#example-request-1)
  + [Example Response](#example-response-1)
* [5. Sign the Permit2 EIP-712 Message](#5-sign-the-permit2-eip-712-message)
* [6. Append Signature Length and Data to Transaction](#6-append-signature-length-and-data-to-transaction)
* [7. Submit the Transaction with Permit2 Signature](#7-submit-the-transaction-with-permit2-signature)
* [Conclusion](#conclusion)

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
[https://0x.org/docs/0x-swap-api/guides/smart-contract-wallet-integration#docusaurus_skipToContent_fallback](https://0x.org/docs/0x-swap-api/guides/smart-contract-wallet-integration#docusaurus_skipToContent_fallback)
