/**
 * 🚀 PARALLEL ORCHESTRATOR
 * Enterprise-grade service that runs Balancer and 0x integrations in parallel
 * Real-time data aggregation and arbitrage opportunity detection
 */

import { EventEmitter } from 'events';
import { balancerService, BalancerChain, SwapType } from '../integrations/balancer-service';
import { zrxService, ZrxChain } from '../integrations/zrx-service';
import { logger } from './logger';

// Real-time data interfaces
export interface ArbitrageOpportunity {
  id: string;
  timestamp: number;
  tokenA: string;
  tokenB: string;
  balancerPrice: number;
  zrxPrice: number;
  spread: number;
  profitUsd: number;
  gasEstimate: string;
  netProfitUsd: number;
  confidence: number;
  source: 'balancer-to-0x' | '0x-to-balancer';
  executionPath: {
    buy: {
      protocol: 'balancer' | '0x';
      route: any;
    };
    sell: {
      protocol: 'balancer' | '0x';
      route: any;
    };
  };
}

export interface MarketSnapshot {
  timestamp: number;
  balancerData: {
    topPools: any[];
    totalTvl: number;
    activeTokens: number;
  };
  zrxData: {
    supportedTokens: number;
    liquiditySources: string[];
    averageGasPrice: string;
  };
  arbitrageOpportunities: ArbitrageOpportunity[];
  systemHealth: {
    balancerStatus: 'healthy' | 'degraded' | 'down';
    zrxStatus: 'healthy' | 'degraded' | 'down';
    lastUpdate: number;
  };
}

/**
 * 🚀 PARALLEL ORCHESTRATOR CLASS
 * Coordinates Balancer and 0x services for maximum efficiency
 */
export class ParallelOrchestrator extends EventEmitter {
  private isRunning: boolean = false;
  private scanInterval: number = 5000; // 5 seconds
  private intervalId: NodeJS.Timeout | null = null;
  private lastSnapshot: MarketSnapshot | null = null;

  // Configuration
  private readonly config = {
    minSpreadBps: parseInt(process.env.NEXT_PUBLIC_MIN_SPREAD_BPS || '23'),
    maxSlippageBps: parseInt(process.env.NEXT_PUBLIC_MAX_SLIPPAGE_BPS || '50'),
    minProfitUsd: parseFloat(process.env.NEXT_PUBLIC_PROFIT_THRESHOLD_USD || '10'),
    maxGasCostUsd: parseFloat(process.env.MAX_GAS_COST_USD || '20'),
    
    // Token pairs to monitor (Base Sepolia)
    monitoredPairs: [
      {
        tokenA: '0x4200000000000000000000000000000000000006', // WETH
        tokenB: '0x036CbD53842c5426634e7929541eC2318f3dCF7e', // USDC
        symbol: 'WETH/USDC'
      },
      {
        tokenA: '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb', // DAI
        tokenB: '0x036CbD53842c5426634e7929541eC2318f3dCF7e', // USDC
        symbol: 'DAI/USDC'
      },
      {
        tokenA: '0x4200000000000000000000000000000000000006', // WETH
        tokenB: '0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f', // GHO
        symbol: 'WETH/GHO'
      }
    ]
  };

  constructor() {
    super();
    this.setupEventHandlers();
  }

  /**
   * Setup event handlers for real-time updates
   */
  private setupEventHandlers(): void {
    this.on('arbitrageFound', (opportunity: ArbitrageOpportunity) => {
      logger.info('🎯 Arbitrage opportunity detected:', {
        id: opportunity.id,
        spread: opportunity.spread,
        profit: opportunity.profitUsd,
        pair: `${opportunity.tokenA}/${opportunity.tokenB}`
      });
    });

    this.on('marketUpdate', (snapshot: MarketSnapshot) => {
      logger.info('📊 Market snapshot updated:', {
        opportunities: snapshot.arbitrageOpportunities.length,
        balancerTvl: snapshot.balancerData.totalTvl,
        systemHealth: snapshot.systemHealth
      });
    });

    this.on('error', (error: Error) => {
      logger.error('🚨 Orchestrator error:', error);
    });
  }

  /**
   * Start the parallel orchestrator
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      logger.warn('Orchestrator is already running');
      return;
    }

    logger.info('🚀 Starting Parallel Orchestrator...');
    this.isRunning = true;

    // Initial scan
    await this.performMarketScan();

    // Setup interval scanning
    this.intervalId = setInterval(async () => {
      try {
        await this.performMarketScan();
      } catch (error) {
        this.emit('error', error);
      }
    }, this.scanInterval);

    logger.info('✅ Parallel Orchestrator started successfully');
  }

  /**
   * Stop the orchestrator
   */
  stop(): void {
    if (!this.isRunning) {
      return;
    }

    logger.info('🛑 Stopping Parallel Orchestrator...');
    this.isRunning = false;

    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    logger.info('✅ Parallel Orchestrator stopped');
  }

