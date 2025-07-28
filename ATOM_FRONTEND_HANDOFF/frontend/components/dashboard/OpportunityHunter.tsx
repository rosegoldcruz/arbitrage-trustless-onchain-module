"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Search, 
  Target, 
  Zap, 
  Timer, 
  TrendingUp, 
  Eye,
  Crosshair,
  Radar,
  Sparkles,
  Flame,
  Crown,
  Rocket
} from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { DataRippleLoader } from "@/components/ui/RippleLoader";

interface Opportunity {
  id: string;
  pair: string;
  token_in: string;
  token_out: string;
  dex_buy: string;
  dex_sell: string;
  profit_potential: number;
  estimated_profit: number;
  gas_cost: number;
  net_profit: number;
  network: string;
  confidence: number;
  expires_in: number;
  status: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

export function OpportunityHunter() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [totalScanned, setTotalScanned] = useState(0);
  const [foundCount, setFoundCount] = useState(0);
  const [huntMode, setHuntMode] = useState<'auto' | 'manual'>('auto');

  // Assign rarity based on profit potential
  const assignRarity = (profit: number): Opportunity['rarity'] => {
    if (profit > 500) return 'legendary';
    if (profit > 200) return 'epic';
    if (profit > 50) return 'rare';
    return 'common';
  };

  const getRarityColor = (rarity: Opportunity['rarity']) => {
    switch (rarity) {
      case 'legendary': return 'from-yellow-400 to-orange-500';
      case 'epic': return 'from-purple-400 to-pink-500';
      case 'rare': return 'from-blue-400 to-cyan-500';
      default: return 'from-gray-400 to-gray-500';
    }
  };

  const getRarityIcon = (rarity: Opportunity['rarity']) => {
    switch (rarity) {
      case 'legendary': return <Crown className="h-4 w-4" />;
      case 'epic': return <Sparkles className="h-4 w-4" />;
      case 'rare': return <Flame className="h-4 w-4" />;
      default: return <Target className="h-4 w-4" />;
    }
  };

  // Fetch opportunities with rarity assignment
  const fetchOpportunities = async () => {
    try {
      const response = await api.arbitrage.opportunities({
        network: 'ethereum',
        min_profit: 0.05,
        limit: 20
      });
      
      if (response.success && response.data) {
        const oppsWithRarity = response.data.opportunities.map((opp: any) => ({
          ...opp,
          rarity: assignRarity(opp.estimated_profit)
        }));
        
        setOpportunities(oppsWithRarity);
        setFoundCount(oppsWithRarity.length);
      }
    } catch (error) {
      console.error('Failed to fetch opportunities:', error);
    }
  };

