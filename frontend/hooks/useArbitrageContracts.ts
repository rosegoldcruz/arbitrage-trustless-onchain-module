'use client';

/**
 * ATOM Arbitrage Contracts Hook
 * Web3 integration for triangular arbitrage and price monitoring
 * Connects smart contracts to React frontend
 */

import { useState, useEffect, useCallback } from 'react';
import { ethers, formatEther, parseEther } from 'ethers';
import { useWeb3Auth } from '@/contexts/Web3AuthContext';
import { toast } from 'sonner';

// Contract addresses (Base Sepolia - update after deployment)
const CONTRACT_ADDRESSES = {
  triangularArbitrage: '0x0000000000000000000000000000000000000000', // Update after deployment
  priceMonitor: '0x0000000000000000000000000000000000000000', // Update after deployment
  executionEngine: '0x0000000000000000000000000000000000000000', // Update after deployment
};

// Simplified ABIs for frontend interaction
const TRIANGULAR_ARBITRAGE_ABI = [
  'function executeTriangularArbitrage(tuple(address tokenA, address tokenB, address tokenC, address poolAB, address poolBC, address poolCA, uint256 amountIn, uint256 minProfitBps, bool useBalancer, bool useCurve) path)',
  'function totalExecutions() view returns (uint256)',
  'function successfulExecutions() view returns (uint256)',
  'function totalProfitUSD() view returns (uint256)',
  'function maxGasPrice() view returns (uint256)',
  'function maxSlippageBps() view returns (uint256)',
  'function minProfitUSD() view returns (uint256)',
  'event TriangularArbitrageExecuted(address indexed tokenA, address indexed tokenB, address indexed tokenC, uint256 amountIn, uint256 profit, uint256 gasUsed, bool successful)'
];

const PRICE_MONITOR_ABI = [
  'function getChainlinkPrice(address token) view returns (uint256 price, bool isStale)',
  'function calculateSpread(address tokenA, address tokenB, address dexAddress) view returns (int256 spreadBps, uint256 impliedPrice, uint256 externalPrice)',
  'function getActiveAlerts(uint256 limit) view returns (tuple(address tokenA, address tokenB, address dexAddress, int256 spreadBps, uint256 estimatedProfit, uint256 timestamp, bool isActive, string dexType)[])',
  'function spreadAlertThreshold() view returns (uint256)',
  'function totalAlertsGenerated() view returns (uint256)',
  'event ArbitrageOpportunity(address indexed tokenA, address indexed tokenB, address indexed dex, int256 spreadBps, uint256 estimatedProfit, string dexType)'
];

const EXECUTION_ENGINE_ABI = [
  'function scanArbitrageOpportunities() view returns (bytes32[] opportunities, uint256[] expectedProfits)',
  'function executeArbitrage(bytes32 tripleId, uint256 amount)',
  'function autoExecuteArbitrage() returns (uint256 executedCount)',
  'function getExecutionHistory(bytes32 tripleId, uint256 limit) view returns (tuple(bytes32 tripleId, uint256 amountIn, uint256 profit, uint256 gasUsed, uint256 timestamp, bool successful, string failureReason)[])',
  'event ArbitrageExecuted(bytes32 indexed tripleId, uint256 amountIn, uint256 profit, bool successful)'
];

// Token addresses (Base Sepolia)
export const TOKENS = {
  DAI: '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
  USDC: '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
  WETH: '0x4200000000000000000000000000000000000006',
  GHO: '0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f'
};

interface ArbitrageStats {
  totalExecutions: number;
  successfulExecutions: number;
  totalProfitUSD: number;
  successRate: number;
  dailyProfit: number;
}

interface ArbitrageOpportunity {
  id: string;
  tokenA: string;
  tokenB: string;
  tokenC: string;
  spreadBps: number;
  estimatedProfit: number;
  confidence: number;
  dexType: string;
  timestamp: number;
  isActive: boolean;
}

interface PriceData {
  token: string;
  chainlinkPrice: number;
  externalPrice: number;
  impliedPrice: number;
  spreadBps: number;
  isStale: boolean;
}

