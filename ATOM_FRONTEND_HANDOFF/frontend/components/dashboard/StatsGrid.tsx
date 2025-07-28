"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign, TrendingUp, Activity, Clock, Loader2, Bot, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface OverallStats {
  total_profit: number;
  total_trades: number;
  successful_trades: number;
  success_rate: number;
  avg_profit_per_trade: number;
  total_gas_spent: number;
  uptime_hours: number;
  active_agents: number;
}

export function StatsGrid() {
  const [statsData, setStatsData] = useState<OverallStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.stats.overview();
      if (response.success && response.data) {
        setStatsData(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      toast.error('Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  // Show loading state
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="bg-gray-900/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-center h-20">
                <Loader2 className="h-8 w-8 animate-spin text-blue-400" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // Show error state
  if (!statsData) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gray-900/50 border-gray-700 col-span-full">
          <CardContent className="p-6">
            <div className="text-center text-gray-400">
              Failed to load statistics. Please try refreshing the page.
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const stats = [
    {
      title: "Total Profit",
      value: `$${statsData.total_profit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      change: `+$${statsData.avg_profit_per_trade.toFixed(2)} avg`,
      changeType: "positive" as const,
      icon: DollarSign,
      description: "Total profit from all trades",
    },
    {
      title: "Total Trades",
      value: statsData.total_trades.toLocaleString(),
      change: `${statsData.successful_trades} successful`,
      changeType: "positive" as const,
      icon: Activity,
      description: "All arbitrage trades executed",
    },
    {
      title: "Success Rate",
      value: `${statsData.success_rate.toFixed(1)}%`,
      change: `${statsData.successful_trades}/${statsData.total_trades}`,
      changeType: (statsData.success_rate > 90 ? "positive" : statsData.success_rate > 70 ? "neutral" : "negative") as "positive" | "neutral" | "negative",
      icon: TrendingUp,
      description: "Trade success percentage",
    },
    {
      title: "Active Agents",
      value: statsData.active_agents.toString(),
      change: `${statsData.uptime_hours}h uptime`,
      changeType: "positive" as const,
      icon: Bot,
      description: "AI agents currently running",
    },
  ];

  const getChangeColor = (type: "positive" | "negative" | "neutral") => {
    switch (type) {
      case "positive":
        return "text-green-400";
      case "negative":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: index * 0.1 }}
        >
          <Card className="bg-gray-900/50 border-gray-700 hover:bg-gray-800/50 transition-colors duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white mb-1">
                {stat.value}
              </div>
              <div className="flex items-center space-x-2">
                <span className={`text-xs font-medium ${getChangeColor(stat.changeType)}`}>
                  {stat.change}
                </span>
                <span className="text-xs text-gray-500">from yesterday</span>
              </div>
              <CardDescription className="text-xs text-gray-400 mt-2">
                {stat.description}
              </CardDescription>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
