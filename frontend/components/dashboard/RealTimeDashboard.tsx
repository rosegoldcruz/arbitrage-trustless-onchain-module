"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Activity,
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
import { toast } from "sonner";
import { realTimeApi, DashboardStatus, ArbitrageOpportunity } from "@/lib/realTimeApi";

export function RealTimeDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardStatus | null>(null);
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>("");

  // Fetch REAL dashboard data using API client
  const fetchDashboardData = async () => {
    try {
      const data = await realTimeApi.getDashboardStatus();
      setDashboardData(data);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to fetch REAL dashboard data');
    }
  };

  // Fetch REAL opportunities using API client
  const fetchOpportunities = async () => {
    try {
      const data = await realTimeApi.getOpportunities();
      setOpportunities(data.opportunities);
    } catch (error) {
      console.error('Error fetching opportunities:', error);
      toast.error('Failed to fetch REAL opportunities');
    }
  };

  // Execute opportunity using API client
  const executeOpportunity = async (opportunityId: string) => {
    try {
      const result = await realTimeApi.executeOpportunity(opportunityId);
      toast.success(`🚀 REAL execution! Profit: $${result.profit_realized.toFixed(2)} | TX: ${result.tx_hash.slice(0, 10)}...`);

      // Refresh data after execution
      await Promise.all([fetchDashboardData(), fetchOpportunities()]);
    } catch (error) {
      console.error('Error executing opportunity:', error);
      toast.error('Failed to execute REAL opportunity');
    }
  };

  // Auto-refresh data
  useEffect(() => {
    const fetchData = async () => {
      await Promise.all([fetchDashboardData(), fetchOpportunities()]);
      setIsLoading(false);
    };

    fetchData();
    
    // Refresh every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading || !dashboardData) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading REAL data...</span>
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
            {Object.entries(dashboardData.dex_connections).map(([dex, status]) => (
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
                  className="flex items-center justify-between p-4 border rounded-lg bg-gradient-to-r from-green-50 to-blue-50"
                >
                  <div>
                    <h4 className="font-medium">{opp.path}</h4>
                    <p className="text-sm text-muted-foreground">
                      via {opp.dex_route} • {opp.confidence.toFixed(1)}% confidence
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="font-bold text-green-600">{opp.spread_bps}bps</p>
                      <p className="text-sm text-muted-foreground">${opp.profit_usd.toFixed(2)}</p>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => executeOpportunity(opp.id)}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Play className="h-4 w-4 mr-1" />
                      Execute
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
