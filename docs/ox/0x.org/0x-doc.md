---
title: 0x API v2
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
highlight_theme: darkula
headingLevel: 2

---

<!-- Generator: Widdershins v4.0.1 -->

<h1 id="0x-api">0x API v2</h1>

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

This is the official API reference for the latest 0x API (v2).

Base URLs:

* <a href="https://api.0x.org">https://api.0x.org</a>

# Authentication

* API Key (ApiKeyAuth)
    - Parameter Name: **0x-api-key**, in: header. 

<h1 id="0x-api-swap">Swap</h1>

Swap API endpoints

## swap::permit2::getPrice

<a id="opIdswap::permit2::getPrice"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/swap/permit2/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000 \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/swap/permit2/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000 HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/swap/permit2/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/swap/permit2/price',
  params: {
  'chainId' => 'integer',
'buyToken' => 'string',
'sellToken' => 'string',
'sellAmount' => 'string'
}, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/swap/permit2/price', params={
  'chainId': '1',  'buyToken': '0xdac17f958d2ee523a2206206994597c13d831ec7',  'sellToken': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',  'sellAmount': '100000000'
}, headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/swap/permit2/price', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/swap/permit2/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/swap/permit2/price", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /swap/permit2/price`

*getPrice (Permit2)*

Get the indicative price for a swap using Permit2 to set allowances

