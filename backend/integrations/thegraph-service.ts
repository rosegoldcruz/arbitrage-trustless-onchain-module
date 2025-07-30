/**
 * 📊 THE GRAPH PROTOCOL SERVICE
 * Production-grade subgraph queries for Base Sepolia
 * API Key: f187a007e656031f58294838b7219a0f
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { z } from 'zod';

// Environment configuration
const THE_GRAPH_API_KEY = process.env.THE_GRAPH_API_KEY || 'f187a007e656031f58294838b7219a0f';
const THE_GRAPH_STUDIO_URL = process.env.THE_GRAPH_STUDIO_URL || 'https://api.studio.thegraph.com/query/atom';

// Base Sepolia subgraph endpoints
export const SUBGRAPH_ENDPOINTS = {
  BALANCER_V3: `${THE_GRAPH_STUDIO_URL}/balancer-v3-base-sepolia/${THE_GRAPH_API_KEY}`,
  UNISWAP_V3: `${THE_GRAPH_STUDIO_URL}/uniswap-v3-base-sepolia/${THE_GRAPH_API_KEY}`,
  AAVE_V3: `${THE_GRAPH_STUDIO_URL}/aave-v3-base-sepolia/${THE_GRAPH_API_KEY}`,
  COMPOUND_V3: `${THE_GRAPH_STUDIO_URL}/compound-v3-base-sepolia/${THE_GRAPH_API_KEY}`
};

// Zod schemas for type safety
const TokenSchema = z.object({
  id: z.string(),
  symbol: z.string(),
  name: z.string(),
  decimals: z.number(),
  totalSupply: z.string(),
  volume: z.string().optional(),
  volumeUSD: z.string().optional(),
  priceUSD: z.string().optional()
});

const PoolSchema = z.object({
  id: z.string(),
  token0: TokenSchema,
  token1: TokenSchema,
  liquidity: z.string(),
  sqrtPrice: z.string(),
  tick: z.number().optional(),
  feeGrowthGlobal0X128: z.string().optional(),
  feeGrowthGlobal1X128: z.string().optional(),
  volumeUSD: z.string(),
  feesUSD: z.string().optional(),
  txCount: z.string(),
  totalValueLockedUSD: z.string()
});

const SwapSchema = z.object({
  id: z.string(),
  transaction: z.object({
    id: z.string(),
    blockNumber: z.string(),
    timestamp: z.string()
  }),
  pool: z.object({
    id: z.string(),
    token0: z.object({
      symbol: z.string()
    }),
    token1: z.object({
      symbol: z.string()
    })
  }),
  sender: z.string(),
  recipient: z.string(),
  amount0: z.string(),
  amount1: z.string(),
  amountUSD: z.string().optional(),
  sqrtPriceX96: z.string(),
  tick: z.number().optional()
});

export type Token = z.infer<typeof TokenSchema>;
export type Pool = z.infer<typeof PoolSchema>;
export type Swap = z.infer<typeof SwapSchema>;

// GraphQL query templates
const QUERIES = {
  TOP_POOLS: `
    query GetTopPools($first: Int!, $orderBy: String!, $orderDirection: String!) {
      pools(
        first: $first
        orderBy: $orderBy
        orderDirection: $orderDirection
        where: { totalValueLockedUSD_gt: "1000" }
      ) {
        id
        token0 {
          id
          symbol
          name
          decimals
        }
        token1 {
          id
          symbol
          name
          decimals
        }
        liquidity
        sqrtPrice
        tick
        volumeUSD
        feesUSD
        txCount
        totalValueLockedUSD
      }
    }
  `,

  RECENT_SWAPS: `
    query GetRecentSwaps($first: Int!, $pool: String) {
      swaps(
        first: $first
        orderBy: timestamp
        orderDirection: desc
        where: { pool: $pool }
      ) {
        id
        transaction {
          id
          blockNumber
          timestamp
        }
        pool {
          id
          token0 {
            symbol
          }
          token1 {
            symbol
          }
        }
        sender
        recipient
        amount0
        amount1
        amountUSD
        sqrtPriceX96
        tick
      }
    }
  `,

  TOKEN_PRICES: `
    query GetTokenPrices($tokens: [String!]!) {
      tokens(where: { id_in: $tokens }) {
        id
        symbol
        name
        decimals
        totalSupply
        volume
        volumeUSD
        priceUSD
      }
    }
  `,

  POOL_HOURLY_DATA: `
    query GetPoolHourlyData($pool: String!, $first: Int!) {
      poolHourDatas(
        first: $first
        orderBy: periodStartUnix
        orderDirection: desc
        where: { pool: $pool }
      ) {
        id
        periodStartUnix
        liquidity
        sqrtPrice
        token0Price
        token1Price
        volumeToken0
        volumeToken1
        volumeUSD
        feesUSD
        txCount
        open
        high
        low
        close
      }
    }
  `
};

export class TheGraphService {
  private client: AxiosInstance;
  private rateLimitDelay: number = 100; // ms between requests

  constructor() {
    this.client = axios.create({
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'ATOM-Arbitrage-Engine/1.0'
      }
    });

    // Add request interceptor for rate limiting
    this.client.interceptors.request.use(async (config) => {
      await new Promise(resolve => setTimeout(resolve, this.rateLimitDelay));
      return config;
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('The Graph API Error:', {
          url: error.config?.url,
          status: error.response?.status,
          data: error.response?.data
        });
        throw error;
      }
    );
  }

  /**
   * Execute GraphQL query against specified subgraph
   */
  private async executeQuery<T>(
    endpoint: string,
    query: string,
    variables: Record<string, any> = {}
  ): Promise<T> {
    try {
      const response: AxiosResponse = await this.client.post(endpoint, {
        query,
        variables
      });

      if (response.data.errors) {
        throw new Error(`GraphQL errors: ${JSON.stringify(response.data.errors)}`);
      }

      return response.data.data;
    } catch (error) {
      console.error('GraphQL query failed:', error);
      throw error;
    }
  }

  /**
   * Get top pools by TVL from Uniswap V3 subgraph
   */
  async getTopPools(
    first: number = 20,
    orderBy: string = 'totalValueLockedUSD',
    orderDirection: string = 'desc'
  ): Promise<Pool[]> {
    const data = await this.executeQuery<{ pools: any[] }>(
      SUBGRAPH_ENDPOINTS.UNISWAP_V3,
      QUERIES.TOP_POOLS,
      { first, orderBy, orderDirection }
    );

    return data.pools.map(pool => PoolSchema.parse(pool));
  }

  /**
   * Get recent swaps for a specific pool
   */
  async getRecentSwaps(poolId: string, first: number = 100): Promise<Swap[]> {
    const data = await this.executeQuery<{ swaps: any[] }>(
      SUBGRAPH_ENDPOINTS.UNISWAP_V3,
      QUERIES.RECENT_SWAPS,
      { first, pool: poolId }
    );

    return data.swaps.map(swap => SwapSchema.parse(swap));
  }

  /**
   * Get token prices for specified token addresses
   */
  async getTokenPrices(tokenAddresses: string[]): Promise<Token[]> {
    const data = await this.executeQuery<{ tokens: any[] }>(
      SUBGRAPH_ENDPOINTS.UNISWAP_V3,
      QUERIES.TOKEN_PRICES,
      { tokens: tokenAddresses.map(addr => addr.toLowerCase()) }
    );

    return data.tokens.map(token => TokenSchema.parse(token));
  }

  /**
   * Get hourly data for a specific pool
   */
  async getPoolHourlyData(poolId: string, hours: number = 24): Promise<any[]> {
    const data = await this.executeQuery<{ poolHourDatas: any[] }>(
      SUBGRAPH_ENDPOINTS.UNISWAP_V3,
      QUERIES.POOL_HOURLY_DATA,
      { pool: poolId, first: hours }
    );

    return data.poolHourDatas;
  }

  /**
   * Get arbitrage opportunities by comparing prices across pools
   */
  async findArbitrageOpportunities(
    minSpreadBps: number = 23,
    minTvl: number = 10000
  ): Promise<any[]> {
    try {
      // Get top pools
      const pools = await this.getTopPools(50);
      
      // Filter pools by TVL
      const eligiblePools = pools.filter(
        pool => parseFloat(pool.totalValueLockedUSD) >= minTvl
      );

      // Group pools by token pairs
      const tokenPairGroups = new Map<string, Pool[]>();
      
      for (const pool of eligiblePools) {
        const pairKey = [pool.token0.symbol, pool.token1.symbol].sort().join('-');
        if (!tokenPairGroups.has(pairKey)) {
          tokenPairGroups.set(pairKey, []);
        }
        tokenPairGroups.get(pairKey)!.push(pool);
      }

      // Find arbitrage opportunities
      const opportunities = [];
      
      for (const [pairKey, poolsForPair] of tokenPairGroups) {
        if (poolsForPair.length < 2) continue;

        // Calculate price differences between pools
        for (let i = 0; i < poolsForPair.length; i++) {
          for (let j = i + 1; j < poolsForPair.length; j++) {
            const pool1 = poolsForPair[i];
            const pool2 = poolsForPair[j];

            // Calculate price from sqrtPrice
            const price1 = this.calculatePriceFromSqrtPrice(pool1.sqrtPrice);
            const price2 = this.calculatePriceFromSqrtPrice(pool2.sqrtPrice);

            const priceDiff = Math.abs(price1 - price2);
            const avgPrice = (price1 + price2) / 2;
            const spreadBps = (priceDiff / avgPrice) * 10000;

            if (spreadBps >= minSpreadBps) {
              opportunities.push({
                id: `${pool1.id}-${pool2.id}`,
                tokenPair: pairKey,
                pool1: {
                  id: pool1.id,
                  price: price1,
                  tvl: parseFloat(pool1.totalValueLockedUSD)
                },
                pool2: {
                  id: pool2.id,
                  price: price2,
                  tvl: parseFloat(pool2.totalValueLockedUSD)
                },
                spreadBps: Math.round(spreadBps),
                estimatedProfitUsd: this.estimateProfit(priceDiff, avgPrice),
                timestamp: Date.now()
              });
            }
          }
        }
      }

      return opportunities.sort((a, b) => b.spreadBps - a.spreadBps);
    } catch (error) {
      console.error('Error finding arbitrage opportunities:', error);
      return [];
    }
  }

  /**
   * Calculate price from Uniswap V3 sqrtPriceX96
   */
  private calculatePriceFromSqrtPrice(sqrtPriceX96: string): number {
    const sqrtPrice = parseFloat(sqrtPriceX96);
    const Q96 = Math.pow(2, 96);
    const price = Math.pow(sqrtPrice / Q96, 2);
    return price;
  }

  /**
   * Estimate profit from price difference
   */
  private estimateProfit(priceDiff: number, avgPrice: number): number {
    // Simple estimation - in reality would need to account for gas, slippage, etc.
    const tradeAmount = 1000; // $1000 trade
    const profitRatio = priceDiff / avgPrice;
    return tradeAmount * profitRatio * 0.8; // 80% efficiency factor
  }

  /**
   * Health check for The Graph service
   */
  async healthCheck(): Promise<{ status: string; latency: number }> {
    const startTime = Date.now();
    
    try {
      await this.getTopPools(1);
      const latency = Date.now() - startTime;
      
      return {
        status: 'healthy',
        latency
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        latency: Date.now() - startTime
      };
    }
  }
}

// Export singleton instance
export const theGraphService = new TheGraphService();
