'use client';

/**
 * 🚀 PARALLEL DASHBOARD COMPONENT
 * Live Balancer & 0x data visualization for Base Sepolia
 * NO MOCK DATA - PRODUCTION GRADE REAL-TIME FEEDS
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  Zap, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';

// Types for our live data
interface BalancerPool {
  id: string;
  address: string;
  name: string;
  chain: string;
  type: string;
  tvl: number;
  apr: number;
  tokens: Array<{
    address: string;
    symbol: string;
    balance: string;
  }>;
  timestamp: string;
}

interface ZrxPrice {
  token: string;
  symbol: string;
  priceUsd: number;
  volume24h?: number;
  priceChange24h?: number;
  timestamp: string;
}

interface ArbitrageOpportunity {
  id: string;
  tokenA: string;
  tokenB: string;
  spread: number;
  spreadBps: number;
  profitUsd: number;
  netProfitUsd: number;
  gasEstimate: string;
  confidence: number;
  source: string;
  balancerPrice: number;
  zrxPrice: number;
  timestamp: number;
}

interface SystemHealth {
  balancerStatus: 'healthy' | 'degraded' | 'down';
  zrxStatus: 'healthy' | 'degraded' | 'down';
  thegraphStatus: 'healthy' | 'degraded' | 'down';
  lastUpdate: number;
}

const ParallelDashboard: React.FC = () => {
  // State management
  const [balancerPools, setBalancerPools] = useState<BalancerPool[]>([]);
  const [zrxPrices, setZrxPrices] = useState<ZrxPrice[]>([]);
  const [thegraphPools, setThegraphPools] = useState<any[]>([]);
  const [thegraphOpportunities, setThegraphOpportunities] = useState<any[]>([]);
  const [arbitrageOpportunities, setArbitrageOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [wsConnected, setWsConnected] = useState(false);

  // API base URL
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'https://api.aeoninvestmentstechnologies.com';

  // Fetch Balancer pools
  const fetchBalancerPools = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/parallel/balancer/pools?min_tvl=1000&limit=20`);
      const result = await response.json();
      
      if (result.success) {
        setBalancerPools(result.data);
      } else {
        throw new Error('Failed to fetch Balancer pools');
      }
    } catch (err) {
      console.error('Error fetching Balancer pools:', err);
      setError(`Balancer pools error: ${err instanceof Error ? err.message : String(err)}`);
    }
  }, [API_BASE]);

  // Fetch 0x prices
  const fetchZrxPrices = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/parallel/zrx/prices`);
      const result = await response.json();
      
      if (result.success) {
        setZrxPrices(result.data);
      } else {
        throw new Error('Failed to fetch 0x prices');
      }
    } catch (err) {
      console.error('Error fetching 0x prices:', err);
      setError(`0x prices error: ${err instanceof Error ? err.message : String(err)}`);
    }
  }, [API_BASE]);

  // Fetch arbitrage opportunities
  const fetchArbitrageOpportunities = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/parallel/arbitrage/opportunities?min_spread_bps=23&min_profit_usd=10`);
      const result = await response.json();

      if (result.success) {
        setArbitrageOpportunities(result.data);
        if (result.systemHealth) {
          setSystemHealth(result.systemHealth);
        }
      } else {
        throw new Error('Failed to fetch arbitrage opportunities');
      }
    } catch (err) {
      console.error('Error fetching arbitrage opportunities:', err);
      setError(`Arbitrage opportunities error: ${err instanceof Error ? err.message : String(err)}`);
    }
  }, [API_BASE]);

  // Fetch The Graph pools
  const fetchThegraphPools = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/parallel/thegraph/pools?min_tvl=1000&limit=20`);
      const result = await response.json();

      if (result.success) {
        setThegraphPools(result.data);
      } else {
        throw new Error('Failed to fetch The Graph pools');
      }
    } catch (err) {
      console.error('Error fetching The Graph pools:', err);
      setError(`The Graph pools error: ${err instanceof Error ? err.message : String(err)}`);
    }
  }, [API_BASE]);

  // Fetch The Graph opportunities
  const fetchThegraphOpportunities = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/parallel/thegraph/opportunities?min_spread_bps=23&min_tvl=1000`);
      const result = await response.json();

      if (result.success) {
        setThegraphOpportunities(result.data);
      } else {
        throw new Error('Failed to fetch The Graph opportunities');
      }
    } catch (err) {
      console.error('Error fetching The Graph opportunities:', err);
      setError(`The Graph opportunities error: ${err instanceof Error ? err.message : String(err)}`);
    }
  }, [API_BASE]);

  // Check system health
  const checkSystemHealth = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/parallel/health`);
      const result = await response.json();
      
      if (result.status) {
        setSystemHealth({
          balancerStatus: result.services.balancer === 'healthy' ? 'healthy' : 'degraded',
          zrxStatus: result.services.zrx === 'healthy' ? 'healthy' : 'degraded',
          thegraphStatus: result.services.thegraph === 'healthy' ? 'healthy' : 'degraded',
          lastUpdate: Date.now()
        });
      }
    } catch (err) {
      console.error('Error checking system health:', err);
      setSystemHealth({
        balancerStatus: 'down',
        zrxStatus: 'down',
        thegraphStatus: 'down',
        lastUpdate: Date.now()
      });
    }
  }, [API_BASE]);

  // Refresh all data
  const refreshAllData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      await Promise.all([
        fetchBalancerPools(),
        fetchZrxPrices(),
        fetchThegraphPools(),
        fetchThegraphOpportunities(),
        fetchArbitrageOpportunities(),
        checkSystemHealth()
      ]);
      setLastUpdate(new Date());
    } catch (err) {
      setError(`Failed to refresh data: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsLoading(false);
    }
  }, [fetchBalancerPools, fetchZrxPrices, fetchArbitrageOpportunities, checkSystemHealth]);

  // WebSocket connection for live updates
  useEffect(() => {
    const wsUrl = `${API_BASE.replace('http', 'ws')}/api/parallel/ws/live-feed`;
    let ws: WebSocket;

    const connectWebSocket = () => {
      try {
        ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          console.log('WebSocket connected');
          setWsConnected(true);
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'market_update') {
              // Update system health from WebSocket
              if (data.data.systemHealth) {
                setSystemHealth(data.data.systemHealth);
              }
              setLastUpdate(new Date());
            }
          } catch (err) {
            console.error('WebSocket message error:', err);
          }
        };
        
        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setWsConnected(false);
          // Reconnect after 5 seconds
          setTimeout(connectWebSocket, 5000);
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setWsConnected(false);
        };
      } catch (err) {
        console.error('WebSocket connection error:', err);
        setWsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [API_BASE]);

  // Initial data load
  useEffect(() => {
    refreshAllData();
    
    // Set up periodic refresh every 30 seconds
    const interval = setInterval(refreshAllData, 30000);
    
    return () => clearInterval(interval);
  }, [refreshAllData]);

  // Helper functions
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    }).format(value);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'down':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800';
      case 'down':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">ATOM Parallel Dashboard</h1>
          <p className="text-muted-foreground">
            Live Balancer & 0x Analytics • Base Sepolia Testnet
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant={wsConnected ? "default" : "destructive"}>
            {wsConnected ? "Live" : "Disconnected"}
          </Badge>
          <Button onClick={refreshAllData} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* System Health */}
      {systemHealth && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="h-5 w-5 mr-2" />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="flex items-center justify-between">
                <span>Balancer Service</span>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(systemHealth.balancerStatus)}
                  <Badge className={getStatusColor(systemHealth.balancerStatus)}>
                    {systemHealth.balancerStatus}
                  </Badge>
                </div>
              </div>
              {/* 0x temporarily hidden on Base Sepolia */}
              {/* <div className="flex items-center justify-between">
                <span>0x Service</span>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(systemHealth.zrxStatus)}
                  <Badge className={getStatusColor(systemHealth.zrxStatus)}>
                    {systemHealth.zrxStatus}
                  </Badge>
                </div>
              </div> */}
              <div className="flex items-center justify-between">
                <span>The Graph</span>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(systemHealth.thegraphStatus)}
                  <Badge className={getStatusColor(systemHealth.thegraphStatus)}>
                    {systemHealth.thegraphStatus}
                  </Badge>
                </div>
              </div>
            </div>
            {lastUpdate && (
              <p className="text-sm text-muted-foreground mt-2">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Dashboard Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="balancer">Balancer Pools</TabsTrigger>
          {/* <TabsTrigger value="zrx">0x Prices</TabsTrigger> */}
          <TabsTrigger value="thegraph">The Graph</TabsTrigger>
          <TabsTrigger value="arbitrage">Arbitrage</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Balancer TVL</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(balancerPools.reduce((sum, pool) => sum + pool.tvl, 0))}
                </div>
                <p className="text-xs text-muted-foreground">
                  Across {balancerPools.length} pools
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Opportunities</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{arbitrageOpportunities.length}</div>
                <p className="text-xs text-muted-foreground">
                  Live arbitrage opportunities
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">The Graph Pools</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{thegraphPools.length}</div>
                <p className="text-xs text-muted-foreground">
                  Subgraph data pools
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Balancer Pools Tab */}
        <TabsContent value="balancer">
          <Card>
            <CardHeader>
              <CardTitle>Balancer Pools</CardTitle>
              <CardDescription>Live pool data from Balancer GraphQL API</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center p-8">
                  <RefreshCw className="h-8 w-8 animate-spin" />
                </div>
              ) : (
                <div className="space-y-4">
                  {balancerPools.map((pool) => (
                    <div key={pool.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold">{pool.name}</h3>
                          <p className="text-sm text-muted-foreground">{pool.type}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">{formatCurrency(pool.tvl)}</p>
                          <p className="text-sm text-green-600">{formatNumber(pool.apr)}% APR</p>
                        </div>
                      </div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {pool.tokens.map((token, idx) => (
                          <Badge key={idx} variant="outline">
                            {token.symbol}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* The Graph Tab */}
        <TabsContent value="thegraph">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>The Graph Protocol Pools</CardTitle>
                <CardDescription>Live subgraph data from Base Sepolia</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex items-center justify-center p-8">
                    <RefreshCw className="h-8 w-8 animate-spin" />
                  </div>
                ) : (
                  <div className="space-y-4">
                    {thegraphPools.map((pool) => (
                      <div key={pool.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-semibold">
                              {pool.token0.symbol}/{pool.token1.symbol}
                            </h3>
                            <p className="text-sm text-muted-foreground">
                              Pool ID: {pool.id.slice(0, 10)}...
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="font-semibold">{formatCurrency(pool.tvl)}</p>
                            <p className="text-sm text-blue-600">{pool.txCount} transactions</p>
                          </div>
                        </div>
                        <div className="mt-2 flex justify-between text-sm">
                          <span>Volume 24h: {formatCurrency(pool.volume24h)}</span>
                          <span>Liquidity: {pool.liquidity}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>The Graph Arbitrage Opportunities</CardTitle>
                <CardDescription>Cross-pool arbitrage detected by subgraph analysis</CardDescription>
              </CardHeader>
              <CardContent>
                {thegraphOpportunities.length === 0 ? (
                  <div className="text-center p-8 text-muted-foreground">
                    No arbitrage opportunities found
                  </div>
                ) : (
                  <div className="space-y-4">
                    {thegraphOpportunities.map((opp) => (
                      <div key={opp.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-semibold">{opp.tokenPair}</h3>
                            <p className="text-sm text-muted-foreground">
                              {opp.pool1.id.slice(0, 8)}... ↔ {opp.pool2.id.slice(0, 8)}...
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="font-semibold text-green-600">
                              {opp.spreadBps} bps
                            </p>
                            <p className="text-sm">
                              Est. Profit: {formatCurrency(opp.estimatedProfitUsd)}
                            </p>
                          </div>
                        </div>
                        <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-muted-foreground">Pool 1 TVL:</span>
                            <span className="ml-2">{formatCurrency(opp.pool1.tvl)}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Pool 2 TVL:</span>
                            <span className="ml-2">{formatCurrency(opp.pool2.tvl)}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ParallelDashboard;
