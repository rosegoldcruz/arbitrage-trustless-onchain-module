"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Play, 
  Pause, 
  RotateCcw, 
  TrendingUp, 
  Zap, 
  DollarSign,
  Activity,
  ArrowRight,
  CheckCircle
} from "lucide-react";
import Link from "next/link";

export default function DemoPage() {
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [profit, setProfit] = useState(0);
  const [trades, setTrades] = useState(0);

  const demoSteps = [
    {
      title: "Scanning Markets",
      description: "AI agents monitoring price feeds across 15 DEXs",
      duration: 2000,
    },
    {
      title: "Opportunity Detected",
      description: "ETH/USDC price difference: Uniswap $2,456.78 vs Curve $2,461.23",
      duration: 1500,
    },
    {
      title: "Flash Loan Initiated",
      description: "Borrowing $50,000 USDC from AAVE (0.09% fee)",
      duration: 2000,
    },
    {
      title: "Executing Arbitrage",
      description: "Buy ETH on Uniswap, sell on Curve",
      duration: 1800,
    },
    {
      title: "Repaying Loan",
      description: "Flash loan repaid with interest",
      duration: 1200,
    },
    {
      title: "Profit Secured",
      description: "Net profit: $89.45 (0.18% return)",
      duration: 1000,
    },
  ];

  const startDemo = async () => {
    setIsRunning(true);
    setCurrentStep(0);
    setProfit(0);
    setTrades(0);

    for (let i = 0; i < demoSteps.length; i++) {
      setCurrentStep(i);
      await new Promise(resolve => setTimeout(resolve, demoSteps[i].duration));
      
      if (i === demoSteps.length - 1) {
        setProfit(prev => prev + 89.45);
        setTrades(prev => prev + 1);
      }
    }

    setIsRunning(false);
    setCurrentStep(0);
  };

  const resetDemo = () => {
    setIsRunning(false);
    setCurrentStep(0);
    setProfit(0);
    setTrades(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
      {/* Header */}
      <div className="border-b border-gray-800 bg-black/50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-2">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-2 rounded-lg">
                  <Zap className="h-6 w-6 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  ATOM
                </span>
              </Link>
              <div className="h-6 w-px bg-gray-600"></div>
              <h1 className="text-xl font-semibold text-white">Interactive Demo</h1>
            </div>
            
            <Link href="/dashboard">
              <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                Try Live Dashboard
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold text-white mb-4"
          >
            ATOM Demo
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-gray-300 max-w-3xl mx-auto"
          >
            Experience how ATOM executes risk-free arbitrage using flash loans. 
            This simulation shows the complete process from opportunity detection to profit realization.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Control Panel */}
          <div className="lg:col-span-1">
            <Card className="bg-gray-900/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Demo Controls</CardTitle>
                <CardDescription className="text-gray-300">
                  Run a simulated arbitrage trade
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">${profit.toFixed(2)}</div>
                    <div className="text-sm text-gray-400">Total Profit</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">{trades}</div>
                    <div className="text-sm text-gray-400">Trades</div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Button
                    onClick={startDemo}
                    disabled={isRunning}
                    className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
                  >
                    {isRunning ? (
                      <>
                        <Activity className="mr-2 h-4 w-4 animate-spin" />
                        Running Demo...
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4" />
                        Start Demo
                      </>
                    )}
                  </Button>
                  
                  <Button
                    onClick={resetDemo}
                    variant="outline"
                    className="w-full border-gray-600 text-white hover:bg-gray-700"
                  >
                    <RotateCcw className="mr-2 h-4 w-4" />
                    Reset
                  </Button>
                </div>
                
                <div className="pt-4 border-t border-gray-700">
                  <h4 className="text-sm font-medium text-white mb-2">Demo Parameters</h4>
                  <div className="space-y-1 text-xs text-gray-400">
                    <div>Network: Ethereum Mainnet</div>
                    <div>Pair: ETH/USDC</div>
                    <div>Amount: $50,000</div>
                    <div>Expected Profit: ~0.18%</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Process Visualization */}
          <div className="lg:col-span-2">
            <Card className="bg-gray-900/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Arbitrage Process</CardTitle>
                <CardDescription className="text-gray-300">
                  Watch how ATOM executes a complete arbitrage cycle
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {demoSteps.map((step, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0.5 }}
                      animate={{ 
                        opacity: isRunning && currentStep === index ? 1 : 
                                isRunning && currentStep > index ? 1 : 0.5,
                        scale: isRunning && currentStep === index ? 1.02 : 1
                      }}
                      className={`flex items-center space-x-4 p-4 rounded-lg border ${
                        isRunning && currentStep === index
                          ? 'border-blue-500 bg-blue-500/10'
                          : isRunning && currentStep > index
                          ? 'border-green-500 bg-green-500/10'
                          : 'border-gray-700 bg-gray-800/30'
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        isRunning && currentStep > index
                          ? 'bg-green-500'
                          : isRunning && currentStep === index
                          ? 'bg-blue-500'
                          : 'bg-gray-600'
                      }`}>
                        {isRunning && currentStep > index ? (
                          <CheckCircle className="h-4 w-4 text-white" />
                        ) : (
                          <span className="text-white text-sm font-medium">{index + 1}</span>
                        )}
                      </div>
                      
                      <div className="flex-1">
                        <h3 className="font-medium text-white">{step.title}</h3>
                        <p className="text-sm text-gray-400">{step.description}</p>
                      </div>
                      
                      {isRunning && currentStep === index && (
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>
                
                {!isRunning && profit > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 p-4 bg-gradient-to-r from-green-900/30 to-emerald-900/30 rounded-lg border border-green-700/30"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-green-400">Demo Complete!</h3>
                        <p className="text-sm text-gray-300">
                          Arbitrage executed successfully with ${profit.toFixed(2)} profit
                        </p>
                      </div>
                      <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                        Profitable
                      </Badge>
                    </div>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-12 text-center"
        >
          <Card className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border-blue-700/30">
            <CardContent className="py-8">
              <h2 className="text-2xl font-bold text-white mb-4">
                Ready to Start Earning?
              </h2>
              <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
                This demo shows just one arbitrage opportunity. ATOM runs 24/7, 
                executing hundreds of profitable trades across multiple networks and DEXs.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/dashboard">
                  <Button size="lg" className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                    Launch Dashboard
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/#pricing">
                  <Button size="lg" variant="outline" className="border-gray-600 text-white hover:bg-gray-700">
                    View Pricing
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
