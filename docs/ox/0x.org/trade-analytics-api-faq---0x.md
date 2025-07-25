# Trade Analytics API FAQ | 0x

Trade Analytics API FAQ | 0x




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

  + [Introduction](/docs/trade-analytics-api/introduction)
  + [API Reference](https://0x.org/docs/api#tag/Trade-Analytics)
  + [FAQ](/docs/trade-analytics-api/trade-faq)
* [AI Tools](/docs/category/ai-tools)
* [Libraries](/docs/category/libraries)
* [Developer Resources](/docs/category/developer-resources)
* [Example Projects](https://github.com/0xProject/0x-examples)
* [Upgrading](/docs/upgrading)
* [Liquidity Providers](/docs/category/liquidity-providers)
* [Need Help?](/docs/category/need-help)

* [Trade Analytics API](/docs/category/trade-analytics-api)
* FAQ

# Trade Analytics API FAQ

What is the 0x Trade Analytics API?

The Trade Analytics API gives integrators easy access to the history of trades initiated through 0x APIs and settled on 0x Smart Contracts. This API offers comprehensive transaction records, providing useful insights into user trading behavior.

Whose data is returned?

The Trade Analytics API will only return data for the app associated with the API key that makes the request. While all trading data is publicly available onchain, the Trade Analytics API provides a streamlined, well formatted data for the specific app making the request.

What is data finality in the context of the Trade Analytics API?

The data accessed through the API is deemed final 48 hours after a trade is completed. This delay allows time for the data pipeline to capture all relevant information, including fees from proxy contracts and updated USD prices from Coingecko.

To ensure that your trading data is up to date, we recommend that you fetch and update data from the preceding 2 days in addition to the current day.

How quickly will a new trade show up in the Trade Analytics API?

Data is updated roughly every 15 minutes. While generally reliable, data from these updates can sometimes be missing or incomplete, especially if they have a dependency on external sources such as token USD price providers. Each trade data is considered final 48 hours after it’s mined onchain – this enables us to address any gaps from earlier updates, ensuring data accuracy.

We don’t recommend using this API for use cases that require real time updates. If you’re interested in such data, please add a feature request to our [Canny Board](https://0x.canny.io/request-features).

Can I detect whether a transaction originated from the 0x API by parsing transaction receipts?

It's a common question — and the short answer is: **not directly via onchain data alone.**

While all 0x API trades are settled through the 0x Settler smart contract, these transactions don’t include a unique tag or flag that explicitly ties them to the API.

That said, there are a few ways to approach attribution, depending on what you're trying to track:

**🔍 If you're trying to track your own app's activity**

* The **[0x Trade Analytics API](/docs/trade-analytics-api/introduction)** is the best place to start. It allows you to query detailed trade data associated with your API key.
* Enable onchain tagging. In your [0x Dashboard](https://dashboard.0x.org/), go to your app’s **Settings** and toggle on **“Enable onchain tagging.”** This makes it easier to filter and trace your transactions onchain later.

**🌍 If you're trying to detect any and all transactions routed via the 0x API**

* You can **monitor the 0x Settler contract** for activity, but this includes all transactions — not just those initiated via the 0x API.
* Currently, there is **no canonical event** that maps directly to “this came from the Swap API,” but we’re exploring ways to make API attribution more accessible in the future.
* If you're interested in **aggregated Swap API usage data**, we may be able to share insights or internal tools depending on your use case. [Reach out to us](/docs/introduction/community#contact-support) — we’d love to hear more about what you're trying to build.

We understand attribution is an important use case, whether you're tracking your own usage or seeking broader ecosystem insights. Don’t hesitate to [contact us](/docs/trade-analytics-api/introduction/community#contact-support) to discuss how we can best support you.

[Previous

Introduction](/docs/trade-analytics-api/introduction)[Next

AI Tools](/docs/category/ai-tools)

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
[https://0x.org/docs/trade-analytics-api/trade-faq#docusaurus_skipToContent_fallback](https://0x.org/docs/trade-analytics-api/trade-faq#docusaurus_skipToContent_fallback)
