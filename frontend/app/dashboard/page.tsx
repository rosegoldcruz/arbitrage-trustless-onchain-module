"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  TrendingUp,
  Zap,
  Shield,
  Bot,
  DollarSign,
  Activity,
  RefreshCw,
  Loader2,
  AlertCircle,
  Target,
  Network,
  CheckCircle,
  Play,
  Clock
} from "lucide-react";
import { toast } from "sonner";
import Navbar from "@/components/Navbar";
import { useWeb3Auth } from "@/contexts/Web3AuthContext";

// REAL API interfaces - NO FAKE DATA
interface DashboardData {
  system_status: string;
  agents: Record<string, {
    status: string;
    profit: number;
    trades: number;
    type: string;
  }>;
  total_profit: number;
  active_agents: number;
  dex_connections: Record<string, string>;
  real_time_data: {
    gas_price: number;
    eth_price: number;
    spread_opportunities: number;
    profitable_paths: number;
  };
}

interface Opportunity {
  id: string;
  path: string;
  spread_bps: number;
  profit_usd: number;
  dex_route: string;
  confidence: number;
  detected_at: string;
}

export default function Dashboard() {
  const { isConnected, address } = useWeb3Auth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const [connectionStatus, setConnectionStatus] = useState<string>("connecting");

  // Fetch REAL dashboard data from backend
  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/dashboard/status');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.status === 'success') {
        setDashboardData(result.data);
        setLastUpdate(new Date().toLocaleTimeString());
        setConnectionStatus("connected");
        
        // Only show success toast on first connection
        if (connectionStatus !== "connected") {
          toast.success('✅ Connected to REAL backend data');
        }
      } else {
        throw new Error('Backend returned error status');
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setConnectionStatus("error");
      toast.error('❌ Backend connection failed - Check if backend is running on port 8000');
    }
  };

  // Fetch REAL opportunities from backend
  const fetchOpportunities = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/dashboard/opportunities');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.status === 'success') {
        setOpportunities(result.data.opportunities);
      }
    } catch (error) {
      console.error('Error fetching opportunities:', error);
    }
  };

  // Execute REAL opportunity via backend
  const executeOpportunity = async (opportunityId: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/dashboard/execute-opportunity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ opportunity_id: opportunityId })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.status === 'success') {
        toast.success(`🚀 REAL execution! Profit: $${result.data.profit_realized.toFixed(2)} | TX: ${result.data.tx_hash.slice(0, 10)}...`);
        
        // Refresh data after execution
        await Promise.all([fetchDashboardData(), fetchOpportunities()]);
      } else {
        throw new Error(result.detail || 'Execution failed');
      }
    } catch (error) {
      console.error('Error executing opportunity:', error);
      toast.error('❌ Failed to execute opportunity');
    }
  };

  // Auto-refresh data every 10 seconds
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

  // Wallet connection check
  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
        <Navbar />
        <div className="flex items-center justify-center min-h-screen">
          <Card className="w-96 bg-gray-900/50 border-gray-700">
            <CardHeader className="text-center">
              <CardTitle className="text-white">🔐 Wallet Required</CardTitle>
              <CardDescription className="text-gray-300">
                Connect your wallet to access the REAL-TIME dashboard
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </div>
    );
  }

  // Loading state
  if (isLoading || !dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
        <Navbar />
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <RefreshCw className="h-8 w-8 animate-spin text-white" />
          <span className="text-white">Loading REAL data from backend...</span>
          <span className="text-sm text-gray-400">Status: {connectionStatus}</span>
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
      case 'configuration_error':
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
      case 'configuration_error':
        return <AlertCircle className="h-4 w-4" />;
      case 'connecting':
      case 'initializing':
        return <RefreshCw className="h-4 w-4 animate-spin" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white">🚀 REAL-TIME DASHBOARD</h1>
            <p className="text-gray-300">Live DEX data • Last update: {lastUpdate}</p>
            <p className="text-sm text-gray-400">Backend: {connectionStatus} • Port 8000</p>
          </div>
          <Badge variant={dashboardData.system_status === 'running' ? 'default' : 'destructive'}>
            {dashboardData.system_status.toUpperCase()}
          </Badge>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gray-900/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">Total Profit</CardTitle>
              <DollarSign className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">
                ${dashboardData.total_profit.toFixed(2)}
              </div>
              <p className="text-xs text-gray-400">
                From REAL arbitrage execution
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">Active Bots</CardTitle>
              <Bot className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {dashboardData.active_agents}/{Object.keys(dashboardData.agents).length}
              </div>
              <p className="text-xs text-gray-400">
                Connected to REAL DEXs
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">Opportunities</CardTitle>
              <Target className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {dashboardData.real_time_data.profitable_paths}
              </div>
              <p className="text-xs text-gray-400">
                Profitable paths found
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">ETH Price</CardTitle>
              <TrendingUp className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                ${dashboardData.real_time_data.eth_price.toFixed(0)}
              </div>
              <p className="text-xs text-gray-400">
                From REAL DEX quotes
              </p>
            </CardContent>
          </Card>
        </div>

        {/* DEX Connections */}
        <Card className="bg-gray-900/50 border-gray-700 mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Network className="h-5 w-5" />
              REAL DEX Connections
            </CardTitle>
            <CardDescription className="text-gray-400">Live connection status to decentralized exchanges</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(dashboardData.dex_connections).map(([dex, status]) => (
                <div key={dex} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(status)}`} />
                  <span className="text-sm font-medium text-white">{dex}</span>
                  {getStatusIcon(status)}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Production Bots - THE 4 REAL BOTS */}
        <Card className="bg-gray-900/50 border-gray-700 mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Bot className="h-5 w-5" />
              Production Bots (NO FAKE DATA)
            </CardTitle>
            <CardDescription className="text-gray-400">REAL bot status and performance from backend</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(dashboardData.agents).map(([botName, bot]) => (
                <div key={botName} className="flex items-center justify-between p-4 border border-gray-700 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(bot.status)}`} />
                    <div>
                      <h4 className="font-medium text-white">{botName.toUpperCase()}</h4>
                      <p className="text-sm text-gray-400">{bot.type}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-green-400">${bot.profit.toFixed(2)}</p>
                    <p className="text-sm text-gray-400">{bot.trades} trades</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Live Opportunities */}
        <Card className="bg-gray-900/50 border-gray-700">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Zap className="h-5 w-5" />
              LIVE Arbitrage Opportunities
            </CardTitle>
            <CardDescription className="text-gray-400">Real-time opportunities from DEX aggregator</CardDescription>
          </CardHeader>
          <CardContent>
            {opportunities.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-400 mb-2">No profitable opportunities found (≥23bps)</p>
                <p className="text-sm text-gray-500">Backend is scanning DEXs for arbitrage paths...</p>
              </div>
            ) : (
              <div className="space-y-3">
                {opportunities.map((opp) => (
                  <motion.div
                    key={opp.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center justify-between p-4 border border-gray-700 rounded-lg bg-gradient-to-r from-green-900/20 to-blue-900/20"
                  >
                    <div>
                      <h4 className="font-medium text-white">{opp.path}</h4>
                      <p className="text-sm text-gray-400">
                        via {opp.dex_route} • {opp.confidence.toFixed(1)}% confidence
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="font-bold text-green-400">{opp.spread_bps}bps</p>
                        <p className="text-sm text-gray-400">${opp.profit_usd.toFixed(2)}</p>
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
    </div>
  );
}
