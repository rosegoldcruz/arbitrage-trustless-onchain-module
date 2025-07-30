/**
 * 🔄 0x API INTEGRATION SERVICE
 * Production-grade REST client for live 0x trade routing and execution
 * NO MOCK DATA - LIVE PRODUCTION FEEDS ONLY
 */

import axios, { AxiosResponse } from 'axios';
import { logger } from '../core/logger';

// 0x API Endpoints
const ZRX_API_BASE_URL = 'https://api.0x.org';
const ZRX_GASLESS_API_URL = 'https://gasless.api.0x.org';

// Supported chains for 0x - FOCUSED ON BASE SEPOLIA TESTNET
export enum ZrxChain {
  BASE = 8453,           // Base Mainnet
  BASE_SEPOLIA = 84532,  // Base Sepolia Testnet - PRIMARY TARGET
  ETHEREUM = 1,
  POLYGON = 137,
  BSC = 56,
  AVALANCHE = 43114,
  FANTOM = 250,
  CELO = 42220,
  OPTIMISM = 10,
  ARBITRUM = 42161
}

// Trade types
export enum TradeType {
  BUY = 'buy',
  SELL = 'sell'
}

// TypeScript interfaces for 0x API responses
export interface ZrxQuote {
  chainId: number;
  price: string;
  guaranteedPrice: string;
  estimatedPriceImpact: string;
  to: string;
  data: string;
  value: string;
  gas: string;
  estimatedGas: string;
  gasPrice: string;
  protocolFee: string;
  minimumProtocolFee: string;
  buyTokenAddress: string;
  sellTokenAddress: string;
  buyAmount: string;
  sellAmount: string;
  sources: Array<{
    name: string;
    proportion: string;
  }>;
  orders: Array<{
    makerToken: string;
    takerToken: string;
    makerAmount: string;
    takerAmount: string;
    fillData: {
      tokenAddressPath: string[];
      router: string;
    };
    source: string;
    sourcePathId: string;
    type: number;
  }>;
  allowanceTarget: string;
  decodedUniqueId: string;
  sellTokenToEthRate: string;
  buyTokenToEthRate: string;
  expectedSlippage?: string;
}

export interface ZrxPrice {
  chainId: number;
  price: string;
  estimatedPriceImpact: string;
  value: string;
  gasPrice: string;
  gas: string;
  estimatedGas: string;
  protocolFee: string;
  minimumProtocolFee: string;
  buyTokenAddress: string;
  sellTokenAddress: string;
  buyAmount: string;
  sellAmount: string;
  sources: Array<{
    name: string;
    proportion: string;
  }>;
  allowanceTarget: string;
  sellTokenToEthRate: string;
  buyTokenToEthRate: string;
  expectedSlippage?: string;
}

export interface ZrxSwapParams {
  chainId: ZrxChain;
  sellToken: string;
  buyToken: string;
  sellAmount?: string;
  buyAmount?: string;
  takerAddress?: string;
  slippagePercentage?: number;
  gasPrice?: string;
  feeRecipient?: string;
  buyTokenPercentageFee?: number;
  affiliateAddress?: string;
  skipValidation?: boolean;
  intentOnFilling?: boolean;
}

export interface ZrxTokenInfo {
  chainId: number;
  address: string;
  name: string;
  symbol: string;
  decimals: number;
  logoURI?: string;
}

export interface ZrxLiquiditySource {
  name: string;
  proportion: string;
  intermediateToken?: string;
  hops?: Array<{
    source: string;
    proportion: string;
  }>;
}

/**
 * 🔄 0x SERVICE CLASS
 * Enterprise-grade service for all 0x API interactions
 */
export class ZrxService {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly gaslessUrl: string;
  private readonly timeout: number;

  constructor() {
    this.apiKey = process.env.THEATOM_API_KEY || '';
    this.baseUrl = ZRX_API_BASE_URL;
    this.gaslessUrl = ZRX_GASLESS_API_URL;
    this.timeout = 30000; // 30 second timeout

    if (!this.apiKey) {
      logger.warn('0x API key not found in environment variables');
    }
  }

  /**
   * Execute API request with error handling and logging
   */
  private async executeRequest<T>(
    endpoint: string,
    params: Record<string, any> = {},
    useGasless: boolean = false
  ): Promise<T> {
    try {
      const baseUrl = useGasless ? this.gaslessUrl : this.baseUrl;
      const url = `${baseUrl}${endpoint}`;

      const headers: Record<string, string> = {
        'User-Agent': 'ATOM-Arbitrage-Engine/1.0'
      };

      if (this.apiKey) {
        headers['0x-api-key'] = this.apiKey;
      }

      const response: AxiosResponse = await axios.get(url, {
        params,
        headers,
        timeout: this.timeout
      });

      logger.info('0x API request successful', {
        endpoint,
        status: response.status,
        dataSize: JSON.stringify(response.data).length,
        timestamp: new Date().toISOString()
      });

      return response.data;
    } catch (error) {
      logger.error('0x API request failed:', {
        endpoint,
        error: error.message,
        response: error.response?.data
      });
      throw new Error(`0x API error: ${error.message}`);
    }
  }

  /**
   * Get price quote for a token swap
   */
  async getPrice(params: ZrxSwapParams): Promise<ZrxPrice> {
    const endpoint = `/swap/v1/price`;
    
    const queryParams = {
      chainId: params.chainId,
      sellToken: params.sellToken,
      buyToken: params.buyToken,
      ...(params.sellAmount && { sellAmount: params.sellAmount }),
      ...(params.buyAmount && { buyAmount: params.buyAmount }),
      ...(params.slippagePercentage && { slippagePercentage: params.slippagePercentage }),
      ...(params.gasPrice && { gasPrice: params.gasPrice }),
      ...(params.takerAddress && { takerAddress: params.takerAddress })
    };

    return this.executeRequest<ZrxPrice>(endpoint, queryParams);
  }

