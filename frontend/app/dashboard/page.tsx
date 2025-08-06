"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Bot,
  Zap,
  TrendingUp,
  Activity,
  Settings,
  Crown,
  Swords,
  BarChart3,
  Network,
  DollarSign
} from "lucide-react";

// Import your awesome components
import { AgentBattleArena } from "@/components/dashboard/AgentBattleArena";
import { RealTimeDashboard } from "@/components/dashboard/RealTimeDashboard";
import { ParallelDashboard } from "@/components/dashboard/ParallelDashboard";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("arena");

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white">
      {/* Header */}
      <div className="border-b border-gray-800 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg"
              >
                <Bot className="h-6 w-6" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  ATOM Dashboard
                </h1>
                <p className="text-sm text-gray-400">Advanced Arbitrage Command Center</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="border-green-500 text-green-400">
                <Activity className="h-3 w-3 mr-1" />
                LIVE
              </Badge>
              <Badge variant="outline" className="border-blue-500 text-blue-400">
                <Zap className="h-3 w-3 mr-1" />
                5 Agents Online
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {/* Main Dashboard */}
      <div className="container mx-auto px-6 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-gray-900/50 border border-gray-800">
            <TabsTrigger value="arena" className="flex items-center gap-2">
              <Swords className="h-4 w-4" />
              Bots Arena
            </TabsTrigger>
            <TabsTrigger value="realtime" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Real-Time
            </TabsTrigger>
            <TabsTrigger value="parallel" className="flex items-center gap-2">
              <Network className="h-4 w-4" />
              Parallel Data
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Analytics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="arena" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <AgentBattleArena />
            </motion.div>
          </TabsContent>

          <TabsContent value="realtime" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <RealTimeDashboard />
            </motion.div>
          </TabsContent>

          <TabsContent value="parallel" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <ParallelDashboard />
            </motion.div>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
            >
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <DollarSign className="h-5 w-5 text-green-400" />
                    Total Profit
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-green-400">$47,892.34</div>
                  <p className="text-sm text-gray-400">+12.5% from last week</p>
                </CardContent>
              </Card>

              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-blue-400" />
                    Success Rate
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-blue-400">94.7%</div>
                  <p className="text-sm text-gray-400">847 wins / 894 trades</p>
                </CardContent>
              </Card>

              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Crown className="h-5 w-5 text-yellow-400" />
                    Top Agent
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-yellow-400">ADOM</div>
                  <p className="text-sm text-gray-400">Level 52 • 456 wins</p>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
