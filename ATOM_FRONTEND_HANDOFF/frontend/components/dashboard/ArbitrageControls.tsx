"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Zap, 
  Settings, 
  Play, 
  Pause, 
  TrendingUp, 
  Loader2, 
  AlertCircle, 
  CheckCircle, 
  Plus, 
  Trash2,
  DollarSign,
  Target,
  Shield
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { TransactionRippleLoader, DataRippleLoader } from "@/components/ui/RippleLoader";

interface ArbitrageOpportunity {
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
}

export function ArbitrageControls() {
  const [selectedNetwork, setSelectedNetwork] = useState("ethereum");
  const [selectedPair, setSelectedPair] = useState("ETH/USDC");
  const [tradeAmount, setTradeAmount] = useState("1.0");
  const [minProfit, setMinProfit] = useState("0.1");
  const [isExecuting, setIsExecuting] = useState(false);
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch opportunities
  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      const response = await api.arbitrage.opportunities({
        network: selectedNetwork,
        min_profit: parseFloat(minProfit),
        limit: 10
      });
      
      if (response.success && response.data) {
        setOpportunities(response.data.opportunities);
      }
    } catch (error) {
      console.error('Failed to fetch opportunities:', error);
      toast.error('Failed to load opportunities');
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh opportunities
  useEffect(() => {
    fetchOpportunities();
    const interval = setInterval(fetchOpportunities, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, [selectedNetwork, minProfit]);

  // Execute arbitrage
  const executeArbitrage = async () => {
    try {
      setIsExecuting(true);
      const response = await api.arbitrage.execute({
        assetPair: selectedPair,
        network: selectedNetwork,
        amount: parseFloat(tradeAmount),
        minProfitThreshold: parseFloat(minProfit)
      });
      
      if (response.success) {
        toast.success(`Arbitrage executed successfully! Profit: $${response.data.profit || '0.00'}`);
        fetchOpportunities(); // Refresh opportunities
      } else {
        toast.error('Failed to execute arbitrage');
      }
    } catch (error) {
      console.error('Arbitrage execution failed:', error);
      toast.error('Arbitrage execution failed');
    } finally {
      setIsExecuting(false);
    }
  };

  // Add token pair
  const addTokenPair = async () => {
    const [tokenA, tokenB] = selectedPair.split('/');
    try {
      const response = await api.tokens.addPair({
        tokenA,
        tokenB,
        network: selectedNetwork,
        auto_trade: true
      });
      
      if (response.success) {
        toast.success(`Token pair ${selectedPair} added successfully!`);
      } else {
        toast.error('Failed to add token pair');
      }
    } catch (error) {
      console.error('Failed to add token pair:', error);
      toast.error('Failed to add token pair');
    }
  };

  return (
    <div className="space-y-6">
      {/* Quick Controls */}
      <Card className="bg-gray-900/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center text-white">
            <Zap className="h-5 w-5 mr-2 text-blue-400" />
            Arbitrage Controls
          </CardTitle>
          <CardDescription className="text-gray-300">
            Execute arbitrage trades and manage opportunities
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="execute" className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-gray-800">
              <TabsTrigger value="execute" className="data-[state=active]:bg-blue-600">Execute</TabsTrigger>
              <TabsTrigger value="monitor" className="data-[state=active]:bg-blue-600">Monitor</TabsTrigger>
              <TabsTrigger value="settings" className="data-[state=active]:bg-blue-600">Settings</TabsTrigger>
            </TabsList>

            {/* Execute Tab */}
            <TabsContent value="execute" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <Label htmlFor="network" className="text-gray-300">Network</Label>
                  <Select value={selectedNetwork} onValueChange={setSelectedNetwork}>
                    <SelectTrigger className="bg-gray-800 border-gray-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800 border-gray-600">
                      <SelectItem value="ethereum">Ethereum</SelectItem>
                      <SelectItem value="base">Base</SelectItem>
                      <SelectItem value="arbitrum">Arbitrum</SelectItem>
                      <SelectItem value="polygon">Polygon</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="pair" className="text-gray-300">Token Pair</Label>
                  <Select value={selectedPair} onValueChange={setSelectedPair}>
                    <SelectTrigger className="bg-gray-800 border-gray-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800 border-gray-600">
                      <SelectItem value="ETH/USDC">ETH/USDC</SelectItem>
                      <SelectItem value="WBTC/ETH">WBTC/ETH</SelectItem>
                      <SelectItem value="DAI/USDC">DAI/USDC</SelectItem>
                      <SelectItem value="USDT/DAI">USDT/DAI</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="amount" className="text-gray-300">Amount</Label>
                  <Input
                    id="amount"
                    type="number"
                    value={tradeAmount}
                    onChange={(e) => setTradeAmount(e.target.value)}
                    className="bg-gray-800 border-gray-600 text-white"
                    placeholder="1.0"
                    step="0.1"
                    min="0.1"
                  />
                </div>

                <div>
                  <Label htmlFor="minProfit" className="text-gray-300">Min Profit %</Label>
                  <Input
                    id="minProfit"
                    type="number"
                    value={minProfit}
                    onChange={(e) => setMinProfit(e.target.value)}
                    className="bg-gray-800 border-gray-600 text-white"
                    placeholder="0.1"
                    step="0.01"
                    min="0.01"
                  />
                </div>
              </div>

              <div className="flex space-x-4">
                <Button
                  onClick={executeArbitrage}
                  disabled={isExecuting}
                  className="bg-green-600 hover:bg-green-700 flex-1"
                >
                  {isExecuting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Executing...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Execute Arbitrage
                    </>
                  )}
                </Button>

                <Button
                  onClick={addTokenPair}
                  variant="outline"
                  className="border-gray-600 hover:border-gray-500"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Pair
                </Button>
              </div>
            </TabsContent>

            {/* Monitor Tab */}
            <TabsContent value="monitor" className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Live Opportunities</h3>
                <Button
                  onClick={fetchOpportunities}
                  disabled={loading}
                  variant="outline"
                  size="sm"
                  className="border-gray-600 hover:border-gray-500"
                >
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    'Refresh'
                  )}
                </Button>
              </div>

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {opportunities.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    {loading ? 'Loading opportunities...' : 'No opportunities found'}
                  </div>
                ) : (
                  opportunities.map((opp) => (
                    <motion.div
                      key={opp.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-gray-800/50 rounded-lg p-4 border border-gray-700"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="text-blue-400 border-blue-400">
                            {opp.pair}
                          </Badge>
                          <Badge variant="outline" className="text-purple-400 border-purple-400">
                            {opp.network}
                          </Badge>
                        </div>
                        <div className="text-right">
                          <div className="text-green-400 font-semibold">
                            +${opp.estimated_profit.toFixed(2)}
                          </div>
                          <div className="text-xs text-gray-400">
                            {opp.profit_potential.toFixed(2)}%
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">Route:</span>
                          <div className="text-white">{opp.dex_buy} → {opp.dex_sell}</div>
                        </div>
                        <div>
                          <span className="text-gray-400">Confidence:</span>
                          <div className="text-white">{opp.confidence}%</div>
                        </div>
                      </div>

                      <div className="mt-3 flex items-center justify-between">
                        <div className="text-xs text-gray-400">
                          Expires in {opp.expires_in}s
                        </div>
                        <Button
                          size="sm"
                          className="bg-blue-600 hover:bg-blue-700"
                          onClick={() => {
                            setSelectedPair(opp.pair);
                            setSelectedNetwork(opp.network);
                            executeArbitrage();
                          }}
                        >
                          Execute
                        </Button>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            </TabsContent>

            {/* Settings Tab */}
            <TabsContent value="settings" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-white flex items-center">
                    <Settings className="h-5 w-5 mr-2" />
                    Risk Management
                  </h3>
                  
                  <div>
                    <Label className="text-gray-300">Max Trade Size (ETH)</Label>
                    <Input
                      type="number"
                      defaultValue="5.0"
                      className="bg-gray-800 border-gray-600 text-white"
                    />
                  </div>

                  <div>
                    <Label className="text-gray-300">Max Slippage (%)</Label>
                    <Input
                      type="number"
                      defaultValue="3.0"
                      className="bg-gray-800 border-gray-600 text-white"
                    />
                  </div>

                  <div>
                    <Label className="text-gray-300">Gas Price Limit (gwei)</Label>
                    <Input
                      type="number"
                      defaultValue="50"
                      className="bg-gray-800 border-gray-600 text-white"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-white flex items-center">
                    <Shield className="h-5 w-5 mr-2" />
                    Safety Features
                  </h3>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">MEV Protection</span>
                      <Badge className="bg-green-500/20 text-green-400">Enabled</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Flash Loan Fallback</span>
                      <Badge className="bg-green-500/20 text-green-400">Enabled</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Auto-Stop Loss</span>
                      <Badge className="bg-yellow-500/20 text-yellow-400">Monitoring</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
