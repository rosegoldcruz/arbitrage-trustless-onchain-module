"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  TrendingUp,
  Zap,
  Shield,
  Bot,
  Settings,
  Play,
  Pause,
  DollarSign,
  Activity,
  Clock,
  RefreshCw,
  Loader2,
  AlertCircle,
  Target,
  Network,
  Flame
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import Link from "next/link";
import { StatsGrid } from "@/components/dashboard/StatsGrid";
import { AgentPanel } from "@/components/dashboard/AgentPanel";
import { ProfitChart } from "@/components/dashboard/ProfitChart";
import { ConsoleLogs } from "@/components/dashboard/ConsoleLogs";
import { TradeHistory } from "@/components/dashboard/TradeHistory";
import { ChatWithAgent } from "@/components/dashboard/ChatWithAgent";
import { ArbitrageControls } from "@/components/dashboard/ArbitrageControls";
import Navbar from "@/components/Navbar";
import { useWeb3Auth } from "@/components/web3/web3auth-provider";
import { RealTimeProfitTracker } from "@/components/dashboard/RealTimeProfitTracker";
import { OpportunityHunter } from "@/components/dashboard/OpportunityHunter";
import { AgentBattleArena } from "@/components/dashboard/AgentBattleArena";
import { EpicLoadingScreen } from "@/components/dashboard/EpicLoadingScreen";

interface SystemStatus {
  status: string;
  agents: any;
  total_profit: number;
  active_agents: number;
  last_update: string;
}

