/**
 * 🚀 0x.org API Integration for ATOM Platform
 * Provides swap quotes, gasless transactions, and DEX aggregation
 */

import { toast } from "sonner";

// Types for 0x.org API responses
export interface SwapQuote {
  sellToken: string;
  buyToken: string;
  sellAmount: string;
  buyAmount: string;
  price: string;
  guaranteedPrice: string;
  to: string;
  data: string;
  value: string;
  gas: string;
  gasPrice: string;
  protocolFee: string;
  minimumProtocolFee: string;
  buyTokenAddress: string;
  sellTokenAddress: string;
  sources: Array<{
    name: string;
    proportion: string;
  }>;
  orders: any[];
  allowanceTarget: string;
  decodedUniqueId: string;
  sellTokenToEthRate: string;
  buyTokenToEthRate: string;
}

export interface GaslessQuote {
  transaction: {
    to: string;
    data: string;
    gas: string;
    gasPrice: string;
    value: string;
  };
  approval?: {
    to: string;
    data: string;
    gas: string;
    gasPrice: string;
    value: string;
  };
  trade: {
    sellToken: string;
    buyToken: string;
    sellAmount: string;
    buyAmount: string;
    tradeType: string;
  };
  fees: {
    integratorFee: string;
    zeroExFee: string;
    gasFee: string;
  };
}

export interface TokenInfo {
  address: string;
  symbol: string;
  name: string;
  decimals: number;
  logoURI?: string;
}

class ZeroXAPI {
  private apiKey: string;
  private baseUrl: string;
  private gaslessUrl: string;

  constructor() {
    this.apiKey = process.env.NEXT_PUBLIC_0X_API_KEY || process.env.THEATOM_API_KEY || '';
    this.baseUrl = process.env.ZRX_API_URL || 'https://api.0x.org';
    this.gaslessUrl = process.env.ZRX_GASLESS_API_URL || 'https://gasless.api.0x.org';

    if (!this.apiKey) {
      console.warn('⚠️ 0x.org API key not found. Some features may not work.');
    }
  }

  private getHeaders() {
    return {
      'Content-Type': 'application/json',
      '0x-api-key': this.apiKey,
      'User-Agent': 'ATOM-Platform/1.0',
    };
  }

