# Swap TypeScript SDK | 0x

Swap TypeScript SDK | 0x




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

  + [Swap & Gasless SDK](/docs/libraries/swap-ts-sdk)
  + [Display Final Swapped Amount](/docs/0x-swap-api/advanced-topics/0x-parser)
* [Developer Resources](/docs/category/developer-resources)
* [Example Projects](https://github.com/0xProject/0x-examples)
* [Upgrading](/docs/upgrading)
* [Liquidity Providers](/docs/category/liquidity-providers)
* [Need Help?](/docs/category/need-help)

* [Libraries](/docs/category/libraries)
* Swap & Gasless SDK

On this page

# Swap TypeScript SDK

We provide a TypeScript client to interact with 0x API. Currently [@0x/swap-ts-sdk](https://www.npmjs.com/package/@0x/swap-ts-sdk) supports 0x API v2 Swap (both Permit2 and AllowaceHolder flows) and Gasless endpoints.

## Setup[​](#setup "Direct link to Setup")

```
pnpm add -E @0x/swap-ts-sdk  

```

info

Important: TypeScript needs to be configured with `compilerOptions.strict` set to true. The client won't correctly type check if TypeScript is not in strict mode.

Visit the [0x dashboard](https://dashboard.0x.org/create-account) to get your API key.

## Usage[​](#usage "Direct link to Usage")

Create a "vanilla" Node client with `createClientV2`:

```
import { createClientV2 } from '@0x/swap-ts-sdk';  
  
const client = createClientV2({  
    apiKey: '33da2...91ebf9',  
});  
  
const price = await client.swap.permit2.getPrice.query({  
    buyToken: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  
    chainId: 1,  
    sellAmount: '1000000000000000000',  
    sellToken: '0xdAC17F958D2ee523a2206206994597C13D831ec7',  
});  

```

### Client documentation[​](#client-documentation "Direct link to Client documentation")

The `@0x/swap-ts-sdk` client is a wrapped & typed [tRPC](https://trpc.io/) v10.x client.

Visit <https://trpc.io/docs/v10/client> for full documentation, including how to use the client with Next.js, React Query, or vanilla Node.

### Aborting calls (timeout)[​](#aborting-calls-timeout "Direct link to Aborting calls (timeout)")

```
import { createClientV2 } from '@0x/swap-ts-sdk';  
  
const client = createClientV2({  
    apiKey: '33da2...91ebf9',  
});  
  
const quote = await client.gasless.getQuote.query(  
    {  
        buyToken: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  
        chainId: 1,  
        sellAmount: '1000000000000000000',  
        sellToken: '0xdAC17F958D2ee523a2206206994597C13D831ec7',  
        taker: '0x60B4f0e1DF30c8c0f0b0c8BEc8787E7564647a80',  
        txOrigin: '0x60B4f0e1DF30c8c0f0b0c8BEc8787E7564647a80',  
    },  
    {  
        signal: AbortSignal.timeout(1000),  
    },  
);  

```

### Using with Next.js[​](#using-with-nextjs "Direct link to Using with Next.js")

You can use `@trpc/next` directly to use the SDK with Next.js. See the documentation here: <https://trpc.io/docs/v10/client/nextjs/ssr>.

To type the client, the packages exports the router type:

```
import type { RouterV2 } from '@0x/swap-ts-sdk';  
import { httpLink } from '@trpc/client';  
import { createTRPCNext } from '@trpc/next';  
  
export const trpc = createTRPCNext<RouterV2>({  
    config(_opts) {  
        return {  
            links: [  
                httpLink({  
                    headers: {  
                        '0x-api-key': 'your-api-key',  
                        '0x-version': 'v2',  
                    },  
                    url: 'https://api.0x.org/trpc/swap',  
                }),  
            ],  
        };  
    },  
    ssr: true,  
});  

```

[Previous

Libraries](/docs/category/libraries)[Next

Display Final Swapped Amount](/docs/0x-swap-api/advanced-topics/0x-parser)

* [Setup](#setup)
* [Usage](#usage)
  + [Client documentation](#client-documentation)
  + [Aborting calls (timeout)](#aborting-calls-timeout)
  + [Using with Next.js](#using-with-nextjs)

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
[https://0x.org/docs/libraries/swap-ts-sdk#docusaurus_skipToContent_fallback](https://0x.org/docs/libraries/swap-ts-sdk#docusaurus_skipToContent_fallback)
