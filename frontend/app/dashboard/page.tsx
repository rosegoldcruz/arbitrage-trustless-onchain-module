"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Zap,
  TrendingUp,
  Activity,
  Settings,
  BarChart3,
  Network,
  DollarSign
} from "lucide-react";

// Import your awesome components
import { RealTimeDashboard } from "@/components/dashboard/RealTimeDashboard";
import ParallelDashboard from "@/components/dashboard/ParallelDashboard";
import { AnalyticsDashboard } from "@/components/dashboard/AnalyticsDashboard";
import { VolatilityWidget } from "@/components/dashboard/VolatilityWidget";
import { TriangularWidget } from "@/components/dashboard/TriangularWidget";
import { MEVWidget } from "@/components/dashboard/MEVWidget";
import { LiquidityWidget } from "@/components/dashboard/LiquidityWidget";
import { StatArbWidget } from "@/components/dashboard/StatArbWidget";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("realtime");

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white">
      {/* Header */}
      <div className="border-b border-gray-800 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                className="w-10 h-10 rounded-full overflow-hidden ring-1 ring-white/10"
              >
                {/* ATOM logo image */}
                <img src="/1.png" alt="ATOM" className="w-full h-full object-contain" />
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
          <TabsList className="grid w-full grid-cols-3 bg-gray-900/50 border border-gray-800">
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



          <TabsContent value="realtime" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <RealTimeDashboard />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <VolatilityWidget />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <TriangularWidget />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <MEVWidget />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <LiquidityWidget />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <StatArbWidget />
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
            >
              <AnalyticsDashboard />
            </motion.div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