  /**
   * Get a swap quote from 0x.org
   */
  async getSwapQuote(params: {
    sellToken: string;
    buyToken: string;
    sellAmount?: string;
    buyAmount?: string;
    slippagePercentage?: number;
    gasPrice?: string;
    takerAddress?: string;
    excludedSources?: string[];
    includedSources?: string[];
    skipValidation?: boolean;
    intentOnFilling?: boolean;
  }): Promise<SwapQuote | null> {
    try {
      const queryParams = new URLSearchParams();
      
      // Required parameters
      queryParams.append('sellToken', params.sellToken);
      queryParams.append('buyToken', params.buyToken);
      
      if (params.sellAmount) {
        queryParams.append('sellAmount', params.sellAmount);
      }
      if (params.buyAmount) {
        queryParams.append('buyAmount', params.buyAmount);
      }
      
      // Optional parameters
      if (params.slippagePercentage) {
        queryParams.append('slippagePercentage', params.slippagePercentage.toString());
      }
      if (params.gasPrice) {
        queryParams.append('gasPrice', params.gasPrice);
      }
      if (params.takerAddress) {
        queryParams.append('takerAddress', params.takerAddress);
      }
      if (params.excludedSources?.length) {
        queryParams.append('excludedSources', params.excludedSources.join(','));
      }
      if (params.includedSources?.length) {
        queryParams.append('includedSources', params.includedSources.join(','));
      }
      if (params.skipValidation) {
        queryParams.append('skipValidation', 'true');
      }
      if (params.intentOnFilling) {
        queryParams.append('intentOnFilling', 'true');
      }

      const response = await fetch(`${this.baseUrl}/swap/v1/quote?${queryParams}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`0x API Error: ${response.status} - ${errorData.reason || response.statusText}`);
      }

      const quote = await response.json();
      return quote as SwapQuote;
    } catch (error) {
      console.error('❌ Error fetching swap quote:', error);
      toast.error(`Failed to get swap quote: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return null;
    }
  }

  /**
   * Get a gasless quote from 0x.org
   */
  async getGaslessQuote(params: {
    sellToken: string;
    buyToken: string;
    sellAmount?: string;
    buyAmount?: string;
    takerAddress: string;
    slippagePercentage?: number;
  }): Promise<GaslessQuote | null> {
    try {
      const queryParams = new URLSearchParams();
      
      queryParams.append('sellToken', params.sellToken);
      queryParams.append('buyToken', params.buyToken);
      queryParams.append('takerAddress', params.takerAddress);
      
      if (params.sellAmount) {
        queryParams.append('sellAmount', params.sellAmount);
      }
      if (params.buyAmount) {
        queryParams.append('buyAmount', params.buyAmount);
      }
      if (params.slippagePercentage) {
        queryParams.append('slippagePercentage', params.slippagePercentage.toString());
      }

      const response = await fetch(`${this.gaslessUrl}/gasless/quote?${queryParams}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`0x Gasless API Error: ${response.status} - ${errorData.reason || response.statusText}`);
      }

      const quote = await response.json();
      return quote as GaslessQuote;
    } catch (error) {
      console.error('❌ Error fetching gasless quote:', error);
      toast.error(`Failed to get gasless quote: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return null;
    }
  }

  /**
   * Get supported tokens for a specific chain
   */
  async getSupportedTokens(chainId: number = 1): Promise<TokenInfo[]> {
    try {
      const response = await fetch(`${this.baseUrl}/swap/v1/tokens?chainId=${chainId}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch tokens: ${response.statusText}`);
      }

      const data = await response.json();
      return data.records || [];
    } catch (error) {
      console.error('❌ Error fetching supported tokens:', error);
      return [];
    }
  }

  /**
   * Get liquidity sources available on 0x
   */
  async getLiquiditySources(chainId: number = 1): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/swap/v1/sources?chainId=${chainId}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch liquidity sources: ${response.statusText}`);
      }

      const data = await response.json();
      return data.sources || [];
    } catch (error) {
      console.error('❌ Error fetching liquidity sources:', error);
      return [];
    }
  }

  /**
   * Check if API key is configured and working
   */
  async validateApiKey(): Promise<boolean> {
    if (!this.apiKey) {
      return false;
    }

    try {
      const response = await fetch(`${this.baseUrl}/swap/v1/sources`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      return response.ok;
    } catch (error) {
      console.error('❌ Error validating API key:', error);
      return false;
    }
  }

  /**
   * Get price for a token pair
   */
  async getPrice(params: {
    sellToken: string;
    buyToken: string;
    sellAmount?: string;
    buyAmount?: string;
  }): Promise<{ price: string; estimatedGas: string } | null> {
    try {
      const queryParams = new URLSearchParams();
      queryParams.append('sellToken', params.sellToken);
      queryParams.append('buyToken', params.buyToken);
      
      if (params.sellAmount) {
        queryParams.append('sellAmount', params.sellAmount);
      }
      if (params.buyAmount) {
        queryParams.append('buyAmount', params.buyAmount);
      }

      const response = await fetch(`${this.baseUrl}/swap/v1/price?${queryParams}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch price: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        price: data.price,
        estimatedGas: data.estimatedGas,
      };
    } catch (error) {
      console.error('❌ Error fetching price:', error);
      return null;
    }
  }
}

// Export singleton instance
export const zeroXAPI = new ZeroXAPI();

// Export utility functions
export const formatTokenAmount = (amount: string, decimals: number): string => {
  const num = parseFloat(amount) / Math.pow(10, decimals);
  return num.toFixed(6);
};

export const parseTokenAmount = (amount: string, decimals: number): string => {
  const num = parseFloat(amount) * Math.pow(10, decimals);
  return Math.floor(num).toString();
};