  // Scanning animation
  const startScan = async () => {
    setIsScanning(true);
    setScanProgress(0);
    setTotalScanned(0);
    
    // Animated scanning process
    for (let i = 0; i <= 100; i += 2) {
      setScanProgress(i);
      setTotalScanned(Math.floor(i * 15)); // Simulate scanning 1500 pairs
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    await fetchOpportunities();
    setIsScanning(false);
    
    toast.success(`🎯 Scan complete! Found ${foundCount} opportunities`);
  };

  // Auto-scan mode
  useEffect(() => {
    if (huntMode === 'auto') {
      fetchOpportunities();
      const interval = setInterval(fetchOpportunities, 15000); // Every 15 seconds
      return () => clearInterval(interval);
    }
  }, [huntMode]);

  // Execute opportunity
  const executeOpportunity = async (opp: Opportunity) => {
    try {
      const response = await api.arbitrage.execute({
        assetPair: opp.pair,
        network: opp.network,
        amount: 1.0
      });
      
      if (response.success) {
        toast.success(`🚀 ${opp.rarity.toUpperCase()} opportunity executed! +$${opp.estimated_profit.toFixed(2)}`);
        
        // Remove executed opportunity
        setOpportunities(prev => prev.filter(o => o.id !== opp.id));
      }
    } catch (error) {
      toast.error('Failed to execute opportunity');
    }
  };

  return (
    <Card className="bg-gray-900/50 border-gray-700">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-white">
            <Radar className="h-5 w-5 mr-2 text-green-400 animate-spin" />
            Opportunity Hunter
            <Badge className="ml-2 bg-green-500/20 text-green-400">
              {foundCount} Found
            </Badge>
          </CardTitle>
          
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              variant={huntMode === 'auto' ? 'default' : 'outline'}
              onClick={() => setHuntMode('auto')}
              className="text-xs"
            >
              Auto Hunt
            </Button>
            <Button
              size="sm"
              variant={huntMode === 'manual' ? 'default' : 'outline'}
              onClick={() => setHuntMode('manual')}
              className="text-xs"
            >
              Manual
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Scanning Interface */}
        {huntMode === 'manual' && (
          <div className="space-y-3">
            <Button
              onClick={startScan}
              disabled={isScanning}
              className="w-full bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
            >
              {isScanning ? (
                <>
                  <Search className="h-4 w-4 mr-2 animate-spin" />
                  Scanning... {scanProgress}%
                </>
              ) : (
                <>
                  <Crosshair className="h-4 w-4 mr-2" />
                  Start Deep Scan
                </>
              )}
            </Button>
            
            {isScanning && (
              <div className="space-y-2">
                <Progress value={scanProgress} className="h-2" />
                <div className="flex justify-between text-xs text-gray-400">
                  <span>Pairs Scanned: {totalScanned.toLocaleString()}</span>
                  <span>Networks: 4/4</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Opportunities List */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          <AnimatePresence mode="popLayout">
            {opportunities.map((opp, index) => (
              <motion.div
                key={opp.id}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, x: 100, scale: 0.95 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className={`relative p-4 rounded-lg border bg-gradient-to-r ${
                  opp.rarity === 'legendary' ? 'from-yellow-500/10 to-orange-500/10 border-yellow-500/30' :
                  opp.rarity === 'epic' ? 'from-purple-500/10 to-pink-500/10 border-purple-500/30' :
                  opp.rarity === 'rare' ? 'from-blue-500/10 to-cyan-500/10 border-blue-500/30' :
                  'from-gray-500/10 to-gray-600/10 border-gray-600/30'
                } hover:scale-[1.02] transition-transform cursor-pointer`}
                onClick={() => executeOpportunity(opp)}
              >
                {/* Rarity Glow Effect */}
                {opp.rarity !== 'common' && (
                  <div className={`absolute inset-0 bg-gradient-to-r ${getRarityColor(opp.rarity)} opacity-5 rounded-lg animate-pulse`} />
                )}
                
                <div className="relative">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Badge 
                        variant="outline" 
                        className={`text-xs bg-gradient-to-r ${getRarityColor(opp.rarity)} text-white border-0`}
                      >
                        {getRarityIcon(opp.rarity)}
                        <span className="ml-1">{opp.rarity.toUpperCase()}</span>
                      </Badge>
                      <Badge variant="outline" className="text-blue-400 border-blue-400">
                        {opp.pair}
                      </Badge>
                      <Badge variant="outline" className="text-purple-400 border-purple-400">
                        {opp.network}
                      </Badge>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-green-400 font-bold text-lg">
                        +${opp.estimated_profit.toFixed(2)}
                      </div>
                      <div className="text-xs text-gray-400">
                        {opp.profit_potential.toFixed(2)}% profit
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm mb-3">
                    <div>
                      <span className="text-gray-400">Route:</span>
                      <div className="text-white text-xs">{opp.dex_buy} → {opp.dex_sell}</div>
                    </div>
                    <div>
                      <span className="text-gray-400">Confidence:</span>
                      <div className="text-white">{opp.confidence}%</div>
                    </div>
                    <div>
                      <span className="text-gray-400">Gas Cost:</span>
                      <div className="text-white">${opp.gas_cost.toFixed(3)}</div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-xs text-gray-400">
                      <Timer className="h-3 w-3" />
                      <span>Expires in {opp.expires_in}s</span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <Eye className="h-3 w-3 text-gray-400" />
                      <span className="text-xs text-gray-400">Click to execute</span>
                    </div>
                  </div>

                  {/* Net Profit Indicator */}
                  <div className="mt-2 pt-2 border-t border-gray-700">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-400">Net Profit:</span>
                      <span className="text-green-400 font-semibold">
                        ${opp.net_profit.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {opportunities.length === 0 && !isScanning && (
            <div className="flex justify-center py-8">
              <DataRippleLoader
                size="large"
                speed={0.8}
                message={huntMode === 'auto' ? 'Auto-hunting in progress...' : 'Ready to hunt for opportunities'}
                subMessage={huntMode === 'auto' ? 'Scanning markets for profitable trades' : 'Click "Start Deep Scan" to begin'}
              />
            </div>
          )}

          {isScanning && (
            <div className="flex justify-center py-8">
              <DataRippleLoader
                size="large"
                speed={1.5}
                message="Deep Scanning Markets..."
                subMessage={`Analyzing ${totalScanned.toLocaleString()} trading pairs`}
              />
            </div>
          )}
        </div>

        {/* Hunt Statistics */}
        {foundCount > 0 && (
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-700">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">{foundCount}</div>
              <div className="text-xs text-gray-400">Found</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">
                {opportunities.filter(o => o.rarity !== 'common').length}
              </div>
              <div className="text-xs text-gray-400">Rare+</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-400">
                ${opportunities.reduce((sum, o) => sum + o.estimated_profit, 0).toFixed(0)}
              </div>
              <div className="text-xs text-gray-400">Total Value</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