  /**
   * Perform comprehensive market scan
   */
  private async performMarketScan(): Promise<void> {
    const startTime = Date.now();
    
    try {
      // Run Balancer and 0x data collection in parallel
      const [balancerData, zrxData] = await Promise.all([
        this.collectBalancerData(),
        this.collectZrxData()
      ]);

      // Find arbitrage opportunities
      const arbitrageOpportunities = await this.findArbitrageOpportunities();

      // Create market snapshot
      const snapshot: MarketSnapshot = {
        timestamp: Date.now(),
        balancerData,
        zrxData,
        arbitrageOpportunities,
        systemHealth: {
          balancerStatus: balancerData ? 'healthy' : 'down',
          zrxStatus: zrxData ? 'healthy' : 'down',
          lastUpdate: Date.now()
        }
      };

      this.lastSnapshot = snapshot;
      this.emit('marketUpdate', snapshot);

      // Emit individual arbitrage opportunities
      arbitrageOpportunities.forEach(opportunity => {
        if (opportunity.netProfitUsd > this.config.minProfitUsd) {
          this.emit('arbitrageFound', opportunity);
        }
      });

      const scanTime = Date.now() - startTime;
      logger.info(`📊 Market scan completed in ${scanTime}ms`);

    } catch (error) {
      logger.error('Failed to perform market scan:', error);
      this.emit('error', error);
    }
  }

  /**
   * Collect Balancer data
   */
  private async collectBalancerData(): Promise<any> {
    try {
      const [topPools, poolsByTvl] = await Promise.all([
        balancerService.getTopPoolsByTVL(10, [BalancerChain.MAINNET]),
        balancerService.getPoolsByTVL([BalancerChain.MAINNET], 10000, 50)
      ]);

      const totalTvl = topPools.reduce((sum, pool) => {
        return sum + parseFloat(pool.dynamicData.totalLiquidity || '0');
      }, 0);

      const activeTokens = new Set();
      poolsByTvl.forEach(pool => {
        pool.allTokens.forEach(token => activeTokens.add(token.address));
      });

      return {
        topPools,
        totalTvl,
        activeTokens: activeTokens.size
      };
    } catch (error) {
      logger.error('Failed to collect Balancer data:', error);
      return null;
    }
  }

  /**
   * Collect 0x data
   */
  private async collectZrxData(): Promise<any> {
    try {
      const [tokens, liquiditySources] = await Promise.all([
        zrxService.getTokens(ZrxChain.ETHEREUM),
        zrxService.getLiquiditySources(ZrxChain.ETHEREUM)
      ]);

      return {
        supportedTokens: tokens.length,
        liquiditySources,
        averageGasPrice: '20' // This would be fetched from gas oracle in production
      };
    } catch (error) {
      logger.error('Failed to collect 0x data:', error);
      return null;
    }
  }

  /**
   * Find arbitrage opportunities between Balancer and 0x
   */
  private async findArbitrageOpportunities(): Promise<ArbitrageOpportunity[]> {
    const opportunities: ArbitrageOpportunity[] = [];

    for (const pair of this.config.monitoredPairs) {
      try {
        // Get Balancer optimal path
        const balancerPath = await balancerService.getOptimalSwapPath(
          pair.tokenA,
          pair.tokenB,
          '1000000000000000000', // 1 token
          SwapType.EXACT_IN,
          BalancerChain.MAINNET
        );

        // Get 0x price
        const zrxPrice = await zrxService.getPrice({
          chainId: ZrxChain.ETHEREUM,
          sellToken: pair.tokenA,
          buyToken: pair.tokenB,
          sellAmount: '1000000000000000000'
        });

        // Calculate spread
        const balancerRate = parseFloat(balancerPath.returnAmountRaw) / parseFloat(balancerPath.swapAmountRaw);
        const zrxRate = parseFloat(zrxPrice.buyAmount) / parseFloat(zrxPrice.sellAmount);
        const spread = Math.abs(balancerRate - zrxRate) / Math.min(balancerRate, zrxRate) * 100;

        if (spread > (this.config.minSpreadBps / 100)) {
          const opportunity: ArbitrageOpportunity = {
            id: `${pair.tokenA}-${pair.tokenB}-${Date.now()}`,
            timestamp: Date.now(),
            tokenA: pair.tokenA,
            tokenB: pair.tokenB,
            balancerPrice: balancerRate,
            zrxPrice: zrxRate,
            spread,
            profitUsd: spread * 1000, // Simplified calculation
            gasEstimate: zrxPrice.estimatedGas,
            netProfitUsd: (spread * 1000) - parseFloat(zrxPrice.estimatedGas) * 0.00002, // Rough gas cost
            confidence: spread > 1 ? 0.9 : 0.7,
            source: balancerRate > zrxRate ? 'balancer-to-0x' : '0x-to-balancer',
            executionPath: {
              buy: {
                protocol: balancerRate < zrxRate ? 'balancer' : '0x',
                route: balancerRate < zrxRate ? balancerPath : zrxPrice
              },
              sell: {
                protocol: balancerRate < zrxRate ? '0x' : 'balancer',
                route: balancerRate < zrxRate ? zrxPrice : balancerPath
              }
            }
          };

          opportunities.push(opportunity);
        }
      } catch (error) {
        logger.warn(`Failed to analyze pair ${pair.symbol}:`, error.message);
      }
    }

    return opportunities;
  }

  /**
   * Get latest market snapshot
   */
  getLatestSnapshot(): MarketSnapshot | null {
    return this.lastSnapshot;
  }

  /**
   * Get system status
   */
  getStatus(): {
    isRunning: boolean;
    uptime: number;
    lastScan: number | null;
    config: any;
  } {
    return {
      isRunning: this.isRunning,
      uptime: this.isRunning ? Date.now() - (this.lastSnapshot?.timestamp || Date.now()) : 0,
      lastScan: this.lastSnapshot?.timestamp || null,
      config: this.config
    };
  }
}

// Export singleton instance
export const parallelOrchestrator = new ParallelOrchestrator();