export function useArbitrageContracts() {
  const { isConnected, address, provider } = useWeb3Auth();
  const [contracts, setContracts] = useState<{
    triangularArbitrage: ethers.Contract | null;
    priceMonitor: ethers.Contract | null;
    executionEngine: ethers.Contract | null;
  }>({
    triangularArbitrage: null,
    priceMonitor: null,
    executionEngine: null
  });

  const [stats, setStats] = useState<ArbitrageStats>({
    totalExecutions: 0,
    successfulExecutions: 0,
    totalProfitUSD: 0,
    successRate: 0,
    dailyProfit: 0
  });

  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize contracts
  useEffect(() => {
    if (!provider || !isConnected) {
      setContracts({
        triangularArbitrage: null,
        priceMonitor: null,
        executionEngine: null
      });
      return;
    }

    try {
      const signer = provider.getSigner();
      
      const triangularArbitrage = new ethers.Contract(
        CONTRACT_ADDRESSES.triangularArbitrage,
        TRIANGULAR_ARBITRAGE_ABI,
        signer
      );

      const priceMonitor = new ethers.Contract(
        CONTRACT_ADDRESSES.priceMonitor,
        PRICE_MONITOR_ABI,
        signer
      );

      const executionEngine = new ethers.Contract(
        CONTRACT_ADDRESSES.executionEngine,
        EXECUTION_ENGINE_ABI,
        signer
      );

      setContracts({
        triangularArbitrage,
        priceMonitor,
        executionEngine
      });

      setError(null);
    } catch (err) {
      console.error('Failed to initialize contracts:', err);
      setError('Failed to initialize contracts');
    }
  }, [provider, isConnected]);

  // Fetch arbitrage statistics
  const fetchStats = useCallback(async () => {
    if (!contracts.triangularArbitrage) return;

    try {
      const [totalExecutions, successfulExecutions, totalProfitUSD] = await Promise.all([
        contracts.triangularArbitrage.totalExecutions(),
        contracts.triangularArbitrage.successfulExecutions(),
        contracts.triangularArbitrage.totalProfitUSD()
      ]);

      const successRate = totalExecutions > 0 
        ? (successfulExecutions / totalExecutions) * 100 
        : 0;

      setStats({
        totalExecutions: totalExecutions.toNumber(),
        successfulExecutions: successfulExecutions.toNumber(),
        totalProfitUSD: parseFloat(formatEther(totalProfitUSD)),
        successRate,
        dailyProfit: parseFloat(formatEther(totalProfitUSD)) // Simplified
      });
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  }, [contracts.triangularArbitrage]);

  // Fetch arbitrage opportunities
  const fetchOpportunities = useCallback(async () => {
    if (!contracts.priceMonitor) return;

    try {
      const alerts = await contracts.priceMonitor.getActiveAlerts(10);
      
      const formattedOpportunities: ArbitrageOpportunity[] = alerts.map((alert: any, index: number) => ({
        id: `opp-${Date.now()}-${index}`,
        tokenA: alert.tokenA,
        tokenB: alert.tokenB,
        tokenC: alert.tokenA, // Simplified for triangular
        spreadBps: alert.spreadBps.toNumber() / 100, // Convert to percentage
        estimatedProfit: parseFloat(formatEther(alert.estimatedProfit)),
        confidence: 85 + Math.random() * 15, // Mock confidence
        dexType: alert.dexType,
        timestamp: alert.timestamp.toNumber(),
        isActive: alert.isActive
      }));

      setOpportunities(formattedOpportunities);
    } catch (err) {
      console.error('Failed to fetch opportunities:', err);
    }
  }, [contracts.priceMonitor]);

  // Execute triangular arbitrage
  const executeArbitrage = useCallback(async (
    tokenA: string,
    tokenB: string,
    tokenC: string,
    amount: string
  ) => {
    if (!contracts.triangularArbitrage || !address) {
      toast.error('Contract not initialized or wallet not connected');
      return false;
    }

    setIsLoading(true);
    try {
      const path = {
        tokenA,
        tokenB,
        tokenC,
        poolAB: '0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E', // Mock pool addresses
        poolBC: '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0',
        poolCA: '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
        amountIn: parseEther(amount),
        minProfitBps: 23, // 0.23%
        useBalancer: false,
        useCurve: true
      };

      const tx = await contracts.triangularArbitrage.executeTriangularArbitrage(path);
      
      toast.success(`🚀 Arbitrage transaction submitted! Hash: ${tx.hash.slice(0, 10)}...`);
      
      const receipt = await tx.wait();
      
      if (receipt.status === 1) {
        toast.success('✅ Arbitrage executed successfully!');
        await fetchStats(); // Refresh stats
        return true;
      } else {
        toast.error('❌ Arbitrage transaction failed');
        return false;
      }
    } catch (err: any) {
      console.error('Arbitrage execution failed:', err);
      toast.error(`❌ Arbitrage failed: ${err.message || 'Unknown error'}`);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [contracts.triangularArbitrage, address, fetchStats]);

  // Get price data for tokens
  const fetchPriceData = useCallback(async () => {
    if (!contracts.priceMonitor) return;

    try {
      const tokenAddresses = Object.values(TOKENS);
      const pricePromises = tokenAddresses.map(async (token) => {
        try {
          const [price, isStale] = await contracts.priceMonitor!.getChainlinkPrice(token);
          return {
            token,
            chainlinkPrice: parseFloat(formatEther(price)),
            externalPrice: 0, // Would be fetched from external API
            impliedPrice: 0, // Would be calculated from DEX
            spreadBps: 0,
            isStale
          };
        } catch {
          return null;
        }
      });

      const results = await Promise.all(pricePromises);
      const validPrices = results.filter((price): price is PriceData => price !== null);
      setPriceData(validPrices);
    } catch (err) {
      console.error('Failed to fetch price data:', err);
    }
  }, [contracts.priceMonitor]);

  // Auto-refresh data
  useEffect(() => {
    if (!contracts.triangularArbitrage || !contracts.priceMonitor) return;

    const fetchData = async () => {
      await Promise.all([
        fetchStats(),
        fetchOpportunities(),
        fetchPriceData()
      ]);
    };

    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10 seconds

    return () => clearInterval(interval);
  }, [contracts, fetchStats, fetchOpportunities, fetchPriceData]);

  // Contract event listeners
  useEffect(() => {
    if (!contracts.triangularArbitrage) return;

    const handleArbitrageExecuted = (tokenA: string, tokenB: string, tokenC: string, amountIn: ethers.BigNumber, profit: ethers.BigNumber, gasUsed: ethers.BigNumber, successful: boolean) => {
      const profitUSD = parseFloat(formatEther(profit));
      
      if (successful) {
        toast.success(`🎉 Arbitrage completed! Profit: $${profitUSD.toFixed(2)}`);
      } else {
        toast.error('❌ Arbitrage execution failed');
      }
      
      fetchStats(); // Refresh stats
    };

    contracts.triangularArbitrage.on('TriangularArbitrageExecuted', handleArbitrageExecuted);

    return () => {
      contracts.triangularArbitrage.off('TriangularArbitrageExecuted', handleArbitrageExecuted);
    };
  }, [contracts.triangularArbitrage, fetchStats]);

  return {
    // Contract instances
    contracts,
    
    // Data
    stats,
    opportunities,
    priceData,
    
    // State
    isLoading,
    error,
    isConnected: isConnected && !!contracts.triangularArbitrage,
    
    // Actions
    executeArbitrage,
    fetchStats,
    fetchOpportunities,
    fetchPriceData,
    
    // Utils
    formatCurrency: (amount: number) => new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount),
    
    formatLargeNumber: (num: number) => {
      if (num >= 1000000) return `$${(num / 1000000).toFixed(1)}M`;
      if (num >= 1000) return `$${(num / 1000).toFixed(0)}K`;
      return `$${num.toFixed(0)}`;
    }
  };
}