  /**
   * Get executable quote for a token swap
   */
  async getQuote(params: ZrxSwapParams): Promise<ZrxQuote> {
    const endpoint = `/swap/v1/quote`;
    
    const queryParams = {
      chainId: params.chainId,
      sellToken: params.sellToken,
      buyToken: params.buyToken,
      ...(params.sellAmount && { sellAmount: params.sellAmount }),
      ...(params.buyAmount && { buyAmount: params.buyAmount }),
      ...(params.takerAddress && { takerAddress: params.takerAddress }),
      ...(params.slippagePercentage && { slippagePercentage: params.slippagePercentage }),
      ...(params.gasPrice && { gasPrice: params.gasPrice }),
      ...(params.feeRecipient && { feeRecipient: params.feeRecipient }),
      ...(params.buyTokenPercentageFee && { buyTokenPercentageFee: params.buyTokenPercentageFee }),
      ...(params.affiliateAddress && { affiliateAddress: params.affiliateAddress }),
      ...(params.skipValidation !== undefined && { skipValidation: params.skipValidation }),
      ...(params.intentOnFilling !== undefined && { intentOnFilling: params.intentOnFilling })
    };

    return this.executeRequest<ZrxQuote>(endpoint, queryParams);
  }

  /**
   * Get supported tokens for a specific chain
   */
  async getTokens(chainId: ZrxChain): Promise<ZrxTokenInfo[]> {
    const endpoint = `/swap/v1/tokens`;
    
    const queryParams = {
      chainId
    };

    const response = await this.executeRequest<{ records: ZrxTokenInfo[] }>(endpoint, queryParams);
    return response.records;
  }

  /**
   * Get liquidity sources for a specific chain
   */
  async getLiquiditySources(chainId: ZrxChain): Promise<string[]> {
    const endpoint = `/swap/v1/sources`;
    
    const queryParams = {
      chainId
    };

    const response = await this.executeRequest<{ records: Array<{ name: string }> }>(endpoint, queryParams);
    return response.records.map(source => source.name);
  }

  /**
   * Get gasless quote (if supported)
   */
  async getGaslessQuote(params: ZrxSwapParams): Promise<ZrxQuote> {
    const endpoint = `/swap/permit2/quote`;
    
    const queryParams = {
      chainId: params.chainId,
      sellToken: params.sellToken,
      buyToken: params.buyToken,
      ...(params.sellAmount && { sellAmount: params.sellAmount }),
      ...(params.buyAmount && { buyAmount: params.buyAmount }),
      ...(params.takerAddress && { takerAddress: params.takerAddress }),
      ...(params.slippagePercentage && { slippagePercentage: params.slippagePercentage })
    };

    return this.executeRequest<ZrxQuote>(endpoint, queryParams, true);
  }

  /**
   * Compare prices across multiple DEXs for arbitrage opportunities
   */
  async findArbitrageOpportunities(
    tokenA: string,
    tokenB: string,
    amount: string,
    chainId: ZrxChain = ZrxChain.ETHEREUM
  ): Promise<{
    buyPrice: ZrxPrice;
    sellPrice: ZrxPrice;
    spread: number;
    profitUsd: number;
  }> {
    try {
      // Get buy price (tokenA -> tokenB)
      const buyPrice = await this.getPrice({
        chainId,
        sellToken: tokenA,
        buyToken: tokenB,
        sellAmount: amount
      });

      // Get sell price (tokenB -> tokenA)
      const sellPrice = await this.getPrice({
        chainId,
        sellToken: tokenB,
        buyToken: tokenA,
        sellAmount: buyPrice.buyAmount
      });

      // Calculate spread and profit
      const buyPriceNum = parseFloat(buyPrice.price);
      const sellPriceNum = parseFloat(sellPrice.price);
      const spread = ((sellPriceNum - buyPriceNum) / buyPriceNum) * 100;
      
      // Estimate profit in USD (simplified calculation)
      const amountUsd = parseFloat(amount) * parseFloat(buyPrice.sellTokenToEthRate);
      const profitUsd = amountUsd * (spread / 100);

      return {
        buyPrice,
        sellPrice,
        spread,
        profitUsd
      };
    } catch (error) {
      logger.error('Failed to find arbitrage opportunities:', error);
      throw error;
    }
  }

  /**
   * Get real-time market data for dashboard
   */
  async getMarketData(
    tokens: string[],
    chainId: ZrxChain = ZrxChain.ETHEREUM
  ): Promise<Array<{
    token: string;
    priceUsd: number;
    volume24h?: number;
    priceChange24h?: number;
  }>> {
    const marketData = [];

    for (const token of tokens) {
      try {
        // Get price against USDC for USD value
        const usdcAddress = chainId === ZrxChain.ETHEREUM 
          ? '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' 
          : '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'; // Polygon USDC

        const price = await this.getPrice({
          chainId,
          sellToken: token,
          buyToken: usdcAddress,
          sellAmount: '1000000000000000000' // 1 token (18 decimals)
        });

        marketData.push({
          token,
          priceUsd: parseFloat(price.price),
          // Note: 0x API doesn't provide volume/change data directly
          // These would need to be fetched from other sources like CoinGecko
        });
      } catch (error) {
        logger.warn(`Failed to get market data for token ${token}:`, error.message);
      }
    }

    return marketData;
  }
}

// Export singleton instance
export const zrxService = new ZrxService();
