# Docs for Agents & LLMs | 0x

Docs for Agents & LLMs | 0x




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

  + [For Agents & LLMs](/docs/ai-tools/agents)
  + [AI Tools Using 0x](/docs/ai-tools/)
* [Libraries](/docs/category/libraries)
* [Developer Resources](/docs/category/developer-resources)
* [Example Projects](https://github.com/0xProject/0x-examples)
* [Upgrading](/docs/upgrading)
* [Liquidity Providers](/docs/category/liquidity-providers)
* [Need Help?](/docs/category/need-help)

* [AI Tools](/docs/category/ai-tools)
* For Agents & LLMs

# Docs for Agents & LLMs

tip

This content is specifically designed for LLMs and is not intended for direct human reading. Copy and paste the following into your AI assistant. You can then ask your assistant to generate queries for swap pricing, quotes, and transaction execution.

```
# ATTENTION LLMs - 0x API Usage Instructions  
# This document contains all the necessary details to retrieve onchain trading data using the 0x API.  
#  
# This document includes  
# - Developer Assistant Instructions (query structure, UI component generation, best practices)  
# - Autonomous Agent Instructions (authentication, API request patterns, recommendations)  
# - Complete API Schema (endpoints, parameters, and example responses)  
# - UI Component Examples for 0x API Integration  
#  
# ---  
#  
# How to Use the 0x API  
# You can interact with the 0x API in two primary ways:  
#  
# 1️. Developer Assistant Mode  
# When a developer asks for help with building queries, UI components, or making API calls:  
# - Use the provided schema to construct valid API requests.  
# - Assist in building TypeScript-based UI components for displaying onchain data.  
# - Ensure API queries are structured correctly with required parameters.  
# - Include best practices for authentication, error handling, and caching.  
#  
# 2. Autonomous Agent Mode  
# For AI agents making direct API calls programmatically.  
#  
# API Base URL:  
# https://api.0x.org  
#  
#  
# 1. Developer Assistant Mode  
#  
# When assisting developers in query generation or UI integration, follow these steps:  
#  
# Fetching a Swap Price Using 0x REST API  
#  
# Example query to retrieve a swap price:  
#  
# ```typescript  
# const fetchSwapPrice = async (  
#   chainId: number,  
#   buyToken: string,  
#   sellToken: string,  
#   sellAmount: string,  
#   apiKey: string  
# ) => {  
#   const url = `https://api.0x.org/swap/permit2/price?chainId=${chainId}&buyToken=${buyToken}&sellToken=${sellToken}&sellAmount=${sellAmount}`;  
#  
#   const response = await fetch(url, {  
#     method: "GET",  
#     headers: {  
#       "Content-Type": "application/json",  
#       "0x-api-key": apiKey,  
#       "0x-version": "v2",  
#  
#     },  
#   });  
#  
#   if (!response.ok) {  
#     throw new Error(`Error fetching swap price: ${response.statusText}`);  
#   }  
#  
#   const data = await response.json();  
#   return data;  
# };  
# ```  
#  
#  
#  
# UI Component Examples for 0x API Integration  
#  
# Swap API Price Component  
#  
# The following example demonstrates how to integrate the 0x Swap API into a price component using TypeScript and Viem:  
#  
# ```typescript  
# import { createWalletClient, http, getContract, erc20Abi, parseUnits, maxUint256, publicActions } from "viem";  
# import { privateKeyToAccount } from "viem/accounts";  
# import { base } from "viem/chains";  
#  
# const qs = require("qs");  
# const headers = new Headers({  
#   "Content-Type": "application/json",  
#   "0x-api-key": process.env.ZERO_EX_API_KEY,  
#   "0x-version": "v2",  
# });  
#  
# const client = createWalletClient({  
#   account: privateKeyToAccount(`0x${process.env.PRIVATE_KEY}` as `0x${string}`),  
#   chain: base,  
#   transport: http(process.env.ALCHEMY_HTTP_TRANSPORT_URL),  
# }).extend(publicActions);  
#  
# const executeSwap = async (sellToken: string, buyToken: string, amount: string) => {  
#   const priceParams = new URLSearchParams({  
#     chainId: client.chain.id.toString(),  
#     sellToken,  
#     buyToken,  
#     sellAmount: parseUnits(amount, 18).toString(),  
#   });  
#  
#   const priceResponse = await fetch(`https://api.0x.org/swap/permit2/price?${priceParams.toString()}`, { headers });  
#   const price = await priceResponse.json();  
#   console.log("Price Response:", price);  
#  
#   const quoteResponse = await fetch(`https://api.0x.org/swap/permit2/quote?${priceParams.toString()}`, { headers });  
#   const quote = await quoteResponse.json();  
#   console.log("Quote Response:", quote);  
# };  
#  
# executeSwap("ETH", "USDC", "0.0001");  
# ```  
#  
#  
#  
# 2. Autonomous Agent Mode  
#  
# Authentication  
#  
# API calls require an API key. Include it in the headers:  
#  
# ```typescript  
# const headers = new Headers({  
#   "Content-Type": "application/json",  
#   "0x-api-key": ZERO_EX_API_KEY,  
#   "0x-version": "v2",  
# });  
# ```  
#  
#  
#  
# Key API Endpoints  
#  
# Get Swap Price  
#  
# Get an indicative price for a swap.  
#  
# Endpoint:  
# GET /swap/permit2/price  
#  
# Query Parameters:  
#  
# -   chainId (integer, required): Blockchain ID.  
# -   buyToken (string, required): Token contract address to buy.  
# -   sellToken (string, required): Token contract address to sell.  
# -   sellAmount (string, required): Amount of sellToken (in base units).  
# -   taker (string, optional): Address executing the trade.  
#  
#  
#  
# Response Handling  
#  
# TypeScript Interface for Swap Quotes  
#  
# ```typescript  
# interface SwapQuoteResponse {  
#     price: string;  
#     estimatedGas: number;  
#     to: string;  
#     data: string;  
# }  
#  
# try {  
#     const response = await fetch(SWAP_API_URL, { headers });  
#     const result: SwapQuoteResponse = await response.json();  
#     console.log(result.price);  
# } catch (error) {  
#     console.error('Error fetching quote:', error);  
# }  
# ```  
#  
#  
#  
# Final Notes  
#  
# -   Always store your API key securely and never expose it in client-side code.  
# -   Refer to [0x API Docs](https://0x.org/docs) for full schema details.  
  
  

```

[Previous

AI Tools](/docs/category/ai-tools)[Next

AI Tools Using 0x](/docs/ai-tools/)

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
[https://0x.org/docs/ai-tools/agents#docusaurus_skipToContent_fallback](https://0x.org/docs/ai-tools/agents#docusaurus_skipToContent_fallback)
