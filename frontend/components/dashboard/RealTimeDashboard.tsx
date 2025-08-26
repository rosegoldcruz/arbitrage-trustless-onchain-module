"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  TrendingUp,
  Zap,
  Network,
  DollarSign,
  Bot,
  RefreshCw,
  Play,
  AlertCircle,
  CheckCircle,
  Clock,
  Target
} from "lucide-react";
import { RecentTradesTable } from "./RecentTradesTable";

import { toast } from "sonner";
import { realTimeApi, DashboardStatus, ArbitrageOpportunity } from "@/lib/realTimeApi";

export function RealTimeDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardStatus | null>(null);
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [executingOpportunities, setExecutingOpportunities] = useState<Set<string>>(new Set());

  // Fetch REAL dashboard data using API client
  const fetchDashboardData = async () => {
    try {
      console.log('🔄 Fetching dashboard data from:', process.env.NEXT_PUBLIC_API_BASE);
      const data = await realTimeApi.getDashboardStatus();
      console.log('✅ Dashboard data received:', data);
      setDashboardData(data);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('❌ Error fetching dashboard data:', error);
      toast.error(`Failed to fetch dashboard data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Fetch REAL opportunities using API client
  const fetchOpportunities = async () => {
    try {
      console.log('🔄 Fetching opportunities...');
      const data = await realTimeApi.getOpportunities();
      console.log('✅ Opportunities received:', data);
      setOpportunities(data.opportunities);
    } catch (error) {
      console.error('❌ Error fetching opportunities:', error);
      toast.error(`Failed to fetch opportunities: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Execute opportunity using API client with proper loading states
  const executeOpportunity = async (opportunityId: string, opportunity?: ArbitrageOpportunity) => {
    try {
      // Add to executing set
      setExecutingOpportunities(prev => new Set(prev).add(opportunityId));

      // Extract token triple from opportunity path if available
      let tokenTriple = ["DAI", "USDC", "GHO"]; // default
      if (opportunity?.path) {
        // Parse path like "WETH → USDC → DAI → WETH" to get tokens
        const tokens = opportunity.path.split(' → ').map(t => t.trim());
        if (tokens.length >= 3) {
          tokenTriple = [tokens[0], tokens[1], tokens[2]];
        }
      }

      const result = await realTimeApi.executeOpportunity(opportunityId, tokenTriple, "1");
      toast.success(`🚀 Executed! Profit: $${result.profit_realized.toFixed(2)} | TX: ${result.tx_hash.slice(0, 10)}...`);

      // Refresh data after execution
      await Promise.all([fetchDashboardData(), fetchOpportunities()]);
    } catch (error) {
      console.error('Error executing opportunity:', error);
      const reason = error instanceof Error ? error.message : 'Unknown error';
      // If the backend returns spread threshold reason, surface it clearly
      toast.error(`Execution blocked: ${reason}`);
    } finally {
      // Remove from executing set
      setExecutingOpportunities(prev => {
        const newSet = new Set(prev);
        newSet.delete(opportunityId);
        return newSet;
      });
    }
  };

  // Auto-refresh data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null);
        await Promise.all([fetchDashboardData(), fetchOpportunities()]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();

    // Refresh every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-400" />
        <div className="text-center">
          <p className="text-lg">Loading REAL data...</p>
          <p className="text-sm text-gray-400">Connecting to {process.env.NEXT_PUBLIC_API_URL}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <AlertCircle className="h-8 w-8 text-red-400" />
        <div className="text-center">
          <p className="text-lg text-red-400">Connection Error</p>
          <p className="text-sm text-gray-400">{error}</p>
          <Button
            onClick={() => window.location.reload()}
            className="mt-4"
            variant="outline"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry Connection
          </Button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <AlertCircle className="h-8 w-8 text-yellow-400" />
        <div className="text-center">
          <p className="text-lg text-yellow-400">No Data Available</p>
          <p className="text-sm text-gray-400">Backend connected but no data received</p>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
      case 'active':
      case 'running':
        return 'bg-green-500';
      case 'error':
      case 'failed':
        return 'bg-red-500';
      case 'connecting':
      case 'initializing':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
      case 'active':
      case 'running':
        return <CheckCircle className="h-4 w-4" />;
      case 'error':
      case 'failed':
        return <AlertCircle className="h-4 w-4" />;
      case 'connecting':
        return <RefreshCw className="h-4 w-4 animate-spin" />;

      case 'initializing':
        return <RefreshCw className="h-4 w-4 animate-spin" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">🚀 REAL-TIME DASHBOARD</h1>
          <p className="text-muted-foreground">Live DEX data • Last update: {lastUpdate}</p>
        </div>
        <Badge variant={dashboardData.system_status === 'running' ? 'default' : 'destructive'}>
          {dashboardData.system_status.toUpperCase()}
        </Badge>
      </div>
      {/* System Status Notice */}
      <div className="rounded-md border border-green-700 bg-green-900/30 text-green-300 px-4 py-3">
        🚀 ATOM Arbitrage System running on Polygon Mainnet. All DEX integrations active and operational.
      </div>


      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Profit</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${dashboardData.total_profit.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              From REAL arbitrage execution
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Bots</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboardData.active_agents}/{Object.keys(dashboardData.agents).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Connected to REAL DEXs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Opportunities</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboardData.real_time_data.profitable_paths}
            </div>
            <p className="text-xs text-muted-foreground">
              Profitable paths found
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">ETH Price</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${dashboardData.real_time_data.eth_price.toFixed(0)}
            </div>
            <p className="text-xs text-muted-foreground">
              From REAL DEX quotes
            </p>
          </CardContent>
        </Card>
      </div>

      {/* DEX Connections */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5" />
            REAL DEX Connections
          </CardTitle>
          <CardDescription>Live connection status to decentralized exchanges</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {Object.entries(dashboardData.dex_connections)
              .filter(([dex]) => dex.toLowerCase() !== '0x')
              .map(([dex, status]) => (
                <div key={dex} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(status)}`} />
                  <span className="text-sm font-medium">{dex}</span>
                  {getStatusIcon(status)}
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      {/* Bot Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            Production Bots
          </CardTitle>
          <CardDescription>REAL bot status and performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(dashboardData.agents).map(([botName, bot]) => (
              <div key={botName} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(bot.status)}`} />
                  <div>
                    <h4 className="font-medium">{botName.toUpperCase()}</h4>
                    <p className="text-sm text-muted-foreground">{bot.type}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium">${bot.profit.toFixed(2)}</p>
                  <p className="text-sm text-muted-foreground">{bot.trades} trades</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Trades Table */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-2 text-gray-100">Recent Trades</h3>
        <RecentTradesTable />
      </div>

      {/* Live Opportunities */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            LIVE Arbitrage Opportunities
          </CardTitle>
          <CardDescription>Real-time opportunities from DEX aggregator</CardDescription>
        </CardHeader>
        <CardContent>
          {opportunities.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No profitable opportunities found (≥23bps)
            </p>
          ) : (
            <div className="space-y-3">
              {opportunities.map((opp) => (
                <motion.div
                  key={opp.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center justify-between p-4 border rounded-lg bg-gradient-to-r from-green-900/20 to-blue-900/20 border-green-500/30 hover:border-green-400/50 transition-colors"
                >
                  <div>
                    <h4 className="font-medium text-white">{opp.path}</h4>
                    <p className="text-sm text-gray-300">
                      via {opp.dex_route} • {opp.confidence.toFixed(1)}% confidence
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="font-bold text-green-400">{opp.spread_bps}bps</p>
                      <p className="text-sm text-gray-300">${opp.profit_usd.toFixed(2)}</p>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => executeOpportunity(opp.id, opp)}
                      disabled={executingOpportunities.has(opp.id)}
                      className="bg-green-600 text-white hover:bg-green-700 disabled:bg-gray-700 disabled:text-gray-300 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 border border-green-500/40"
                    >
                      {executingOpportunities.has(opp.id) ? (
                        <>
                          <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                          Executing...
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 mr-1" />
                          Execute
                        </>
                      )}
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