export default function Dashboard() {
  const { isConnected, address, isCorrectNetwork, login, logout } = useWeb3Auth();
  const [backendConnected, setBackendConnected] = useState(false);
  const [tradingMode, setTradingMode] = useState<'test' | 'live'>('test');
  const [selectedNetwork, setSelectedNetwork] = useState('ethereum');
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [showEpicLoading, setShowEpicLoading] = useState(true);

  // Fetch system status
  const fetchSystemStatus = async () => {
    try {
      const response = await api.health();
      if (response.success) {
        setSystemStatus(response.data);
        setBackendConnected(true);
        setLastRefresh(new Date());
      }
    } catch (error) {
      console.error('Failed to fetch system status:', error);
      setBackendConnected(false);
      toast.error('Failed to connect to backend');
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh system status
  useEffect(() => {
    fetchSystemStatus();

    const interval = setInterval(fetchSystemStatus, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Only trigger if not typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key) {
        case 'r':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            // Trigger arbitrage
            console.log('Keyboard shortcut: Run Arbitrage');
          }
          break;
        case 's':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            // Simulate flash loan
            console.log('Keyboard shortcut: Simulate Flash Loan');
          }
          break;
        case 'c':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            // Toggle wallet connection
            if (isConnected) {
              logout();
            } else {
              login();
            }
          }
          break;
        case '?':
          e.preventDefault();
          // Show help modal (could implement later)
          console.log('Keyboard shortcut: Show help');
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isConnected]);

  // Show epic loading screen first
  if (showEpicLoading) {
    return <EpicLoadingScreen onComplete={() => setShowEpicLoading(false)} />;
  }

  return (
      <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
        <Navbar />

        {/* Status Bar */}
        <div className="border-b border-gray-800 bg-black/30 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                {/* Connection Status */}
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
                  <span className="text-sm text-gray-300">
                    {isConnected ? 'Backend Connected' : 'Backend Disconnected'}
                  </span>
                </div>

                {/* System Status */}
                {systemStatus && (
                  <div className="text-sm text-gray-300">
                    Profit: <span className="text-green-400 font-semibold">${systemStatus.total_profit.toFixed(2)}</span>
                  </div>
                )}
              </div>

              <div className="flex items-center space-x-2">
                {/* Refresh Button */}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={fetchSystemStatus}
                  disabled={loading}
                  className="border-gray-600 hover:border-gray-500"
                >
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left Column - Stats and Controls */}
          <div className="lg:col-span-3 space-y-8">
            {/* Stats Grid */}
            <StatsGrid />
            
            {/* Control Panel */}
            <Card className="bg-gray-900/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Control Panel</CardTitle>
                <CardDescription className="text-gray-300">
                  Manage your arbitrage operations
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* 🚀 AEON NETWORK - THE FULL SYSTEM */}
                <div className="mb-6 space-y-4">
                  <Link href="/aeon">
                    <Button
                      size="lg"
                      className="w-full bg-gradient-to-r from-blue-500 via-purple-500 to-green-500 hover:from-blue-600 hover:via-purple-600 hover:to-green-600 text-white font-bold text-xl py-6 shadow-lg hover:shadow-xl transition-all duration-300 border-2 border-white/20"
                    >
                      <Network className="h-8 w-8 mr-4" />
                      🧠 AEON NETWORK - ADVANCED, EFFICIENT, OPTIMIZED
                      <Flame className="h-8 w-8 ml-4" />
                    </Button>
                  </Link>
                  <p className="text-center text-gray-300 text-sm">
                    🧠 AEON (On-chain) • 🔁 ATOM/ADOM (Hybrid) • ⚙️ SPECTRE (Analytics)
                  </p>
                  <p className="text-center text-gray-400 text-xs">
                    Three Parallel Ecosystems • Antifragile Intelligence • Cross-Validation
                  </p>
                </div>

                {/* 🚀 ARBITRAGE ENGINE - SINGLE SYSTEM */}
                <div className="mb-6">
                  <Link href="/arbitrage">
                    <Button
                      size="lg"
                      className="w-full bg-gradient-to-r from-green-500 via-blue-500 to-purple-600 hover:from-green-600 hover:via-blue-600 hover:to-purple-700 text-white font-bold text-lg py-4 shadow-lg hover:shadow-xl transition-all duration-300"
                    >
                      <Target className="h-6 w-6 mr-3" />
                      🚀 ARBITRAGE ENGINE - $150K DAILY TARGET
                      <DollarSign className="h-6 w-6 ml-3" />
                    </Button>
                  </Link>
                  <p className="text-center text-gray-400 text-sm mt-2">
                    $10M Flash Loans • 1% Profit • Real-time Opportunities
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <Button
                    className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                    disabled={!isConnected}
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Run Arbitrage
                  </Button>
                  
                  <Button 
                    variant="outline"
                    className="border-gray-600 text-white hover:bg-gray-800"
                    disabled={!isConnected}
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Simulate Flash Loan
                  </Button>
                  
                  <Button 
                    variant="outline"
                    className="border-gray-600 text-white hover:bg-gray-800"
                    disabled={!isConnected}
                  >
                    <Bot className="h-4 w-4 mr-2" />
                    Deploy Bot
                  </Button>
                  
                  <Button 
                    variant="outline"
                    className="border-gray-600 text-white hover:bg-gray-800"
                    disabled={!isConnected}
                  >
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Add Token Pair
                  </Button>
                </div>
                
                <div className="mt-6 flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div>
                      <label className="text-sm text-gray-300">Network</label>
                      <select 
                        value={selectedNetwork}
                        onChange={(e) => setSelectedNetwork(e.target.value)}
                        className="ml-2 bg-gray-800 border border-gray-600 text-white rounded px-3 py-1"
                      >
                        <option value="ethereum">Ethereum</option>
                        <option value="base">Base</option>
                        <option value="arbitrum">Arbitrum</option>
                        <option value="polygon">Polygon</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="text-sm text-gray-300">Mode</label>
                      <select 
                        value={tradingMode}
                        onChange={(e) => setTradingMode(e.target.value as 'test' | 'live')}
                        className="ml-2 bg-gray-800 border border-gray-600 text-white rounded px-3 py-1"
                      >
                        <option value="test">Test Mode</option>
                        <option value="live">Live Mode</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                    <span className="text-sm text-gray-300">
                      {isConnected ? 'Wallet Connected' : 'Wallet Disconnected'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {/* 🔥 REAL-TIME PROFIT TRACKER */}
            <RealTimeProfitTracker />

            {/* 🎯 OPPORTUNITY HUNTER */}
            <OpportunityHunter />

            {/* ⚡ ARBITRAGE CONTROLS */}
            <ArbitrageControls />

            {/* 📊 PROFIT CHART */}
            <ProfitChart />

            {/* 📈 TRADE HISTORY */}
            <TradeHistory />
          </div>
          
          {/* Right Column - EPIC AGENT FEATURES */}
          <div className="space-y-8">
            {/* 🏟️ AGENT BATTLE ARENA */}
            <AgentBattleArena />

            {/* 🤖 AI AGENTS PANEL */}
            <AgentPanel />

            {/* 💬 CONSOLE LOGS */}
            <ConsoleLogs />

            {/* 🧠 CHAT WITH AGENT */}
            <ChatWithAgent />
          </div>
        </div>
      </div>
      </div>
  );
}