<h3 id="swap::permit2::getprice-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|chainId|query|integer|true|Chain ID. See [here](https://0x.org/docs/developer-resources/supported-chains) for the list of supported chains|
|buyToken|query|string|true|The contract address of the token to buy|
|sellToken|query|string|true|The contract address of the token to sell|
|sellAmount|query|string|true|The amount of `sellToken` in `sellToken` base units to sell|
|taker|query|string|false|The address which holds the `sellToken` balance and has the allowance set for the swap|
|txOrigin|query|string|false|The address of the external account that started the transaction. This is only needed if `taker` is a smart contract.|
|swapFeeRecipient|query|string|false|The wallet address to receive the specified trading fees. You must also specify the `swapFeeToken` and `swapFeeBps` in the request to use this feature. Learn more about setting up a trading fee/commission in the FAQs|
|swapFeeBps|query|integer|false|The amount in Bps of the `swapFeeToken` to charge and deliver to the `swapFeeRecipient`. You must also specify the `swapFeeRecipient` and `swapFeeToken` in the request to use this feature. For security, this field has a default limit of 1000 Bps. If your application requires a higher value, please reach out to us.|
|swapFeeToken|query|string|false|The contract address of the token to receive trading fees in. This must be set to the value of either the `buyToken` or the `sellToken`. You must also specify the `swapFeeRecipient` and `swapFeeBps` in the request to use this feature|
|tradeSurplusRecipient|query|string|false|The address to receive any trade surplus. If specified, this address will receive trade surplus when applicable. Otherwise, the taker will receive the surplus. This feature is only available to selected integrators on a custom pricing plan. In other cases, the surplus will be collected by 0x. For assistance with a custom plan, please contact support.|
|gasPrice|query|string|false|The target gas price (in wei) for the swap transaction. If not provided, the default value is based on the 0x gas price oracle|
|slippageBps|query|integer|false|The maximum acceptable slippage of the `buyToken` in Bps. If this parameter is set to 0, no slippage will be tolerated. If not provided, the default slippage tolerance is 100Bps|
|excludedSources|query|string|false|Liquidity sources e.g. Uniswap_V3, SushiSwap, 0x_RFQ to exclude from the provided quote. See https://api.0x.org/sources?chainId=<chain_id> with the desired chain's ID for a full list of sources. Separate multiple sources with a comma|
|sellEntireBalance|query|string|false|If set to `true`, the taker's entire `sellToken` balance will be sold during trade execution. The `sellAmount` should be the maximum estimated value, as close as possible to the actual taker's balance to ensure the best routing. Selling more than the `sellAmount` may cause the trade to revert. This feature is designed for cases where the precise sell amount is determined during execution. Learn more [here](https://0x.org/docs/0x-swap-api/advanced-topics/sell-entire-balance).|

#### Enumerated Values

|Parameter|Value|
|---|---|
|sellEntireBalance|true|
|sellEntireBalance|false|

> Example responses

> 200 Response

```json
{
  "blockNumber": "20114676",
  "buyAmount": "100032748",
  "buyToken": "0xdac17f958d2ee523a2206206994597c13d831ec7",
  "fees": {
    "integratorFee": null,
    "zeroExFee": null,
    "gasFee": null
  },
  "gas": "288095",
  "gasPrice": "7062490000",
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
  },
  "liquidityAvailable": true,
  "minBuyAmount": "99032421",
  "route": {
    "fills": [
      {
        "from": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "to": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "source": "SolidlyV3",
        "proportionBps": "10000"
      }
    ],
    "tokens": [
      {
        "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "symbol": "USDC"
      },
      {
        "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "symbol": "USDT"
      }
    ]
  },
  "sellAmount": "100000000",
  "sellToken": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "tokenMetadata": {
    "buyToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    },
    "sellToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    }
  },
  "totalNetworkFee": "2034668056550000",
  "zid": "0x111111111111111111111111"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="swap::permit2::getprice-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|403 error response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|422 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="swap::permit2::getprice-responseschema">Response Schema</h3>

#### Enumerated Values

|Property|Value|
|---|---|
|type|volume|
|type|volume|
|type|gas|
|liquidityAvailable|true|
|liquidityAvailable|false|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|
|name|SWAP_VALIDATION_FAILED|
|name|TOKEN_NOT_SUPPORTED|

Status Code **403**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|TAKER_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE|
|name|SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

## swap::permit2::getQuote

<a id="opIdswap::permit2::getQuote"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/swap/permit2/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/swap/permit2/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/swap/permit2/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/swap/permit2/quote',
  params: {
  'chainId' => 'integer',
'buyToken' => 'string',
'sellToken' => 'string',
'sellAmount' => 'string',
'taker' => 'string'
}, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/swap/permit2/quote', params={
  'chainId': '1',  'buyToken': '0xdac17f958d2ee523a2206206994597c13d831ec7',  'sellToken': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',  'sellAmount': '100000000',  'taker': '0x70a9f34f9b34c64957b9c401a97bfed35b95049e'
}, headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/swap/permit2/quote', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/swap/permit2/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/swap/permit2/quote", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /swap/permit2/quote`

*getQuote (Permit2)*

Get the firm quote for a swap using Permit2 to set allowances

<h3 id="swap::permit2::getquote-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|chainId|query|integer|true|Chain ID. See [here](https://0x.org/docs/developer-resources/supported-chains) for the list of supported chains|
|buyToken|query|string|true|The contract address of the token to buy|
|sellToken|query|string|true|The contract address of the token to sell|
|sellAmount|query|string|true|The amount of `sellToken` in `sellToken` base units to sell|
|taker|query|string|true|The address which holds the `sellToken` balance and has the allowance set for the swap|
|txOrigin|query|string|false|The address of the external account that started the transaction. This is only needed if `taker` is a smart contract.|
|swapFeeRecipient|query|string|false|The wallet address to receive the specified trading fees. You must also specify the `swapFeeToken` and `swapFeeBps` in the request to use this feature. Learn more about setting up a trading fee/commission in the FAQs|
|swapFeeBps|query|integer|false|The amount in Bps of the `swapFeeToken` to charge and deliver to the `swapFeeRecipient`. You must also specify the `swapFeeRecipient` and `swapFeeToken` in the request to use this feature. For security, this field has a default limit of 1000 Bps. If your application requires a higher value, please reach out to us.|
|swapFeeToken|query|string|false|The contract address of the token to receive trading fees in. This must be set to the value of either the `buyToken` or the `sellToken`. You must also specify the `swapFeeRecipient` and `swapFeeBps` in the request to use this feature|
|tradeSurplusRecipient|query|string|false|The address to receive any trade surplus. If specified, this address will receive trade surplus when applicable. Otherwise, the taker will receive the surplus. This feature is only available to selected integrators on a custom pricing plan. In other cases, the surplus will be collected by 0x. For assistance with a custom plan, please contact support.|
|gasPrice|query|string|false|The target gas price (in wei) for the swap transaction. If not provided, the default value is based on the 0x gas price oracle|
|slippageBps|query|integer|false|The maximum acceptable slippage of the `buyToken` in Bps. If this parameter is set to 0, no slippage will be tolerated. If not provided, the default slippage tolerance is 100Bps|
|excludedSources|query|string|false|Liquidity sources e.g. Uniswap_V3, SushiSwap, 0x_RFQ to exclude from the provided quote. See https://api.0x.org/sources?chainId=<chain_id> with the desired chain's ID for a full list of sources. Separate multiple sources with a comma|
|sellEntireBalance|query|string|false|If set to `true`, the taker's entire `sellToken` balance will be sold during trade execution. The `sellAmount` should be the maximum estimated value, as close as possible to the actual taker's balance to ensure the best routing. Selling more than the `sellAmount` may cause the trade to revert. This feature is designed for cases where the precise sell amount is determined during execution. Learn more [here](https://0x.org/docs/0x-swap-api/advanced-topics/sell-entire-balance).|

#### Enumerated Values

|Parameter|Value|
|---|---|
|sellEntireBalance|true|
|sellEntireBalance|false|

> Example responses

> 200 Response

```json
{
  "blockNumber": "20114692",
  "buyAmount": "100037537",
  "buyToken": "0xdac17f958d2ee523a2206206994597c13d831ec7",
  "fees": {
    "integratorFee": null,
    "zeroExFee": null,
    "gasFee": null
  },
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
  },
  "liquidityAvailable": true,
  "minBuyAmount": "99037162",
  "permit2": {
    "type": "Permit2",
    "hash": "0xab0c8909f2f8daed2891abb5e93762c65787e0067ef2ab9184bb635ad0f3df51",
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
        "chainId": 1,
        "verifyingContract": "0x000000000022d473030f116ddee9f6b43ac78ba3"
      },
      "message": {
        "permitted": {
          "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
          "amount": "100000000"
        },
        "spender": "0x7f6cee965959295cc64d0e6c00d99d6532d8e86b",
        "nonce": "2241959297937691820908574931991575",
        "deadline": "1718669420"
      },
      "primaryType": "PermitTransferFrom"
    }
  },
  "route": {
    "fills": [
      {
        "from": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "to": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "source": "SolidlyV3",
        "proportionBps": "10000"
      }
    ],
    "tokens": [
      {
        "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "symbol": "USDC"
      },
      {
        "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "symbol": "USDT"
      }
    ]
  },
  "sellAmount": "100000000",
  "sellToken": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "tokenMetadata": {
    "buyToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    },
    "sellToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    }
  },
  "totalNetworkFee": "1393685870940000",
  "transaction": {
    "to": "0x7f6cee965959295cc64d0e6c00d99d6532d8e86b",
    "data": "0x1fff991f00000000000000000000000070a9f34f9b34c64957b9c401a97bfed35b95049e000000000000000000000000dac17f958d2ee523a2206206994597c13d831ec70000000000000000000000000000000000000000000000000000000005e72fea00000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001c00000000000000000000000000000000000000000000000000000000000000144c1fb425e0000000000000000000000007f6cee965959295cc64d0e6c00d99d6532d8e86b000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480000000000000000000000000000000000000000000000000000000005f5e1000000000000000000000000000000000000006e898131631616b1779bad70bc17000000000000000000000000000000000000000000000000000000006670d06c00000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000041ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000016438c9c147000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb4800000000000000000000000000000000000000000000000000000000000027100000000000000000000000006146be494fee4c73540cb1c5f87536abf1452500000000000000000000000000000000000000000000000000000000000000004400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000084c31b8d7a0000000000000000000000007f6cee965959295cc64d0e6c00d99d6532d8e86b00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000005f5e10000000000000000000000000000000000000000000000000000000001000276a40000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "gas": "288079",
    "gasPrice": "4837860000",
    "value": "0"
  },
  "zid": "0x111111111111111111111111"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="swap::permit2::getquote-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|403 error response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|422 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="swap::permit2::getquote-responseschema">Response Schema</h3>

#### Enumerated Values

|Property|Value|
|---|---|
|type|volume|
|type|volume|
|type|gas|
|liquidityAvailable|true|
|type|Permit2|
|liquidityAvailable|false|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|
|name|SWAP_VALIDATION_FAILED|
|name|TOKEN_NOT_SUPPORTED|

Status Code **403**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|TAKER_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE|
|name|SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

## swap::allowanceHolder::getPrice

<a id="opIdswap::allowanceHolder::getPrice"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/swap/allowance-holder/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000 \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/swap/allowance-holder/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000 HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/swap/allowance-holder/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/swap/allowance-holder/price',
  params: {
  'chainId' => 'integer',
'buyToken' => 'string',
'sellToken' => 'string',
'sellAmount' => 'string'
}, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/swap/allowance-holder/price', params={
  'chainId': '1',  'buyToken': '0xdac17f958d2ee523a2206206994597c13d831ec7',  'sellToken': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',  'sellAmount': '100000000'
}, headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/swap/allowance-holder/price', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/swap/allowance-holder/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/swap/allowance-holder/price", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /swap/allowance-holder/price`

*getPrice (Allowance Holder)*

Get the indicative price for a swap using Allowance Holder to set allowances

<h3 id="swap::allowanceholder::getprice-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|chainId|query|integer|true|Chain ID. See [here](https://0x.org/docs/developer-resources/supported-chains) for the list of supported chains|
|buyToken|query|string|true|The contract address of the token to buy|
|sellToken|query|string|true|The contract address of the token to sell|
|sellAmount|query|string|true|The amount of `sellToken` in `sellToken` base units to sell|
|taker|query|string|false|The address which holds the `sellToken` balance and has the allowance set for the swap|
|txOrigin|query|string|false|The address of the external account that started the transaction. This is only needed if `taker` is a smart contract.|
|swapFeeRecipient|query|string|false|The wallet address to receive the specified trading fees. You must also specify the `swapFeeToken` and `swapFeeBps` in the request to use this feature. Learn more about setting up a trading fee/commission in the FAQs|
|swapFeeBps|query|integer|false|The amount in Bps of the `swapFeeToken` to charge and deliver to the `swapFeeRecipient`. You must also specify the `swapFeeRecipient` and `swapFeeToken` in the request to use this feature. For security, this field has a default limit of 1000 Bps. If your application requires a higher value, please reach out to us.|
|swapFeeToken|query|string|false|The contract address of the token to receive trading fees in. This must be set to the value of either the `buyToken` or the `sellToken`. You must also specify the `swapFeeRecipient` and `swapFeeBps` in the request to use this feature|
|tradeSurplusRecipient|query|string|false|The address to receive any trade surplus. If specified, this address will receive trade surplus when applicable. Otherwise, the taker will receive the surplus. This feature is only available to selected integrators on a custom pricing plan. In other cases, the surplus will be collected by 0x. For assistance with a custom plan, please contact support.|
|gasPrice|query|string|false|The target gas price (in wei) for the swap transaction. If not provided, the default value is based on the 0x gas price oracle|
|slippageBps|query|integer|false|The maximum acceptable slippage of the `buyToken` in Bps. If this parameter is set to 0, no slippage will be tolerated. If not provided, the default slippage tolerance is 100Bps|
|excludedSources|query|string|false|Liquidity sources e.g. Uniswap_V3, SushiSwap, 0x_RFQ to exclude from the provided quote. See https://api.0x.org/sources?chainId=<chain_id> with the desired chain's ID for a full list of sources. Separate multiple sources with a comma|
|sellEntireBalance|query|string|false|If set to `true`, the taker's entire `sellToken` balance will be sold during trade execution. The `sellAmount` should be the maximum estimated value, as close as possible to the actual taker's balance to ensure the best routing. Selling more than the `sellAmount` may cause the trade to revert. This feature is designed for cases where the precise sell amount is determined during execution. Learn more [here](https://0x.org/docs/0x-swap-api/advanced-topics/sell-entire-balance).|

#### Enumerated Values

|Parameter|Value|
|---|---|
|sellEntireBalance|true|
|sellEntireBalance|false|

> Example responses

> 200 Response

```json
{
  "blockNumber": "20114676",
  "buyAmount": "100032748",
  "buyToken": "0xdac17f958d2ee523a2206206994597c13d831ec7",
  "fees": {
    "integratorFee": null,
    "zeroExFee": null,
    "gasFee": null
  },
  "gas": "288095",
  "gasPrice": "7062490000",
  "issues": {
    "allowance": {
      "actual": "0",
      "spender": "0x0000000000001ff3684f28c67538d4d072c22734"
    },
    "balance": {
      "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "actual": "0",
      "expected": "100000000"
    },
    "simulationIncomplete": false,
    "invalidSourcesPassed": []
  },
  "liquidityAvailable": true,
  "minBuyAmount": "99032421",
  "route": {
    "fills": [
      {
        "from": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "to": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "source": "SolidlyV3",
        "proportionBps": "10000"
      }
    ],
    "tokens": [
      {
        "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "symbol": "USDC"
      },
      {
        "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "symbol": "USDT"
      }
    ]
  },
  "sellAmount": "100000000",
  "sellToken": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "tokenMetadata": {
    "buyToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    },
    "sellToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    }
  },
  "totalNetworkFee": "2034668056550000",
  "zid": "0x111111111111111111111111"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="swap::allowanceholder::getprice-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|403 error response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|422 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="swap::allowanceholder::getprice-responseschema">Response Schema</h3>

#### Enumerated Values

|Property|Value|
|---|---|
|type|volume|
|type|volume|
|type|gas|
|liquidityAvailable|true|
|liquidityAvailable|false|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|
|name|SWAP_VALIDATION_FAILED|
|name|TOKEN_NOT_SUPPORTED|

Status Code **403**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|TAKER_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE|
|name|SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

## swap::allowanceHolder::getQuote

<a id="opIdswap::allowanceHolder::getQuote"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/swap/allowance-holder/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/swap/allowance-holder/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/swap/allowance-holder/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/swap/allowance-holder/quote',
  params: {
  'chainId' => 'integer',
'buyToken' => 'string',
'sellToken' => 'string',
'sellAmount' => 'string',
'taker' => 'string'
}, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/swap/allowance-holder/quote', params={
  'chainId': '1',  'buyToken': '0xdac17f958d2ee523a2206206994597c13d831ec7',  'sellToken': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',  'sellAmount': '100000000',  'taker': '0x70a9f34f9b34c64957b9c401a97bfed35b95049e'
}, headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/swap/allowance-holder/quote', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/swap/allowance-holder/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=100000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/swap/allowance-holder/quote", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /swap/allowance-holder/quote`

*getQuote (Allowance Holder)*

Get the firm quote for a swap using Allowance Holder to set allowances

<h3 id="swap::allowanceholder::getquote-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|chainId|query|integer|true|Chain ID. See [here](https://0x.org/docs/developer-resources/supported-chains) for the list of supported chains|
|buyToken|query|string|true|The contract address of the token to buy|
|sellToken|query|string|true|The contract address of the token to sell|
|sellAmount|query|string|true|The amount of `sellToken` in `sellToken` base units to sell|
|taker|query|string|true|The address which holds the `sellToken` balance and has the allowance set for the swap|
|txOrigin|query|string|false|The address of the external account that started the transaction. This is only needed if `taker` is a smart contract.|
|swapFeeRecipient|query|string|false|The wallet address to receive the specified trading fees. You must also specify the `swapFeeToken` and `swapFeeBps` in the request to use this feature. Learn more about setting up a trading fee/commission in the FAQs|
|swapFeeBps|query|integer|false|The amount in Bps of the `swapFeeToken` to charge and deliver to the `swapFeeRecipient`. You must also specify the `swapFeeRecipient` and `swapFeeToken` in the request to use this feature. For security, this field has a default limit of 1000 Bps. If your application requires a higher value, please reach out to us.|
|swapFeeToken|query|string|false|The contract address of the token to receive trading fees in. This must be set to the value of either the `buyToken` or the `sellToken`. You must also specify the `swapFeeRecipient` and `swapFeeBps` in the request to use this feature|
|tradeSurplusRecipient|query|string|false|The address to receive any trade surplus. If specified, this address will receive trade surplus when applicable. Otherwise, the taker will receive the surplus. This feature is only available to selected integrators on a custom pricing plan. In other cases, the surplus will be collected by 0x. For assistance with a custom plan, please contact support.|
|gasPrice|query|string|false|The target gas price (in wei) for the swap transaction. If not provided, the default value is based on the 0x gas price oracle|
|slippageBps|query|integer|false|The maximum acceptable slippage of the `buyToken` in Bps. If this parameter is set to 0, no slippage will be tolerated. If not provided, the default slippage tolerance is 100Bps|
|excludedSources|query|string|false|Liquidity sources e.g. Uniswap_V3, SushiSwap, 0x_RFQ to exclude from the provided quote. See https://api.0x.org/sources?chainId=<chain_id> with the desired chain's ID for a full list of sources. Separate multiple sources with a comma|
|sellEntireBalance|query|string|false|If set to `true`, the taker's entire `sellToken` balance will be sold during trade execution. The `sellAmount` should be the maximum estimated value, as close as possible to the actual taker's balance to ensure the best routing. Selling more than the `sellAmount` may cause the trade to revert. This feature is designed for cases where the precise sell amount is determined during execution. Learn more [here](https://0x.org/docs/0x-swap-api/advanced-topics/sell-entire-balance).|

#### Enumerated Values

|Parameter|Value|
|---|---|
|sellEntireBalance|true|
|sellEntireBalance|false|

> Example responses

> 200 Response

```json
{
  "blockNumber": "20114692",
  "buyAmount": "100037537",
  "buyToken": "0xdac17f958d2ee523a2206206994597c13d831ec7",
  "fees": {
    "integratorFee": null,
    "zeroExFee": null,
    "gasFee": null
  },
  "issues": {
    "allowance": {
      "actual": "0",
      "spender": "0x0000000000001ff3684f28c67538d4d072c22734"
    },
    "balance": {
      "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "actual": "0",
      "expected": "100000000"
    },
    "simulationIncomplete": false,
    "invalidSourcesPassed": []
  },
  "liquidityAvailable": true,
  "minBuyAmount": "99037162",
  "route": {
    "fills": [
      {
        "from": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "to": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "source": "SolidlyV3",
        "proportionBps": "10000"
      }
    ],
    "tokens": [
      {
        "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "symbol": "USDC"
      },
      {
        "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "symbol": "USDT"
      }
    ]
  },
  "sellAmount": "100000000",
  "sellToken": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "tokenMetadata": {
    "buyToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    },
    "sellToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    }
  },
  "totalNetworkFee": "1393685870940000",
  "transaction": {
    "to": "0x7f6cee965959295cc64d0e6c00d99d6532d8e86b",
    "data": "0x1fff991f00000000000000000000000070a9f34f9b34c64957b9c401a97bfed35b95049e000000000000000000000000dac17f958d2ee523a2206206994597c13d831ec70000000000000000000000000000000000000000000000000000000005e72fea00000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001c00000000000000000000000000000000000000000000000000000000000000144c1fb425e0000000000000000000000007f6cee965959295cc64d0e6c00d99d6532d8e86b000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480000000000000000000000000000000000000000000000000000000005f5e1000000000000000000000000000000000000006e898131631616b1779bad70bc17000000000000000000000000000000000000000000000000000000006670d06c00000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000041ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000016438c9c147000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb4800000000000000000000000000000000000000000000000000000000000027100000000000000000000000006146be494fee4c73540cb1c5f87536abf1452500000000000000000000000000000000000000000000000000000000000000004400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000084c31b8d7a0000000000000000000000007f6cee965959295cc64d0e6c00d99d6532d8e86b00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000005f5e10000000000000000000000000000000000000000000000000000000001000276a40000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "gas": "288079",
    "gasPrice": "4837860000",
    "value": "0"
  },
  "zid": "0x111111111111111111111111"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="swap::allowanceholder::getquote-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|403 error response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|422 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="swap::allowanceholder::getquote-responseschema">Response Schema</h3>

#### Enumerated Values

|Property|Value|
|---|---|
|type|volume|
|type|volume|
|type|gas|
|liquidityAvailable|true|
|liquidityAvailable|false|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|
|name|SWAP_VALIDATION_FAILED|
|name|TOKEN_NOT_SUPPORTED|

Status Code **403**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|TAKER_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE|
|name|SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

## swap::chains

<a id="opIdswap::chains"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/swap/chains \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/swap/chains HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/swap/chains',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/swap/chains',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/swap/chains', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/swap/chains', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/swap/chains");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/swap/chains", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /swap/chains`

*getChains*

Get list of supported chains for swap

<h3 id="swap::chains-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|

> Example responses

> 200 Response

```json
[
  {
    "chainName": "Ethereum",
    "chainId": "1"
  },
  {
    "chainName": "Optimism",
    "chainId": "10"
  },
  {
    "chainName": "BSC",
    "chainId": "56"
  },
  {
    "chainName": "Polygon",
    "chainId": "137"
  },
  {
    "chainName": "Base",
    "chainId": "8453"
  },
  {
    "chainName": "Arbitrum",
    "chainId": "42161"
  },
  {
    "chainName": "Avalanche",
    "chainId": "43114"
  },
  {
    "chainName": "Linea",
    "chainId": "59144"
  },
  {
    "chainName": "Scroll",
    "chainId": "534352"
  },
  {
    "chainName": "Mantle",
    "chainId": "5000"
  },
  {
    "chainName": "Blast",
    "chainId": "81457"
  },
  {
    "chainName": "Mode",
    "chainId": "34443"
  }
]
```

> 500 Response

```json
{
  "name": "INTERNAL_SERVER_ERROR",
  "message": "string",
  "data": {
    "zid": "string"
  }
}
```

<h3 id="swap::chains-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="swap::chains-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» chains|[object]|true|none|none|
|»» chainId|number|true|none|none|
|»» chainName|string|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

<h1 id="0x-api-gasless">Gasless</h1>

Gasless API endpoints

## gasless::getPrice

<a id="opIdgasless::getPrice"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/gasless/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=300000000 \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/gasless/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=300000000 HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/gasless/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=300000000',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/gasless/price',
  params: {
  'chainId' => 'integer',
'buyToken' => 'string',
'sellToken' => 'string',
'sellAmount' => 'string'
}, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/gasless/price', params={
  'chainId': '1',  'buyToken': '0xdac17f958d2ee523a2206206994597c13d831ec7',  'sellToken': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',  'sellAmount': '300000000'
}, headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/gasless/price', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/gasless/price?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=300000000");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/gasless/price", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /gasless/price`

*getPrice*

Get the indicative price for a gasless swap

<h3 id="gasless::getprice-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|chainId|query|integer|true|Chain ID. See [here](https://0x.org/docs/developer-resources/supported-chains) for the list of supported chains|
|buyToken|query|string|true|The contract address of the token to buy|
|sellToken|query|string|true|The contract address of the token to sell. Native token is not supported|
|sellAmount|query|string|true|The amount of `sellToken` in `sellToken` base units to sell|
|taker|query|string|false|The address which holds the `sellToken` balance and has the allowance set for the swap|
|swapFeeRecipient|query|string|false|The wallet address to receive the specified trading fees. You must also specify the `swapFeeToken` and `swapFeeBps` in the request to use this feature. Learn more about setting up a trading fee/commission in the FAQs|
|swapFeeBps|query|integer|false|The amount in Bps of the `swapFeeToken` to charge and deliver to the `swapFeeRecipient`. You must also specify the `swapFeeRecipient` and `swapFeeToken` in the request to use this feature. For security, this field has a default limit of 1000 Bps. If your application requires a higher value, please reach out to us.|
|swapFeeToken|query|string|false|The contract address of the token to receive trading fees in. This must be set to the value of either the `buyToken` or the `sellToken`. You must also specify the `swapFeeRecipient` and `swapFeeBps` in the request to use this feature|
|tradeSurplusRecipient|query|string|false|The address to receive any trade surplus. If specified, this address will receive trade surplus when applicable. Otherwise, the taker will receive the surplus. This feature is only available to selected integrators on a custom pricing plan. In other cases, the surplus will be collected by 0x. For assistance with a custom plan, please contact support.|
|slippageBps|query|integer|false|The maximum acceptable slippage of the `buyToken` in Bps. 0x sets the optimal slippage tolerance per trade by default. To mitigate the risk of MEV attacks, we recommend adjusting this value only when trading low-liquidity tokens.|
|excludedSources|query|string|false|Liquidity sources e.g. Uniswap_V3, SushiSwap, 0x_RFQ to exclude from the provided quote. See https://api.0x.org/sources?chainId=<chain_id> with the desired chain's ID for a full list of sources. Separate multiple sources with a comma|

> Example responses

> 200 Response

```json
{
  "blockNumber": "20114764",
  "buyAmount": "291527064",
  "buyToken": "0xdac17f958d2ee523a2206206994597c13d831ec7",
  "fees": {
    "integratorFee": null,
    "zeroExFee": {
      "amount": "150053",
      "token": "0xdac17f958d2ee523a2206206994597c13d831ec7",
      "type": "volume"
    },
    "gasFee": {
      "amount": "8430138",
      "token": "0xdac17f958d2ee523a2206206994597c13d831ec7",
      "type": "gas"
    }
  },
  "issues": {
    "allowance": {
      "actual": "0",
      "spender": "0x000000000022d473030f116ddee9f6b43ac78ba3"
    },
    "balance": {
      "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "actual": "0",
      "expected": "300000000"
    },
    "simulationIncomplete": false,
    "invalidSourcesPassed": []
  },
  "liquidityAvailable": true,
  "minBuyAmount": "290652483",
  "route": {
    "fills": [
      {
        "from": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "to": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "source": "SolidlyV3",
        "proportionBps": "10000"
      }
    ],
    "tokens": [
      {
        "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "symbol": "USDC"
      },
      {
        "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "symbol": "USDT"
      }
    ]
  },
  "sellAmount": "300000000",
  "sellToken": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "target": "0x7c39a136ea20b3483e402ea031c1f3c019bab24b",
  "tokenMetadata": {
    "buyToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    },
    "sellToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    }
  },
  "zid": "0x111111111111111111111111"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="gasless::getprice-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|403 error response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|422 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="gasless::getprice-responseschema">Response Schema</h3>

#### Enumerated Values

|Property|Value|
|---|---|
|type|volume|
|type|volume|
|type|gas|
|liquidityAvailable|true|
|liquidityAvailable|false|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|
|name|UNABLE_TO_CALCULATE_GAS_FEE|
|name|SELL_AMOUNT_TOO_SMALL|
|name|SWAP_VALIDATION_FAILED|
|name|TOKEN_NOT_SUPPORTED|

Status Code **403**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|TAKER_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE|
|name|SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

## gasless::getQuote

<a id="opIdgasless::getQuote"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/gasless/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=300000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/gasless/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=300000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/gasless/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=300000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/gasless/quote',
  params: {
  'chainId' => 'integer',
'buyToken' => 'string',
'sellToken' => 'string',
'sellAmount' => 'string',
'taker' => 'string'
}, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/gasless/quote', params={
  'chainId': '1',  'buyToken': '0xdac17f958d2ee523a2206206994597c13d831ec7',  'sellToken': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',  'sellAmount': '300000000',  'taker': '0x70a9f34f9b34c64957b9c401a97bfed35b95049e'
}, headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/gasless/quote', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/gasless/quote?chainId=1&buyToken=0xdac17f958d2ee523a2206206994597c13d831ec7&sellToken=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&sellAmount=300000000&taker=0x70a9f34f9b34c64957b9c401a97bfed35b95049e");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/gasless/quote", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /gasless/quote`

*getQuote*

Get the firm quote for a gasless swap

<h3 id="gasless::getquote-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|chainId|query|integer|true|Chain ID. See [here](https://0x.org/docs/developer-resources/supported-chains) for the list of supported chains|
|buyToken|query|string|true|The contract address of the token to buy|
|sellToken|query|string|true|The contract address of the token to sell. Native token is not supported|
|sellAmount|query|string|true|The amount of `sellToken` in `sellToken` base units to sell|
|taker|query|string|true|The address which holds the `sellToken` balance and has the allowance set for the swap|
|swapFeeRecipient|query|string|false|The wallet address to receive the specified trading fees. You must also specify the `swapFeeToken` and `swapFeeBps` in the request to use this feature. Learn more about setting up a trading fee/commission in the FAQs|
|swapFeeBps|query|integer|false|The amount in Bps of the `swapFeeToken` to charge and deliver to the `swapFeeRecipient`. You must also specify the `swapFeeRecipient` and `swapFeeToken` in the request to use this feature. For security, this field has a default limit of 1000 Bps. If your application requires a higher value, please reach out to us.|
|swapFeeToken|query|string|false|The contract address of the token to receive trading fees in. This must be set to the value of either the `buyToken` or the `sellToken`. You must also specify the `swapFeeRecipient` and `swapFeeBps` in the request to use this feature|
|tradeSurplusRecipient|query|string|false|The address to receive any trade surplus. If specified, this address will receive trade surplus when applicable. Otherwise, the taker will receive the surplus. This feature is only available to selected integrators on a custom pricing plan. In other cases, the surplus will be collected by 0x. For assistance with a custom plan, please contact support.|
|slippageBps|query|integer|false|The maximum acceptable slippage of the `buyToken` in Bps. 0x sets the optimal slippage tolerance per trade by default. To mitigate the risk of MEV attacks, we recommend adjusting this value only when trading low-liquidity tokens.|
|excludedSources|query|string|false|Liquidity sources e.g. Uniswap_V3, SushiSwap, 0x_RFQ to exclude from the provided quote. See https://api.0x.org/sources?chainId=<chain_id> with the desired chain's ID for a full list of sources. Separate multiple sources with a comma|

> Example responses

> 200 Response

```json
{
  "approval": {
    "type": "permit",
    "hash": "0xf3849ebcd806e518f2d3457b76d31ccf41be07fe64f0a25bbe798f1b9edde872",
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
            "name": "chainId",
            "type": "uint256"
          },
          {
            "name": "verifyingContract",
            "type": "address"
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
        "name": "USD Coin",
        "version": "2",
        "chainId": 1,
        "verifyingContract": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
      },
      "message": {
        "owner": "0x70a9f34f9b34c64957b9c401a97bfed35b95049e",
        "spender": "0x000000000022d473030f116ddee9f6b43ac78ba3",
        "value": "300000000",
        "nonce": 0,
        "deadline": "1718667104"
      },
      "primaryType": "Permit"
    }
  },
  "blockNumber": "20114747",
  "buyAmount": "292995086",
  "buyToken": "0xdac17f958d2ee523a2206206994597c13d831ec7",
  "fees": {
    "integratorFee": null,
    "zeroExFee": {
      "amount": "150053",
      "token": "0xdac17f958d2ee523a2206206994597c13d831ec7",
      "type": "volume"
    },
    "gasFee": {
      "amount": "6962116",
      "token": "0xdac17f958d2ee523a2206206994597c13d831ec7",
      "type": "gas"
    }
  },
  "issues": {
    "allowance": {
      "actual": "0",
      "spender": "0x000000000022d473030f116ddee9f6b43ac78ba3"
    },
    "balance": {
      "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "actual": "0",
      "expected": "300000000"
    },
    "simulationIncomplete": false,
    "invalidSourcesPassed": []
  },
  "liquidityAvailable": true,
  "minBuyAmount": "292116101",
  "route": {
    "fills": [
      {
        "from": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "to": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "source": "SolidlyV3",
        "proportionBps": "10000"
      }
    ],
    "tokens": [
      {
        "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "symbol": "USDC"
      },
      {
        "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "symbol": "USDT"
      }
    ]
  },
  "sellAmount": "300000000",
  "sellToken": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "target": "0x7c39a136ea20b3483e402ea031c1f3c019bab24b",
  "tokenMetadata": {
    "buyToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    },
    "sellToken": {
      "buyTaxBps": "0",
      "sellTaxBps": "0"
    }
  },
  "trade": {
    "type": "settler_metatransaction",
    "hash": "0x3ff032fa3a970a3f2b763afce093fd133ced63c0b097ab12ae1441b42de4a167",
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
        ]
      },
      "domain": {
        "name": "Permit2",
        "chainId": 1,
        "verifyingContract": "0x000000000022d473030f116ddee9f6b43ac78ba3"
      },
      "message": {
        "permitted": {
          "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
          "amount": "300000000"
        },
        "spender": "0x7c39a136ea20b3483e402ea031c1f3c019bab24b",
        "nonce": "2241959297937691820908574931991567",
        "deadline": "1718670104",
        "slippageAndActions": {
          "recipient": "0x70a9f34f9b34c64957b9c401a97bfed35b95049e",
          "buyToken": "0xdac17f958d2ee523a2206206994597c13d831ec7",
          "minAmountOut": "292116101",
          "actions": [
            "0x0dfeb4190000000000000000000000007c39a136ea20b3483e402ea031c1f3c019bab24b000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480000000000000000000000000000000000000000000000000000000011e1a3000000000000000000000000000000000000006e898131631616b1779bad70bc0f000000000000000000000000000000000000000000000000000000006670d318",
            "0x38c9c147000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb4800000000000000000000000000000000000000000000000000000000000027100000000000000000000000006146be494fee4c73540cb1c5f87536abf1452500000000000000000000000000000000000000000000000000000000000000004400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000084c31b8d7a0000000000000000000000007c39a136ea20b3483e402ea031c1f3c019bab24b00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000011e1a30000000000000000000000000000000000000000000000000000000001000276a400000000000000000000000000000000000000000000000000000000",
            "0x38c9c147000000000000000000000000dac17f958d2ee523a2206206994597c13d831ec700000000000000000000000000000000000000000000000000000000000000ec000000000000000000000000dac17f958d2ee523a2206206994597c13d831ec7000000000000000000000000000000000000000000000000000000000000002400000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000044a9059cbb00000000000000000000000038f5e5b4da37531a6e85161e337e0238bb27aa90000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
          ]
        }
      },
      "primaryType": "PermitWitnessTransferFrom"
    }
  },
  "zid": "0x111111111111111111111111"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="gasless::getquote-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|403 error response|Inline|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|422 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="gasless::getquote-responseschema">Response Schema</h3>

#### Enumerated Values

|Property|Value|
|---|---|
|type|executeMetaTransaction::approve|
|type|permit|
|type|daiPermit|
|type|volume|
|type|volume|
|type|gas|
|liquidityAvailable|true|
|type|settler_metatransaction|
|type|settler_intent|
|liquidityAvailable|false|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|
|name|INSUFFICIENT_BALANCE|
|name|UNABLE_TO_CALCULATE_GAS_FEE|
|name|SELL_AMOUNT_TOO_SMALL|
|name|SWAP_VALIDATION_FAILED|
|name|TOKEN_NOT_SUPPORTED|

Status Code **403**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|TAKER_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE|
|name|SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

## gasless::submit

<a id="opIdgasless::submit"></a>

> Code samples

```shell
# You can also use wget
curl -X POST https://api.0x.org/gasless/submit \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
POST https://api.0x.org/gasless/submit HTTP/1.1
Host: api.0x.org
Content-Type: application/json
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript
const inputBody = '{
  "chainId": 0,
  "approval": {
    "type": "executeMetaTransaction::approve",
    "eip712": {
      "types": {
        "EIP712Domain": [
          {
            "name": "string",
            "type": "string"
          }
        ],
        "Permit": [
          {
            "name": "string",
            "type": "string"
          }
        ]
      },
      "domain": {
        "name": "string",
        "version": "string",
        "chainId": 0,
        "verifyingContract": "string",
        "salt": "string"
      },
      "message": {
        "owner": "string",
        "spender": "string",
        "value": "string",
        "nonce": 0,
        "deadline": "string"
      },
      "primaryType": "Permit"
    },
    "signature": {
      "signatureType": 0,
      "v": 0,
      "r": "string",
      "s": "string"
    }
  },
  "trade": {
    "type": "settler_metatransaction",
    "eip712": {
      "types": {
        "property1": [
          {
            "name": "string",
            "type": "string"
          }
        ],
        "property2": [
          {
            "name": "string",
            "type": "string"
          }
        ]
      },
      "primaryType": "string",
      "domain": {
        "name": "string",
        "version": "string",
        "chainId": 0,
        "verifyingContract": "string",
        "salt": "string"
      },
      "message": {
        "permitted": {
          "token": "string",
          "amount": "string"
        },
        "spender": "string",
        "nonce": "string",
        "deadline": "string",
        "slippageAndActions": {
          "recipient": "string",
          "buyToken": "string",
          "minAmountOut": "string",
          "actions": [
            "string"
          ]
        }
      }
    },
    "signature": {
      "signatureType": 0,
      "v": 0,
      "r": "string",
      "s": "string"
    }
  }
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/gasless/submit',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.post 'https://api.0x.org/gasless/submit',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.post('https://api.0x.org/gasless/submit', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','https://api.0x.org/gasless/submit', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/gasless/submit");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "https://api.0x.org/gasless/submit", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /gasless/submit`

*submit*

Submit a gasless swap

> Body parameter

```json
{
  "chainId": 0,
  "approval": {
    "type": "executeMetaTransaction::approve",
    "eip712": {
      "types": {
        "EIP712Domain": [
          {
            "name": "string",
            "type": "string"
          }
        ],
        "Permit": [
          {
            "name": "string",
            "type": "string"
          }
        ]
      },
      "domain": {
        "name": "string",
        "version": "string",
        "chainId": 0,
        "verifyingContract": "string",
        "salt": "string"
      },
      "message": {
        "owner": "string",
        "spender": "string",
        "value": "string",
        "nonce": 0,
        "deadline": "string"
      },
      "primaryType": "Permit"
    },
    "signature": {
      "signatureType": 0,
      "v": 0,
      "r": "string",
      "s": "string"
    }
  },
  "trade": {
    "type": "settler_metatransaction",
    "eip712": {
      "types": {
        "property1": [
          {
            "name": "string",
            "type": "string"
          }
        ],
        "property2": [
          {
            "name": "string",
            "type": "string"
          }
        ]
      },
      "primaryType": "string",
      "domain": {
        "name": "string",
        "version": "string",
        "chainId": 0,
        "verifyingContract": "string",
        "salt": "string"
      },
      "message": {
        "permitted": {
          "token": "string",
          "amount": "string"
        },
        "spender": "string",
        "nonce": "string",
        "deadline": "string",
        "slippageAndActions": {
          "recipient": "string",
          "buyToken": "string",
          "minAmountOut": "string",
          "actions": [
            "string"
          ]
        }
      }
    },
    "signature": {
      "signatureType": 0,
      "v": 0,
      "r": "string",
      "s": "string"
    }
  }
}
```

<h3 id="gasless::submit-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|body|body|object|true|none|
|» chainId|body|integer|true|Chain ID. See [here](https://0x.org/docs/developer-resources/supported-chains) for the list of supported chains|
|» approval|body|object¦null|false|The gasless approval object from the quote endpoint including its signature|
|»» type|body|string|true|The `approval.type` from the quote endpoint|
|»» eip712|body|any|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» types|body|object|true|none|
|»»»»» EIP712Domain|body|[object]|true|none|
|»»»»»» name|body|string|true|none|
|»»»»»» type|body|string|true|none|
|»»»»» Permit|body|[object]|true|none|
|»»»»»» name|body|string|true|none|
|»»»»»» type|body|string|true|none|
|»»»» domain|body|object|true|none|
|»»»»» name|body|string|false|none|
|»»»»» version|body|string|false|none|
|»»»»» chainId|body|number|false|none|
|»»»»» verifyingContract|body|string|false|none|
|»»»»» salt|body|string|false|none|
|»»»» message|body|object|true|none|
|»»»»» owner|body|string|true|none|
|»»»»» spender|body|string|true|none|
|»»»»» value|body|string|true|none|
|»»»»» nonce|body|number|true|none|
|»»»»» deadline|body|string|true|none|
|»»»» primaryType|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» types|body|object|true|none|
|»»»»» EIP712Domain|body|[object]|true|none|
|»»»»»» name|body|string|true|none|
|»»»»»» type|body|string|true|none|
|»»»»» Permit|body|[object]|true|none|
|»»»»»» name|body|string|true|none|
|»»»»»» type|body|string|true|none|
|»»»» domain|body|object|true|none|
|»»»»» name|body|string|false|none|
|»»»»» version|body|string|false|none|
|»»»»» chainId|body|number|false|none|
|»»»»» verifyingContract|body|string|false|none|
|»»»»» salt|body|string|false|none|
|»»»» message|body|object|true|none|
|»»»»» holder|body|string|true|none|
|»»»»» spender|body|string|true|none|
|»»»»» nonce|body|number|true|none|
|»»»»» expiry|body|string|true|none|
|»»»»» allowed|body|boolean|true|none|
|»»»» primaryType|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» types|body|object|true|none|
|»»»»» EIP712Domain|body|[object]|true|none|
|»»»»»» name|body|string|true|none|
|»»»»»» type|body|string|true|none|
|»»»»» MetaTransaction|body|[object]|true|none|
|»»»»»» name|body|string|true|none|
|»»»»»» type|body|string|true|none|
|»»»» domain|body|object|true|none|
|»»»»» name|body|string|false|none|
|»»»»» version|body|string|false|none|
|»»»»» chainId|body|number|false|none|
|»»»»» verifyingContract|body|string|false|none|
|»»»»» salt|body|string|false|none|
|»»»» message|body|object|true|none|
|»»»»» nonce|body|number|true|none|
|»»»»» from|body|string|true|none|
|»»»»» functionSignature|body|string|true|none|
|»»»» primaryType|body|string|true|none|
|»» signature|body|object|true|none|
|»»» signatureType|body|number|true|none|
|»»» v|body|number|true|none|
|»»» r|body|string|true|none|
|»»» s|body|string|true|none|
|» trade|body|object|true|The trade object from the quote endpoint including its signature|
|»» type|body|string|true|The `trade.type` from the quote endpoint|
|»» eip712|body|object|true|The `trade.eip712` from the quote endpoint|
|»»» types|body|object|true|none|
|»»»» **additionalProperties**|body|[object]|false|none|
|»»»»» name|body|string|true|none|
|»»»»» type|body|string|true|none|
|»»» primaryType|body|string|true|none|
|»»» domain|body|object|true|none|
|»»»» name|body|string|false|none|
|»»»» version|body|string|false|none|
|»»»» chainId|body|number|false|none|
|»»»» verifyingContract|body|string|false|none|
|»»»» salt|body|string|false|none|
|»»» message|body|any|true|none|
|»»»» *anonymous*|body|object|false|none|
|»»»»» permitted|body|object|true|none|
|»»»»»» token|body|string|true|none|
|»»»»»» amount|body|any|true|none|
|»»»»»»» *anonymous*|body|string|false|none|
|»»»»»»» *anonymous*|body|number|false|none|
|»»»»»»» *anonymous*|body|any|false|none|
|»»»»» spender|body|string|true|none|
|»»»»» nonce|body|any|true|none|
|»»»»»» *anonymous*|body|string|false|none|
|»»»»»» *anonymous*|body|number|false|none|
|»»»»»» *anonymous*|body|any|false|none|
|»»»»» deadline|body|any|true|none|
|»»»»»» *anonymous*|body|string|false|none|
|»»»»»» *anonymous*|body|number|false|none|
|»»»»»» *anonymous*|body|any|false|none|
|»»»»» slippageAndActions|body|object|true|none|
|»»»»»» recipient|body|string|true|none|
|»»»»»» buyToken|body|string|true|none|
|»»»»»» minAmountOut|body|any|true|none|
|»»»»»»» *anonymous*|body|string|false|none|
|»»»»»»» *anonymous*|body|number|false|none|
|»»»»»»» *anonymous*|body|any|false|none|
|»»»»»» actions|body|[string]|true|none|
|»»»» *anonymous*|body|object|false|none|
|»»»»» permitted|body|object|true|none|
|»»»»»» token|body|string|true|none|
|»»»»»» amount|body|any|true|none|
|»»»»»»» *anonymous*|body|string|false|none|
|»»»»»»» *anonymous*|body|number|false|none|
|»»»»»»» *anonymous*|body|any|false|none|
|»»»»» spender|body|string|true|none|
|»»»»» nonce|body|any|true|none|
|»»»»»» *anonymous*|body|string|false|none|
|»»»»»» *anonymous*|body|number|false|none|
|»»»»»» *anonymous*|body|any|false|none|
|»»»»» deadline|body|any|true|none|
|»»»»»» *anonymous*|body|string|false|none|
|»»»»»» *anonymous*|body|number|false|none|
|»»»»»» *anonymous*|body|any|false|none|
|»»»»» slippage|body|object|true|none|
|»»»»»» recipient|body|string|true|none|
|»»»»»» buyToken|body|string|true|none|
|»»»»»» minAmountOut|body|any|true|none|
|»»»»»»» *anonymous*|body|string|false|none|
|»»»»»»» *anonymous*|body|number|false|none|
|»»»»»»» *anonymous*|body|any|false|none|
|»» signature|body|object|true|none|
|»»» signatureType|body|number|true|none|
|»»» v|body|number|true|none|
|»»» r|body|string|true|none|
|»»» s|body|string|true|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|»» type|executeMetaTransaction::approve|
|»» type|permit|
|»» type|daiPermit|
|»»»» primaryType|Permit|
|»»»» primaryType|Permit|
|»»»» primaryType|MetaTransaction|
|»» type|settler_metatransaction|
|»» type|settler_intent|

> Example responses

> 200 Response

```json
{
  "tradeHash": "0xcb3285b35c024fca76037bea9ea4cb68645fed3bdd84030956577de2f1592aa9",
  "type": "settler_metatransaction",
  "zid": "0x111111111111111111111111"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="gasless::submit-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="gasless::submit-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» tradeHash|string|true|none|The hash for the trade according to [EIP-712](https://eips.ethereum.org/EIPS/eip-712)|
|» type|string|true|none|The transaction type determined by the trade route. This is currently just `settler_metatransaction` and could expand to more types in the future|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|type|settler_metatransaction|
|type|settler_intent|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|
|name|INSUFFICIENT_BALANCE_OR_ALLOWANCE|
|name|INVALID_SIGNATURE|
|name|INVALID_SIGNER|
|name|META_TRANSACTION_EXPIRY_TOO_SOON|
|name|META_TRANSACTION_INVALID|
|name|PENDING_TRADES_ALREADY_EXIST|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

## gasless::getStatus

<a id="opIdgasless::getStatus"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/gasless/status/{tradeHash}?chainId=8453 \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/gasless/status/{tradeHash}?chainId=8453 HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/gasless/status/{tradeHash}?chainId=8453',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/gasless/status/{tradeHash}',
  params: {
  'chainId' => 'integer'
}, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/gasless/status/{tradeHash}', params={
  'chainId': '8453'
}, headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/gasless/status/{tradeHash}', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/gasless/status/{tradeHash}?chainId=8453");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/gasless/status/{tradeHash}", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /gasless/status/{tradeHash}`

*getStatus*

Get the status of a gasless swap

<h3 id="gasless::getstatus-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|chainId|query|integer|true| [here](https://0x.org/docs/next/developer-resources/supported-chains) for the list of supported chains|
|tradeHash|path|string|true|The hash for the trade according to [EIP-712](https://eips.ethereum.org/EIPS/eip-712)|

> Example responses

> 200 Response

```json
{
  "status": "confirmed",
  "transactions": [
    {
      "hash": "0x36b42bc0ec313cfb9bf5122fbda933cbcce5f557bc3b7197b52223b05d7e596f",
      "timestamp": 1718662626073
    }
  ],
  "zid": "0x111111111111111111111111"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="gasless::getstatus-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|404 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="gasless::getstatus-responseschema">Response Schema</h3>

#### Enumerated Values

|Property|Value|
|---|---|
|status|pending|
|status|submitted|
|status|succeeded|
|status|confirmed|
|reason|transaction_simulation_failed|
|reason|order_expired|
|reason|last_look_declined|
|reason|transaction_reverted|
|reason|market_maker_sigature_error|
|reason|insufficient_allowance|
|reason|insufficient_balance|
|reason|internal_error|
|status|failed|

Status Code **400**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|
|»» details|[object]|true|none|The list of invalid inputs|
|»»» field|string|true|none|The input field name|
|»»» reason|string|true|none|The validation failure reason|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|

Status Code **404**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|META_TRANSACTION_STATUS_NOT_FOUND|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

## gasless::getGaslessApprovalTokens

<a id="opIdgasless::getGaslessApprovalTokens"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/gasless/gasless-approval-tokens?chainId=8453 \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/gasless/gasless-approval-tokens?chainId=8453 HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/gasless/gasless-approval-tokens?chainId=8453',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/gasless/gasless-approval-tokens',
  params: {
  'chainId' => 'integer'
}, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/gasless/gasless-approval-tokens', params={
  'chainId': '8453'
}, headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/gasless/gasless-approval-tokens', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/gasless/gasless-approval-tokens?chainId=8453");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/gasless/gasless-approval-tokens", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /gasless/gasless-approval-tokens`

*getGaslessApprovalTokens*

Get token addresses that support gasless approvals

<h3 id="gasless::getgaslessapprovaltokens-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|chainId|query|integer|true|Chain ID. See [here](https://0x.org/docs/developer-resources/supported-chains) for the list of supported chains|

> Example responses

> 200 Response

```json
{
  "tokens": [
    "0x111111111117dc0aa78b770fa6a738034120c302",
    "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9",
    "0xb98d4c97425d9908e66e53a6fdf673acca0be986",
    "0xed04915c23f00a313a544955524eb7dbd823143d",
    "0x6b0b3a982b4634ac68dd83a4dbf02311ce324181",
    "0xac51066d7bec65dc4589368da368b212745d63e8"
  ],
  "zid": "0x111111111111111111111111"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="gasless::getgaslessapprovaltokens-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="gasless::getgaslessapprovaltokens-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» tokens|[string]|true|none|The list of tokens that can be used for gasless approvals|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

Status Code **400**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|
|»» details|[object]|true|none|The list of invalid inputs|
|»»» field|string|true|none|The input field name|
|»»» reason|string|true|none|The validation failure reason|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

## gasless::chains

<a id="opIdgasless::chains"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/gasless/chains \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/gasless/chains HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/gasless/chains',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/gasless/chains',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/gasless/chains', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/gasless/chains', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/gasless/chains");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/gasless/chains", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /gasless/chains`

*getChains*

Get list of supported chains for gasless

<h3 id="gasless::chains-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|

> Example responses

> 200 Response

```json
[
  {
    "chainName": "Ethereum",
    "chainId": "1"
  },
  {
    "chainName": "Optimism",
    "chainId": "10"
  },
  {
    "chainName": "BSC",
    "chainId": "56"
  },
  {
    "chainName": "Polygon",
    "chainId": "137"
  },
  {
    "chainName": "Base",
    "chainId": "8453"
  },
  {
    "chainName": "Arbitrum",
    "chainId": "42161"
  },
  {
    "chainName": "Avalanche",
    "chainId": "43114"
  },
  {
    "chainName": "Scroll",
    "chainId": "534352"
  },
  {
    "chainName": "Mantle",
    "chainId": "5000"
  },
  {
    "chainName": "Blast",
    "chainId": "81457"
  },
  {
    "chainName": "Mode",
    "chainId": "34443"
  }
]
```

> 500 Response

```json
{
  "name": "INTERNAL_SERVER_ERROR",
  "message": "string",
  "data": {
    "zid": "string"
  }
}
```

<h3 id="gasless::chains-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="gasless::chains-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» chains|[object]|true|none|none|
|»» chainId|number|true|none|none|
|»» chainName|string|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

<h1 id="0x-api-sources">Sources</h1>

Sources API endpoints

## sources::getSources

<a id="opIdsources::getSources"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/sources?chainId=1 \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/sources?chainId=1 HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/sources?chainId=1',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/sources',
  params: {
  'chainId' => 'integer'
}, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/sources', params={
  'chainId': '1'
}, headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/sources', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/sources?chainId=1");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/sources", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /sources`

*getSources*

Get the list of supported sources

<h3 id="sources::getsources-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|chainId|query|integer|true|Chain ID. See [here](https://0x.org/docs/developer-resources/supported-chains) for the list of supported chains|

> Example responses

> 200 Response

```json
{
  "sources": [
    "0x_RFQ",
    "Ambient",
    "BalancerV1",
    "BalancerV2",
    "BancorV3",
    "Curve",
    "DodoV1",
    "DodoV2",
    "FraxswapV2",
    "Integral",
    "Lido",
    "MakerPsm",
    "Maverick",
    "Origin",
    "PancakeSwapV3",
    "RocketPool",
    "SolidlyV3",
    "SushiSwap",
    "Synapse",
    "UniswapV2",
    "UniswapV3"
  ],
  "zid": "0x111111111111111111111111"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="sources::getsources-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="sources::getsources-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» sources|[string]|true|none|The array of liquidity sources aggregated by 0x for the requested chain|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

Status Code **400**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|
|»» details|[object]|true|none|The list of invalid inputs|
|»»» field|string|true|none|The input field name|
|»»» reason|string|true|none|The validation failure reason|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

<h1 id="0x-api-trade-analytics">Trade Analytics</h1>

Trade Analytics API endpoints

## tradeAnalytics::swap

<a id="opIdtradeAnalytics::swap"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/trade-analytics/swap \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/trade-analytics/swap HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/trade-analytics/swap',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/trade-analytics/swap',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/trade-analytics/swap', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/trade-analytics/swap', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/trade-analytics/swap");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/trade-analytics/swap", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /trade-analytics/swap`

*getSwapTrades*

Get the list of completed swap trades. Returns a maximum of 200 trades per request. Visit [here](https://docs.0x.org/trade-analytics-api/introduction) for more details about how the API works.

<h3 id="tradeanalytics::swap-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|cursor|query|string|false|A pagination cursor used to fetch the next page of trades. It should be set to `null` for the initial request; otherwise, it should be the value of `nextCursor` that is returned from `getSwapTrades` or `getGaslessTrades` calls.|
|startTimestamp|query|integer|false|Unix timestamp in seconds, specifying the starting point of the time range filter. Only trades completed on or after this timestamp will be included in the response.|
|endTimestamp|query|integer|false|Unix timestamp in seconds, specifying the end point of the time range filter. Only trades completed on or before this timestamp will be included in the response.|

> Example responses

> 200 Response

```json
{
  "nextCursor": null,
  "trades": [
    {
      "appName": "Example app",
      "blockNumber": "123456",
      "buyToken": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
      "buyAmount": "0.0512",
      "chainId": 1,
      "fees": {
        "integratorFee": null,
        "zeroExFee": null
      },
      "gasUsed": "141111",
      "protocolVersion": "Settler",
      "sellToken": "0x4d1c297d39c5c1277964d0e3f8aqqqq493664530",
      "sellAmount": "123.111",
      "slippageBps": "1",
      "taker": "0x23f2ad8e04dfdc0000a3e80891e3ae43f322000a",
      "timestamp": 1777772227,
      "tokens": [
        {
          "address": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
          "symbol": "ETH"
        },
        {
          "address": "0xaaaaaaaaaaaaaa277964d0e3f8aa901493664530",
          "symbol": "TKN"
        }
      ],
      "transactionHash": "0x42bad789ddd64aaaaaaaaaaaceb795063f5623558f130e0f4d30ad399b041411",
      "volumeUsd": "139.73",
      "zid": "0x04baaaaaaa1f1af0304eb412",
      "service": "swap"
    }
  ],
  "zid": "0xaaaaaae1b3bf43f082d5012d"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="tradeanalytics::swap-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="tradeanalytics::swap-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» nextCursor|string¦null|true|none|The cursor to fetch the next page of trades. If not present, there are no more trades to fetch for given parameters.|
|» trades|[object]|true|none|none|
|»» appName|string|true|none|The name of the app that initiated the trade|
|»» blockNumber|string|true|none|The block number at which the trade was executed|
|»» buyToken|string|true|none|The contract address of the token received by the taker|
|»» buyAmount|string¦null|true|none|The settled amount on the `buyToken`, formatted by the token decimals|
|»» chainId|integer|true|none|The ID of the chain where the trade was executed|
|»» chainName|string|true|none|The name of the chain where the trade was executed|
|»» fees|object|true|none|The details about fees collected for the trade|
|»»» integratorFee|object¦null|true|none|The details about the fee collected by integrator|
|»»»» token|string¦null|true|none|The contract address of the token in which the integrator collected a fee|
|»»»» amount|string¦null|true|none|The amount of the integrator fee, formatted by the token decimals|
|»»»» amountUsd|string¦null|true|none|The amount of the integrator fee in USD.|
|»»» zeroExFee|object¦null|true|none|The details about the fee collected by 0x|
|»»»» token|string¦null|true|none|The contract address of the token in which 0x collected a fee|
|»»»» amount|string¦null|true|none|The amount of the 0x fee, formatted by the token decimals|
|»»»» amountUsd|string¦null|true|none|The amount of the 0x fee in USD.|
|»» gasUsed|string|true|none|The amount of gas used in the trade|
|»» protocolVersion|string|true|none|The version of the 0x protocol used to execute the trade|
|»» sellToken|string|true|none|The contract address of the token spent by the taker|
|»» sellAmount|string¦null|true|none|The amount of the `sellToken`, formatted by the token decimals|
|»» slippageBps|string¦null|true|none|The slippage of the `buyToken` in bps|
|»» taker|string|true|none|The wallet address of the taker​|
|»» timestamp|integer|true|none|The timestamp of the block containing the trade|
|»» tokens|[object]|true|none|Properties of the tokens involved in the trade|
|»»» address|string|true|none|The contract address of the token|
|»»» symbol|string¦null|true|none|The symbol of the token|
|»» transactionHash|string|true|none|The trade's transaction hash|
|»» volumeUsd|string¦null|true|none|The total volume of the trade in USD. This value is based on an estimate of the token price at the point of execution.|
|»» zid|string|true|none|The `zid` corresponding to the trade|
|»» service|string|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|protocolVersion|0xv4|
|protocolVersion|Settler|
|service|swap|

Status Code **400**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|
|»» details|[object]|true|none|The list of invalid inputs|
|»»» field|string|true|none|The input field name|
|»»» reason|string|true|none|The validation failure reason|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

## tradeAnalytics::gasless

<a id="opIdtradeAnalytics::gasless"></a>

> Code samples

```shell
# You can also use wget
curl -X GET https://api.0x.org/trade-analytics/gasless \
  -H 'Accept: application/json' \
  -H '0x-api-key: string' \
  -H '0x-version: v2'

```

```http
GET https://api.0x.org/trade-analytics/gasless HTTP/1.1
Host: api.0x.org
Accept: application/json
0x-api-key: string
0x-version: v2

```

```javascript

const headers = {
  'Accept':'application/json',
  '0x-api-key':'string',
  '0x-version':'v2'
};

fetch('https://api.0x.org/trade-analytics/gasless',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json',
  '0x-api-key' => 'string',
  '0x-version' => 'v2'
}

result = RestClient.get 'https://api.0x.org/trade-analytics/gasless',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json',
  '0x-api-key': 'string',
  '0x-version': 'v2'
}

r = requests.get('https://api.0x.org/trade-analytics/gasless', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
    '0x-api-key' => 'string',
    '0x-version' => 'v2',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','https://api.0x.org/trade-analytics/gasless', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.0x.org/trade-analytics/gasless");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
        "0x-api-key": []string{"string"},
        "0x-version": []string{"v2"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "https://api.0x.org/trade-analytics/gasless", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /trade-analytics/gasless`

*getGaslessTrades*

Get the list of completed gasless trades. Returns a maximum of 200 trades per request. Visit [here](https://docs.0x.org/trade-analytics-api/introduction) for more details about how the API works.

<h3 id="tradeanalytics::gasless-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|0x-api-key|header|string|true|Visit dashboard.0x.org to get your API Key|
|0x-version|header|string|true|API version|
|cursor|query|string|false|A pagination cursor used to fetch the next page of trades. It should be set to `null` for the initial request; otherwise, it should be the value of `nextCursor` that is returned from `getSwapTrades` or `getGaslessTrades` calls.|
|startTimestamp|query|integer|false|Unix timestamp in seconds, specifying the starting point of the time range filter. Only trades completed on or after this timestamp will be included in the response.|
|endTimestamp|query|integer|false|Unix timestamp in seconds, specifying the end point of the time range filter. Only trades completed on or before this timestamp will be included in the response.|

> Example responses

> 200 Response

```json
{
  "nextCursor": null,
  "trades": [
    {
      "appName": "Example app",
      "blockNumber": "123456",
      "buyToken": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
      "buyAmount": "0.0512",
      "chainId": 1,
      "fees": {
        "integratorFee": null,
        "zeroExFee": null
      },
      "gasUsed": "141111",
      "protocolVersion": "Settler",
      "sellToken": "0x4d1c297d39c5c1277964d0e3f8aqqqq493664530",
      "sellAmount": "123.111",
      "slippageBps": "1",
      "taker": "0x23f2ad8e04dfdc0000a3e80891e3ae43f322000a",
      "timestamp": 1777772227,
      "tokens": [
        {
          "address": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
          "symbol": "ETH"
        },
        {
          "address": "0xaaaaaaaaaaaaaa277964d0e3f8aa901493664530",
          "symbol": "TKN"
        }
      ],
      "transactionHash": "0x42bad789ddd64aaaaaaaaaaaceb795063f5623558f130e0f4d30ad399b041411",
      "volumeUsd": "139.73",
      "zid": "0x04baaaaaaa1f1af0304eb412",
      "service": "gasless"
    }
  ],
  "zid": "0xaaaaaae1b3bf43f082d5012d"
}
```

> 400 Response

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}
```

<h3 id="tradeanalytics::gasless-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|400 error response|Inline|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|500 error response|Inline|

<h3 id="tradeanalytics::gasless-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» nextCursor|string¦null|true|none|The cursor to fetch the next page of trades. If not present, there are no more trades to fetch for given parameters.|
|» trades|[object]|true|none|none|
|»» appName|string|true|none|The name of the app that initiated the trade|
|»» blockNumber|string|true|none|The block number at which the trade was executed|
|»» buyToken|string|true|none|The contract address of the token received by the taker|
|»» buyAmount|string¦null|true|none|The settled amount on the `buyToken`, formatted by the token decimals|
|»» chainId|integer|true|none|The ID of the chain where the trade was executed|
|»» chainName|string|true|none|The name of the chain where the trade was executed|
|»» fees|object|true|none|The details about fees collected for the trade|
|»»» integratorFee|object¦null|true|none|The details about the fee collected by integrator|
|»»»» token|string¦null|true|none|The contract address of the token in which the integrator collected a fee|
|»»»» amount|string¦null|true|none|The amount of the integrator fee, formatted by the token decimals|
|»»»» amountUsd|string¦null|true|none|The amount of the integrator fee in USD.|
|»»» zeroExFee|object¦null|true|none|The details about the fee collected by 0x|
|»»»» token|string¦null|true|none|The contract address of the token in which 0x collected a fee|
|»»»» amount|string¦null|true|none|The amount of the 0x fee, formatted by the token decimals|
|»»»» amountUsd|string¦null|true|none|The amount of the 0x fee in USD.|
|»» gasUsed|string|true|none|The amount of gas used in the trade|
|»» protocolVersion|string|true|none|The version of the 0x protocol used to execute the trade|
|»» sellToken|string|true|none|The contract address of the token spent by the taker|
|»» sellAmount|string¦null|true|none|The amount of the `sellToken`, formatted by the token decimals|
|»» slippageBps|string¦null|true|none|The slippage of the `buyToken` in bps|
|»» taker|string|true|none|The wallet address of the taker​|
|»» timestamp|integer|true|none|The timestamp of the block containing the trade|
|»» tokens|[object]|true|none|Properties of the tokens involved in the trade|
|»»» address|string|true|none|The contract address of the token|
|»»» symbol|string¦null|true|none|The symbol of the token|
|»» transactionHash|string|true|none|The trade's transaction hash|
|»» volumeUsd|string¦null|true|none|The total volume of the trade in USD. This value is based on an estimate of the token price at the point of execution.|
|»» zid|string|true|none|The `zid` corresponding to the trade|
|»» service|string|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|protocolVersion|0xv4|
|protocolVersion|Settler|
|service|gasless|

Status Code **400**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» name|string|true|none|none|
|» message|string|true|none|none|
|» data|object|true|none|none|
|»» zid|string|true|none|The unique ZeroEx identifier of the request|
|»» details|[object]|true|none|The list of invalid inputs|
|»»» field|string|true|none|The input field name|
|»»» reason|string|true|none|The validation failure reason|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|
|name|UNCATEGORIZED|

<aside class="success">
This operation does not require authentication
</aside>

# Schemas

<h2 id="tocS_BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE">BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE</h2>
<!-- backwards compatibility -->
<a id="schemabuy_token_not_authorized_for_trade"></a>
<a id="schema_BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE"></a>
<a id="tocSbuy_token_not_authorized_for_trade"></a>
<a id="tocsbuy_token_not_authorized_for_trade"></a>

```json
{
  "name": "BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE",
  "message": "string",
  "data": {
    "zid": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|BUY_TOKEN_NOT_AUTHORIZED_FOR_TRADE|

<h2 id="tocS_INPUT_INVALID">INPUT_INVALID</h2>
<!-- backwards compatibility -->
<a id="schemainput_invalid"></a>
<a id="schema_INPUT_INVALID"></a>
<a id="tocSinput_invalid"></a>
<a id="tocsinput_invalid"></a>

```json
{
  "name": "INPUT_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "details": [
      {
        "field": "string",
        "reason": "string"
      }
    ]
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|
|» details|[object]|true|none|The list of invalid inputs|
|»» field|string|true|none|The input field name|
|»» reason|string|true|none|The validation failure reason|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INPUT_INVALID|

<h2 id="tocS_INSUFFICIENT_BALANCE">INSUFFICIENT_BALANCE</h2>
<!-- backwards compatibility -->
<a id="schemainsufficient_balance"></a>
<a id="schema_INSUFFICIENT_BALANCE"></a>
<a id="tocSinsufficient_balance"></a>
<a id="tocsinsufficient_balance"></a>

```json
{
  "name": "INSUFFICIENT_BALANCE",
  "message": "string",
  "data": {
    "zid": "string",
    "taker": "string",
    "sellToken": "string",
    "sellAmount": "string",
    "balance": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|
|» taker|string|true|none|The taker of the transaction|
|» sellToken|string|true|none|The sell token|
|» sellAmount|any|true|none|The sell amount|

allOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|any|false|none|none|

and

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|string|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» balance|any|true|none|The current balance of the taker for the sell token|

allOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|any|false|none|none|

and

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INSUFFICIENT_BALANCE|

<h2 id="tocS_INSUFFICIENT_BALANCE_OR_ALLOWANCE">INSUFFICIENT_BALANCE_OR_ALLOWANCE</h2>
<!-- backwards compatibility -->
<a id="schemainsufficient_balance_or_allowance"></a>
<a id="schema_INSUFFICIENT_BALANCE_OR_ALLOWANCE"></a>
<a id="tocSinsufficient_balance_or_allowance"></a>
<a id="tocsinsufficient_balance_or_allowance"></a>

```json
{
  "name": "INSUFFICIENT_BALANCE_OR_ALLOWANCE",
  "message": "string",
  "data": {
    "zid": "string",
    "metaTransactionHash": "string",
    "taker": "string",
    "sellToken": "string",
    "sellAmount": "string",
    "minBalanceOrAllowance": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|
|» metaTransactionHash|string|true|none|The hash of the meta-transaction provided by the caller|
|» taker|string|true|none|The intended signer of the meta-transaction|
|» sellToken|string|true|none|The sell token|
|» sellAmount|any|true|none|The sell amount|

allOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|any|false|none|none|

and

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|string|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» minBalanceOrAllowance|any|true|none|The smaller value of the balance or the allowance of the taker|

allOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|any|false|none|none|

and

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INSUFFICIENT_BALANCE_OR_ALLOWANCE|

<h2 id="tocS_INTERNAL_SERVER_ERROR">INTERNAL_SERVER_ERROR</h2>
<!-- backwards compatibility -->
<a id="schemainternal_server_error"></a>
<a id="schema_INTERNAL_SERVER_ERROR"></a>
<a id="tocSinternal_server_error"></a>
<a id="tocsinternal_server_error"></a>

```json
{
  "name": "INTERNAL_SERVER_ERROR",
  "message": "string",
  "data": {
    "zid": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INTERNAL_SERVER_ERROR|

<h2 id="tocS_INVALID_SIGNATURE">INVALID_SIGNATURE</h2>
<!-- backwards compatibility -->
<a id="schemainvalid_signature"></a>
<a id="schema_INVALID_SIGNATURE"></a>
<a id="tocSinvalid_signature"></a>
<a id="tocsinvalid_signature"></a>

```json
{
  "name": "INVALID_SIGNATURE",
  "message": "string",
  "data": {
    "zid": "string",
    "metaTransactionHash": "string",
    "taker": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|
|» metaTransactionHash|string|true|none|The hash of the meta-transaction provided by the caller|
|» taker|string|true|none|The intended signer of the meta-transaction|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INVALID_SIGNATURE|

<h2 id="tocS_INVALID_SIGNER">INVALID_SIGNER</h2>
<!-- backwards compatibility -->
<a id="schemainvalid_signer"></a>
<a id="schema_INVALID_SIGNER"></a>
<a id="tocSinvalid_signer"></a>
<a id="tocsinvalid_signer"></a>

```json
{
  "name": "INVALID_SIGNER",
  "message": "string",
  "data": {
    "zid": "string",
    "metaTransactionHash": "string",
    "taker": "string",
    "signer": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|
|» metaTransactionHash|string|true|none|The hash of the meta-transaction provided by the caller|
|» taker|string|true|none|The intended signer of the meta-transaction|
|» signer|string|true|none|The signer of the meta-transaction|

#### Enumerated Values

|Property|Value|
|---|---|
|name|INVALID_SIGNER|

<h2 id="tocS_META_TRANSACTION_EXPIRY_TOO_SOON">META_TRANSACTION_EXPIRY_TOO_SOON</h2>
<!-- backwards compatibility -->
<a id="schemameta_transaction_expiry_too_soon"></a>
<a id="schema_META_TRANSACTION_EXPIRY_TOO_SOON"></a>
<a id="tocSmeta_transaction_expiry_too_soon"></a>
<a id="tocsmeta_transaction_expiry_too_soon"></a>

```json
{
  "name": "META_TRANSACTION_EXPIRY_TOO_SOON",
  "message": "string",
  "data": {
    "zid": "string",
    "metaTransactionHash": "string",
    "expiry": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|
|» metaTransactionHash|string|true|none|The hash of the meta-transaction provided by the caller|
|» expiry|any|true|none|The expiry of the meta-transaction provided by the caller in ms|

allOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|any|false|none|none|

and

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|name|META_TRANSACTION_EXPIRY_TOO_SOON|

<h2 id="tocS_META_TRANSACTION_INVALID">META_TRANSACTION_INVALID</h2>
<!-- backwards compatibility -->
<a id="schemameta_transaction_invalid"></a>
<a id="schema_META_TRANSACTION_INVALID"></a>
<a id="tocSmeta_transaction_invalid"></a>
<a id="tocsmeta_transaction_invalid"></a>

```json
{
  "name": "META_TRANSACTION_INVALID",
  "message": "string",
  "data": {
    "zid": "string",
    "metaTransactionHash": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|
|» metaTransactionHash|string|true|none|The hash of the meta-transaction provided by the caller|

#### Enumerated Values

|Property|Value|
|---|---|
|name|META_TRANSACTION_INVALID|

<h2 id="tocS_META_TRANSACTION_STATUS_NOT_FOUND">META_TRANSACTION_STATUS_NOT_FOUND</h2>
<!-- backwards compatibility -->
<a id="schemameta_transaction_status_not_found"></a>
<a id="schema_META_TRANSACTION_STATUS_NOT_FOUND"></a>
<a id="tocSmeta_transaction_status_not_found"></a>
<a id="tocsmeta_transaction_status_not_found"></a>

```json
{
  "name": "META_TRANSACTION_STATUS_NOT_FOUND",
  "message": "string",
  "data": {
    "zid": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|META_TRANSACTION_STATUS_NOT_FOUND|

<h2 id="tocS_PENDING_TRADES_ALREADY_EXIST">PENDING_TRADES_ALREADY_EXIST</h2>
<!-- backwards compatibility -->
<a id="schemapending_trades_already_exist"></a>
<a id="schema_PENDING_TRADES_ALREADY_EXIST"></a>
<a id="tocSpending_trades_already_exist"></a>
<a id="tocspending_trades_already_exist"></a>

```json
{
  "name": "PENDING_TRADES_ALREADY_EXIST",
  "message": "string",
  "data": {
    "zid": "string",
    "metaTransactionHash": "string",
    "pendingMetaTransactionHashes": [
      "string"
    ]
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|
|» metaTransactionHash|string|true|none|The hash of the meta-transaction provided by the caller|
|» pendingMetaTransactionHashes|[string]|true|none|The list of pending meta-transaction hashes for the same taker and sell token|

#### Enumerated Values

|Property|Value|
|---|---|
|name|PENDING_TRADES_ALREADY_EXIST|

<h2 id="tocS_SELL_AMOUNT_TOO_SMALL">SELL_AMOUNT_TOO_SMALL</h2>
<!-- backwards compatibility -->
<a id="schemasell_amount_too_small"></a>
<a id="schema_SELL_AMOUNT_TOO_SMALL"></a>
<a id="tocSsell_amount_too_small"></a>
<a id="tocssell_amount_too_small"></a>

```json
{
  "name": "SELL_AMOUNT_TOO_SMALL",
  "message": "string",
  "data": {
    "zid": "string",
    "minSellAmount": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|
|» minSellAmount|any|true|none|The minimum sell amount required for the trade to go through|

allOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|any|false|none|none|

and

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|»» *anonymous*|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|name|SELL_AMOUNT_TOO_SMALL|

<h2 id="tocS_SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE">SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE</h2>
<!-- backwards compatibility -->
<a id="schemasell_token_not_authorized_for_trade"></a>
<a id="schema_SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE"></a>
<a id="tocSsell_token_not_authorized_for_trade"></a>
<a id="tocssell_token_not_authorized_for_trade"></a>

```json
{
  "name": "SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE",
  "message": "string",
  "data": {
    "zid": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|SELL_TOKEN_NOT_AUTHORIZED_FOR_TRADE|

<h2 id="tocS_SWAP_VALIDATION_FAILED">SWAP_VALIDATION_FAILED</h2>
<!-- backwards compatibility -->
<a id="schemaswap_validation_failed"></a>
<a id="schema_SWAP_VALIDATION_FAILED"></a>
<a id="tocSswap_validation_failed"></a>
<a id="tocsswap_validation_failed"></a>

```json
{
  "name": "SWAP_VALIDATION_FAILED",
  "message": "string",
  "data": {
    "zid": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|SWAP_VALIDATION_FAILED|

<h2 id="tocS_TAKER_NOT_AUTHORIZED_FOR_TRADE">TAKER_NOT_AUTHORIZED_FOR_TRADE</h2>
<!-- backwards compatibility -->
<a id="schemataker_not_authorized_for_trade"></a>
<a id="schema_TAKER_NOT_AUTHORIZED_FOR_TRADE"></a>
<a id="tocStaker_not_authorized_for_trade"></a>
<a id="tocstaker_not_authorized_for_trade"></a>

```json
{
  "name": "TAKER_NOT_AUTHORIZED_FOR_TRADE",
  "message": "string",
  "data": {
    "zid": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|TAKER_NOT_AUTHORIZED_FOR_TRADE|

<h2 id="tocS_TOKEN_NOT_SUPPORTED">TOKEN_NOT_SUPPORTED</h2>
<!-- backwards compatibility -->
<a id="schematoken_not_supported"></a>
<a id="schema_TOKEN_NOT_SUPPORTED"></a>
<a id="tocStoken_not_supported"></a>
<a id="tocstoken_not_supported"></a>

```json
{
  "name": "TOKEN_NOT_SUPPORTED",
  "message": "string",
  "data": {
    "zid": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|TOKEN_NOT_SUPPORTED|

<h2 id="tocS_UNABLE_TO_CALCULATE_GAS_FEE">UNABLE_TO_CALCULATE_GAS_FEE</h2>
<!-- backwards compatibility -->
<a id="schemaunable_to_calculate_gas_fee"></a>
<a id="schema_UNABLE_TO_CALCULATE_GAS_FEE"></a>
<a id="tocSunable_to_calculate_gas_fee"></a>
<a id="tocsunable_to_calculate_gas_fee"></a>

```json
{
  "name": "UNABLE_TO_CALCULATE_GAS_FEE",
  "message": "string",
  "data": {
    "zid": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|UNABLE_TO_CALCULATE_GAS_FEE|

<h2 id="tocS_UNCATEGORIZED">UNCATEGORIZED</h2>
<!-- backwards compatibility -->
<a id="schemauncategorized"></a>
<a id="schema_UNCATEGORIZED"></a>
<a id="tocSuncategorized"></a>
<a id="tocsuncategorized"></a>

```json
{
  "name": "UNCATEGORIZED",
  "message": "string",
  "data": {
    "zid": "string"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|message|string|true|none|none|
|data|object|true|none|none|
|» zid|string|true|none|The unique ZeroEx identifier of the request|

#### Enumerated Values

|Property|Value|
|---|---|
|name|UNCATEGORIZED|

