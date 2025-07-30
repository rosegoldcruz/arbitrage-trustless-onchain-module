/**
 * 🏊‍♂️ BALANCER V3 API INTEGRATION SERVICE
 * Production-grade GraphQL client for live Balancer data
 * NO MOCK DATA - LIVE PRODUCTION FEEDS ONLY
 */

import axios, { AxiosResponse } from 'axios';
import { logger } from '../core/logger';

// Balancer V3 GraphQL Endpoint
const BALANCER_API_URL = 'https://api-v3.balancer.fi/graphql';

// Chain enum mapping - FOCUSED ON BASE SEPOLIA TESTNET
export enum BalancerChain {
  BASE = 'BASE',
  BASE_SEPOLIA = 'BASE_SEPOLIA',
  MAINNET = 'MAINNET',
  ARBITRUM = 'ARBITRUM',
  AVALANCHE = 'AVALANCHE',
  POLYGON = 'POLYGON'
}

// Event types
export enum PoolEventType {
  ADD = 'ADD',
  REMOVE = 'REMOVE',
  SWAP = 'SWAP'
}

// Swap types for SOR
export enum SwapType {
  EXACT_IN = 'EXACT_IN',
  EXACT_OUT = 'EXACT_OUT'
}

// TypeScript interfaces for type safety
export interface BalancerPool {
  id: string;
  address: string;
  name: string;
  chain: BalancerChain;
  type: string;
  version: number;
  dynamicData: {
    totalLiquidity: string;
    aprItems: Array<{
      title: string;
      type: string;
      apr: number;
    }>;
  };
  allTokens: Array<{
    address: string;
    name: string;
    symbol: string;
  }>;
  poolTokens: Array<{
    address: string;
    symbol: string;
    balance: string;
    hasNestedPool: boolean;
  }>;
}

export interface UserPoolBalance {
  address: string;
  userBalance: {
    stakedBalances: Array<{
      balance: string;
      balanceUsd: string;
      stakingType: string;
    }>;
    walletBalance: string;
    walletBalanceUsd: string;
    totalBalance: string;
    totalBalanceUsd: string;
  };
}

export interface PoolEvent {
  type: PoolEventType;
  valueUsd: string;
  timestamp: number;
  poolId: string;
  tokens?: Array<{
    address: string;
    amount: string;
    valueUsd: string;
  }>;
  fee?: {
    address: string;
    amount: string;
    valueUsd: string;
  };
}

export interface SwapPath {
  swapAmountRaw: string;
  returnAmountRaw: string;
  priceImpact: {
    priceImpact: string;
    error?: string;
  };
  routes: Array<{
    hops: Array<{
      poolId: string;
      tokenIn: string;
      tokenOut: string;
    }>;
  }>;
}

/**
 * 🏊‍♂️ BALANCER SERVICE CLASS
 * Enterprise-grade service for all Balancer V3 API interactions
 */
export class BalancerService {
  private readonly apiUrl: string;
  private readonly timeout: number;

  constructor() {
    this.apiUrl = BALANCER_API_URL;
    this.timeout = 30000; // 30 second timeout
  }

