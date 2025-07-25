# Gasless API - Technical Appendix | 0x

Gasless API - Technical Appendix | 0x




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
* Technical Appendix

On this page

# Gasless API - Technical Appendix

*Learn how to sign the trade & approval objects, split signatures, submit, and compute the trade hash for a gasless trade*

The following is the typical flow when using Gasless API.
This guide covers how to complete **steps 3 - 4**.

1. Get an indicative price using `/gasless/price`
2. Get a firm quote using `/gasless/quote`
3. Submit the transaction using `/gasless/submit`
   1. Sign the gasless approval object (if applicable)
   2. Sign the trade object
   3. Split the signatures
   4. Package split signed objects into a format that can be POST to `/gasless/submit`
   5. Compute trade hash
4. Check the trade status using `/gasless/status/{tradeHash}`

tip

Checkout the [Gasless API Runnable Headless Example](https://github.com/0xProject/0x-examples/tree/main/gasless-v2-headless-example) to see these steps in action

## Signing objects[​](#signing-objects "Direct link to Signing objects")

To take advantage of gaslesses approvals and gasless trades, user must sign the `approval.eip712` and the `trade.eip712` objects returned by [`/quote`](/docs/api#tag/Gasless/operation/gasless::getQuote). These objects contain everything (domain, types, primaryType, message) needed when signing these objects .

There are different EIP-712 signing strategies if you are user facing wallet that shows the users the details of what they are signing. Some commonly used tools for this include:

* integrating with MetaMask (via [`signTypedData_v4`](https://docs.metamask.io/guide/signing-data.html#sign-typed-data-v4))
* viem's [signTypedData](https://viem.sh/docs/actions/wallet/signTypedData.html)
* wagmi's [signTypedData](https://wagmi.sh/core/api/actions/signTypedData)

### Sign gasless approval object[​](#sign-gasless-approval-object "Direct link to Sign gasless approval object")

If a token supports [gasless approvals](/docs/gasless-api/guides/understanding-gasless-api#gasless-approvals), the `/quote` response will return an “approval” object which contains the necessary information to process a gasless approval, see below:

```
 "approval":{  
     "type": "permit", // this is approval.type from the /quote endpoint  
     "hash": "0xf3849ebcd806e518f2d3457b76d31ccf41be07fe64f0a25bbe798f1b9edde872",  
     "eip712": {  
        "types": {/* this is approval.eip712.types from the /quote endpoint */},  
        "domain": {/* this is approval.eip712.domain from the /quote endpoint */},  
        "message": {/* this is approval.eip712.message from the /quote endpoint */},  
        "primaryType": "Permit",  
     }  
    }  
  }  

```

Keep in mind that the `domain` field of this object must follow a strict ordering as specified in EIP-712. The `approval.eip712` object will present the correct ordering, but make sure that this ordering is preserved when obtaining the signature:

* `name` , `version`, `chainId`, `verifyingContract`, `salt`
  + Contracts may not utilize all of these fields (i.e. one or more may be missing), but if they are present, they must be in this order
* Any other field must follow in alphabetical order

tip

See [example code to sign approval object](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L170-L180)

Here is an example to sign it using viem's [signTypedData](https://viem.sh/docs/actions/wallet/signTypedData.html):

```
// Sign the data returned by approval.712 in the quote response  
  async function signApprovalObject(): Promise<any> {  
    // Logic to sign approval object  
    const approvalSignature = await client.signTypedData({  
      types: quote.approval.eip712.types,  
      domain: quote.approval.eip712.domain,  
      message: quote.approval.eip712.message,  
      primaryType: quote.approval.eip712.primaryType,  
    });  
    return approvalSignature;  
  }  

```

### Sign trade object[​](#sign-trade-object "Direct link to Sign trade object")

Similar to gasless approval, to submit a trade, you must have your user sign `trade.eip712` object returned at the time of the `/quote`. All the instructions & caveats are the same as previous section.

tip

See example code to [sign trade object](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L158-L168)

Here is an example to sign it using viem's [signTypedData](https://viem.sh/docs/actions/wallet/signTypedData.html):

```
// Sign the data returned by trade.712 in the quote response  
 async function signTradeObject(): Promise<any> {  
    // Logic to sign trade object  
    const tradeSignature = await client.signTypedData({  
      types: quote.trade.eip712.types,  
      domain: quote.trade.eip712.domain,  
      message: quote.trade.eip712.message,  
      primaryType: quote.trade.eip712.primaryType,  
    });  
    return tradeSignature;  
  }  

```

## Split signatures[​](#split-signatures "Direct link to Split signatures")

Once signed, the signature needs to be split to its individual components (v, r, s) and to be formatted in an object that can be POST to `/submit` (see object format [here](/docs/api#tag/Gasless/operation/gasless::submit)).

tip

Example code showing how to implement a [split signature function](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/utils/signature.ts). This is a variation of this [`splitSignature`](https://github.com/wevm/viem/discussions/458#discussioncomment-5842564) implementation.

Example code using split signature to [split approval and trade signatures](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L207-L234)

## POST the split signatures to /submit[​](#post-the-split-signatures-to-submit "Direct link to POST the split signatures to /submit")

### Example request[​](#example-request "Direct link to Example request")

Once the signatures have been split, in order to POST to `/submit`, approval and trade objects must be formatted to contain the following key/value pairs:

```
curl -X POST '<https://api.0x.org/gasless/submit>' --header '0x-api-key: <API_KEY>' --header '0x-version: v2' --data '{  
 "trade": {  
   "type": "settler_metatransaction", // this is trade.type from the /quote endpoint  
   "eip712": { /* this is trade.eip712 from the /quote endpoint */ },  
   "signature": {  
     "v": 27,  
     "r": "0xeaac9ddbbf9b251a384eb4a545a2800a6d7aca4ceb5e5a3154ddd0d2923533d2",  
     "s": "0x601deadfd33bd8b0ad35468613eabcac0a250a7a32035e261a13e2dcbc462e49",  
     "signatureType": 2  
    }  
  },  
 "approval":{  
     "type": "permit", // this is approval.type from the /quote endpoint  
     "eip712": {/* this is approval.eip712 from the /quote endpoint */},  
     "signature": {  
       "v": 28,  
       "r": "0x55c26901285d5cb4d9d1ebb2828122fd6c334b343901944d34a810b3d2d79773",  
       "s": "0x20854d829e3118c3f780228ca83fac6154060328a90d2a21267c9f7d1ae9e53b",  
       "signatureType": 2  
    }  
  }  
}'  

```

tip

See [example code to POST split signatures to submit](https://github.com/0xProject/0x-examples/blob/main/gasless-v2-headless-example/index.ts#L236-L265)

Here is an example code snippet of how to submit it using JavaScript:

```
 // Make a POST request to submit trade with split signed trade object (and approval object if available)  
  async function submitTrade(  
    tradeDataToSubmit: any,  
    approvalDataToSubmit: any  
  ): Promise<void> {  
    try {  
      let successfulTradeHash;  
      const requestBody: any = {  
        trade: tradeDataToSubmit,  
        chainId: client.chain.id,  
      };  
      if (approvalDataToSubmit) {  
        requestBody.approval = approvalDataToSubmit;  
      }  
      const response = await fetch("https://api.0x.org/gasless/submit", {  
        method: "POST",  
        headers: {  
          "0x-api-key": process.env.ZERO_EX_API_KEY as string,  
          "0x-version": process.env.ZERO_EX_API_VERSION as string,  
          "Content-Type": "application/json",  
        },  
        body: JSON.stringify(requestBody),  
      });  
      const data = await response.json();  
      successfulTradeHash = data.tradeHash;  
      console.log("#️⃣ tradeHash: ", successfulTradeHash);  
      return successfulTradeHash;  
    } catch (error) {  
      console.error("Error submitting the gasless swap", error);  
    }  
  }  

```

### Example response[​](#example-response "Direct link to Example response")

If the submitted trade is successful, and object with `type`, `tradeHash`, and `zid` are returned.

```
{  
  "tradeHash": "0xcb3285b35c024fca76037bea9ea4cb68645fed3bdd84030956577de2f1592aa9",  
  "type": "settler_metatransaction",  
  "zid": "0x111111111111111111111111"  
}  

```

## Status Code[​](#status-code "Direct link to Status Code")

* `201` if successful
* `400`:
  + If the trade is too close to expiration time.
  + If the signature in the payload is invalid.
  + If the balance / allowance of the taker is less than the trade amount.
  + (`otc` only) If the trade has been outstanding for too long.
  + (`otc` only) If the balance / allowance of the market maker selected to settle the trade is less than the trade amount (very unlikely).
  + If the query params are not able to pass validation.
* `429` if there is already a trade associated with a taker address and a taker token that's not been settled by our relayers yet. For example, if `address A` already has a `USDC -> WETH` trade submitted and it has not settled yet, then a subsequent `/submit` call with `address A` and `USDC -> *` trade will fail with `429`. The taker is, however, allowed to submit other trades with a different taker token.
* `500` if there is an internal server error.

## Note for go-ethereum[​](#note-for-go-ethereum "Direct link to Note for go-ethereum")

* If you're using `go-ethereum`, for `domain`, make sure you order the fields in the exact same order as specified in <https://eips.ethereum.org/EIPS/eip-712> since `go-ethereum` does not enforce ordering. Also, make sure you skipped fields that are absent.

```
- string name: the user readable name of signing domain, i.e. the name of the DApp or the protocol.  
- string version: the current major version of the signing domain. Signatures from different - versions are not compatible.  
- uint256 chainId: the EIP-155 chain id. The user-agent should refuse signing if it does not match the currently active chain.  
- address verifyingContract: the address of the contract that will verify the signature. The user-agent may do contract specific phishing prevention.  
- bytes32 salt: an disambiguating salt for the protocol. This can be used as a domain separator of last resort.  
  
The EIP712Domain fields should be the order as above, skipping any absent fields  

```

* If you're using `ethers v6` (`v5` and `v4` are fine), there is an [issue](https://github.com/ethers-io/ethers.js/discussions/3873) for signing EIP-712 object. Make sure you updated `ethers` version to `>= 6.3.0`.

[Previous

Understanding Gasless API](/docs/gasless-api/guides/understanding-gasless-api)[Next

FAQ](/docs/gasless-api/gasless-faq)

* [Signing objects](#signing-objects)
  + [Sign gasless approval object](#sign-gasless-approval-object)
  + [Sign trade object](#sign-trade-object)
* [Split signatures](#split-signatures)
* [POST the split signatures to /submit](#post-the-split-signatures-to-submit)
  + [Example request](#example-request)
  + [Example response](#example-response)
* [Status Code](#status-code)
* [Note for go-ethereum](#note-for-go-ethereum)

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
[https://0x.org/docs/gasless-api/guides/gasless-api-technical-appendix#splitting-signatures](https://0x.org/docs/gasless-api/guides/gasless-api-technical-appendix#splitting-signatures)
