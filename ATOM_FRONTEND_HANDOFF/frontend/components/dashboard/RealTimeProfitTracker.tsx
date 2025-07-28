"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Zap, 
  Target,
  Flame,
  Crown,
  Rocket
} from "lucide-react";
import { api } from "@/lib/api";

interface ProfitUpdate {
  id: string;
  amount: number;
  agent: string;
  pair: string;
  timestamp: Date;
  type: 'profit' | 'loss';
}

export function RealTimeProfitTracker() {
  const [totalProfit, setTotalProfit] = useState(4591.57);
  const [recentUpdates, setRecentUpdates] = useState<ProfitUpdate[]>([]);
  const [isStreaking, setIsStreaking] = useState(false);
  const [streakCount, setStreakCount] = useState(0);
  const [dailyGoal] = useState(1000);
  const [achievements, setAchievements] = useState<string[]>([]);
  const [multiplier, setMultiplier] = useState(1.0);

  useEffect(() => {
    // Simulate real-time profit updates
    const interval = setInterval(() => {
      const agents = ['ATOM', 'ADOM', 'MEV_SENTINEL'];
      const pairs = ['ETH/USDC', 'WBTC/ETH', 'DAI/USDC', 'USDT/DAI'];
      
      const isProfit = Math.random() > 0.15; // 85% profit rate
      const amount = isProfit 
        ? Math.random() * 200 + 10  // $10-$210 profit
        : -(Math.random() * 50 + 5); // $5-$55 loss

      const update: ProfitUpdate = {
        id: `update-${Date.now()}-${Math.random()}`,
        amount: parseFloat(amount.toFixed(2)),
        agent: agents[Math.floor(Math.random() * agents.length)],
        pair: pairs[Math.floor(Math.random() * pairs.length)],
        timestamp: new Date(),
        type: isProfit ? 'profit' : 'loss'
      };

      setRecentUpdates(prev => {
        const updated = [update, ...prev].slice(0, 10);
        
        // Check for streak
        const recentProfits = updated.slice(0, 5).filter(u => u.type === 'profit');
        if (recentProfits.length === 5) {
          setIsStreaking(true);
          setStreakCount(prev => prev + 1);
        } else if (recentProfits.length < 3) {
          setIsStreaking(false);
          setStreakCount(0);
        }
        
        return updated;
      });

      setTotalProfit(prev => prev + amount);
    }, 3000 + Math.random() * 4000); // 3-7 second intervals

    return () => clearInterval(interval);
  }, []);

  const dailyProgress = Math.min((totalProfit % dailyGoal) / dailyGoal * 100, 100);
  const isNearGoal = dailyProgress > 80;

  return (
    <div className="space-y-4">
      {/* Main Profit Display */}
      <Card className="bg-gradient-to-br from-green-900/20 to-blue-900/20 border-green-500/30 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-blue-500/5 animate-pulse" />
        
        <CardHeader className="relative">
          <CardTitle className="flex items-center justify-between text-white">
            <div className="flex items-center space-x-2">
              <DollarSign className="h-6 w-6 text-green-400" />
              <span>Total Profit</span>
              {isStreaking && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="flex items-center space-x-1"
                >
                  <Flame className="h-5 w-5 text-orange-400 animate-bounce" />
                  <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/30">
                    🔥 {streakCount}x STREAK!
                  </Badge>
                </motion.div>
              )}
            </div>
            
            {isNearGoal && (
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                className="flex items-center space-x-1"
              >
                <Target className="h-5 w-5 text-yellow-400" />
                <span className="text-yellow-400 text-sm font-semibold">
                  Goal: {dailyProgress.toFixed(0)}%
                </span>
              </motion.div>
            )}
          </CardTitle>
        </CardHeader>
        
        <CardContent className="relative">
          <motion.div
            key={totalProfit}
            initial={{ scale: 1.1, color: "#10b981" }}
            animate={{ scale: 1, color: "#ffffff" }}
            transition={{ duration: 0.5 }}
            className="text-4xl font-bold mb-4"
          >
            ${totalProfit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </motion.div>
          
          {/* Daily Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Daily Goal Progress</span>
              <span className="text-green-400">${(totalProfit % dailyGoal).toFixed(2)} / ${dailyGoal}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-green-500 to-blue-500"
                initial={{ width: 0 }}
                animate={{ width: `${dailyProgress}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Updates Feed */}
      <Card className="bg-gray-900/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center text-white">
            <Zap className="h-5 w-5 mr-2 text-yellow-400" />
            Live Profit Feed
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            <AnimatePresence mode="popLayout">
              {recentUpdates.map((update) => (
                <motion.div
                  key={update.id}
                  initial={{ opacity: 0, x: -50, scale: 0.9 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  exit={{ opacity: 0, x: 50, scale: 0.9 }}
                  transition={{ duration: 0.3 }}
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    update.type === 'profit' 
                      ? 'bg-green-500/10 border-green-500/30' 
                      : 'bg-red-500/10 border-red-500/30'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`p-1 rounded-full ${
                      update.type === 'profit' ? 'bg-green-500/20' : 'bg-red-500/20'
                    }`}>
                      {update.type === 'profit' ? (
                        <TrendingUp className="h-4 w-4 text-green-400" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-400" />
                      )}
                    </div>
                    
                    <div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className="text-xs">
                          {update.agent}
                        </Badge>
                        <span className="text-sm text-gray-300">{update.pair}</span>
                      </div>
                      <div className="text-xs text-gray-400">
                        {update.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                  
                  <div className={`text-lg font-bold ${
                    update.type === 'profit' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {update.type === 'profit' ? '+' : ''}${Math.abs(update.amount).toFixed(2)}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            
            {recentUpdates.length === 0 && (
              <div className="text-center py-8 text-gray-400">
                <Rocket className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>Waiting for profit updates...</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Achievement Notifications */}
      <AnimatePresence>
        {isStreaking && streakCount > 0 && streakCount % 5 === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -50, scale: 0.8 }}
            className="fixed bottom-4 right-4 z-50"
          >
            <Card className="bg-gradient-to-r from-orange-500/20 to-red-500/20 border-orange-500/50">
              <CardContent className="p-4">
                <div className="flex items-center space-x-3">
                  <Crown className="h-8 w-8 text-yellow-400 animate-bounce" />
                  <div>
                    <div className="text-lg font-bold text-white">
                      🎉 LEGENDARY STREAK!
                    </div>
                    <div className="text-sm text-orange-400">
                      {streakCount} consecutive profitable trades!
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