  /**
   * Execute GraphQL query with error handling and logging
   */
  private async executeQuery<T>(query: string, variables?: any): Promise<T> {
    try {
      const response: AxiosResponse = await axios.post(
        this.apiUrl,
        {
          query,
          variables
        },
        {
          timeout: this.timeout,
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'ATOM-Arbitrage-Engine/1.0'
          }
        }
      );

      if (response.data.errors) {
        logger.error('Balancer GraphQL errors:', response.data.errors);
        throw new Error(`GraphQL errors: ${JSON.stringify(response.data.errors)}`);
      }

      logger.info('Balancer API query successful', {
        dataSize: JSON.stringify(response.data.data).length,
        timestamp: new Date().toISOString()
      });

      return response.data.data;
    } catch (error) {
      logger.error('Balancer API query failed:', error);
      throw new Error(`Balancer API error: ${error.message}`);
    }
  }

  /**
   * 1. Get Pool Balances for a User
   */
  async getUserPoolBalances(
    userAddress: string,
    chains: BalancerChain[] = [BalancerChain.MAINNET]
  ): Promise<UserPoolBalance[]> {
    const query = `
      query GetUserPoolBalances($userAddress: String!, $chains: [GqlChain!]!) {
        poolGetPools(where: {chainIn: $chains, userAddress: $userAddress}) {
          address
          userBalance {
            stakedBalances {
              balance
              balanceUsd
              stakingType
            }
            walletBalance
            walletBalanceUsd
            totalBalance
            totalBalanceUsd
          }
        }
      }
    `;

    const variables = {
      userAddress,
      chains
    };

    const result = await this.executeQuery<{ poolGetPools: UserPoolBalance[] }>(query, variables);
    return result.poolGetPools;
  }

  /**
   * 2. Get Add/Remove Events for a User
   */
  async getUserPoolEvents(
    userAddress: string,
    poolIds: string[],
    chains: BalancerChain[] = [BalancerChain.MAINNET],
    eventTypes: PoolEventType[] = [PoolEventType.ADD, PoolEventType.REMOVE],
    first: number = 1000
  ): Promise<PoolEvent[]> {
    const query = `
      query GetUserPoolEvents(
        $userAddress: String!,
        $poolIds: [String!]!,
        $chains: [GqlChain!]!,
        $eventTypes: [GqlPoolEventType!]!,
        $first: Int!
      ) {
        poolEvents(
          where: {
            typeIn: $eventTypes,
            chainIn: $chains,
            poolIdIn: $poolIds,
            userAddress: $userAddress
          },
          first: $first
        ) {
          type
          valueUsd
          timestamp
          poolId
          ... on GqlPoolAddRemoveEventV3 {
            tokens {
              address
              amount
              valueUsd
            }
          }
        }
      }
    `;

    const variables = {
      userAddress,
      poolIds,
      chains,
      eventTypes,
      first
    };

    const result = await this.executeQuery<{ poolEvents: PoolEvent[] }>(query, variables);
    return result.poolEvents;
  }

  /**
   * 3. Query Smart Order Router (SOR) - Best Swap Paths
   */
  async getOptimalSwapPath(
    tokenIn: string,
    tokenOut: string,
    swapAmount: string,
    swapType: SwapType = SwapType.EXACT_IN,
    chain: BalancerChain = BalancerChain.MAINNET
  ): Promise<SwapPath> {
    const query = `
      query GetOptimalSwapPath(
        $chain: GqlChain!,
        $swapAmount: String!,
        $swapType: GqlSorSwapType!,
        $tokenIn: String!,
        $tokenOut: String!
      ) {
        sorGetSwapPaths(
          chain: $chain,
          swapAmount: $swapAmount,
          swapType: $swapType,
          tokenIn: $tokenIn,
          tokenOut: $tokenOut
        ) {
          swapAmountRaw
          returnAmountRaw
          priceImpact {
            priceImpact
            error
          }
          routes {
            hops {
              poolId
              tokenIn
              tokenOut
            }
          }
        }
      }
    `;

    const variables = {
      chain,
      swapAmount,
      swapType,
      tokenIn,
      tokenOut
    };

    const result = await this.executeQuery<{ sorGetSwapPaths: SwapPath }>(query, variables);
    return result.sorGetSwapPaths;
  }

  /**
   * 4. Get All Pools with TVL Filter
   */
  async getPoolsByTVL(
    chains: BalancerChain[] = [BalancerChain.MAINNET],
    minTvl: number = 10000,
    first: number = 100
  ): Promise<BalancerPool[]> {
    const query = `
      query GetPoolsByTVL($chains: [GqlChain!]!, $minTvl: Float!, $first: Int!) {
        poolGetPools(where: {chainIn: $chains, minTvl: $minTvl}, first: $first) {
          id
          address
          name
          chain
          type
          version
          dynamicData {
            totalLiquidity
            aprItems {
              title
              type
              apr
            }
          }
          allTokens {
            address
            name
            symbol
          }
          poolTokens {
            address
            symbol
            balance
            hasNestedPool
          }
        }
      }
    `;

    const variables = {
      chains,
      minTvl,
      first
    };

    const result = await this.executeQuery<{ poolGetPools: BalancerPool[] }>(query, variables);
    return result.poolGetPools;
  }

  /**
   * 5. Get Top Pools Ordered by TVL
   */
  async getTopPoolsByTVL(
    first: number = 10,
    chains: BalancerChain[] = [BalancerChain.MAINNET]
  ): Promise<BalancerPool[]> {
    const query = `
      query GetTopPoolsByTVL($first: Int!, $chains: [GqlChain!]!) {
        poolGetPools(first: $first, orderBy: totalLiquidity, where: {chainIn: $chains}) {
          id
          name
          chain
          dynamicData {
            totalLiquidity
            aprItems {
              apr
            }
          }
          staking {
            gauge {
              gaugeAddress
            }
          }
        }
      }
    `;

    const variables = {
      first,
      chains
    };

    const result = await this.executeQuery<{ poolGetPools: BalancerPool[] }>(query, variables);
    return result.poolGetPools;
  }
}

// Export singleton instance
export const balancerService = new BalancerService();
