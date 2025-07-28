"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Shield, Zap, Bot, TrendingUp, Clock, DollarSign } from "lucide-react";

export function AboutSection() {
  const benefits = [
    {
      icon: Shield,
      title: "Risk-Free Arbitrage",
      description: "Flash loans ensure you never risk your own capital. All transactions are atomic - they either succeed completely or fail completely, protecting you from partial execution risks.",
      color: "from-green-500 to-emerald-600"
    },
    {
      icon: Zap,
      title: "Instant Execution",
      description: "Our AI agents monitor thousands of trading pairs across multiple DEXs in real-time, executing profitable arbitrage opportunities within milliseconds of detection.",
      color: "from-blue-500 to-cyan-600"
    },
    {
      icon: Bot,
      title: "AI Agents",
      description: "ATOM handles basic arbitrage, ADOM manages complex multi-hop strategies, and MEV Sentinel protects against front-running while maximizing your profits.",
      color: "from-purple-500 to-violet-600"
    },
    {
      icon: Clock,
      title: "24/7 Operation",
      description: "Our agents work around the clock, never missing an opportunity. They operate across multiple time zones and market conditions to maximize your earning potential.",
      color: "from-orange-500 to-red-600"
    },
    {
      icon: TrendingUp,
      title: "Proven Strategy",
      description: "Arbitrage is one of the most reliable trading strategies in DeFi. By exploiting price differences across exchanges, you earn consistent profits regardless of market direction.",
      color: "from-pink-500 to-rose-600"
    },
    {
      icon: DollarSign,
      title: "No Capital Required",
      description: "Start earning immediately without any upfront investment. Flash loans provide the capital, you keep the profits. Scale your operations without increasing your risk.",
      color: "from-yellow-500 to-amber-600"
    },
  ];

  return (
    <section id="about" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            About ATOM
          </h2>
          <p className="text-xl text-gray-300 max-w-4xl mx-auto">
            ATOM revolutionizes DeFi arbitrage by combining flash loans with AI-powered agents. 
            Our platform eliminates the traditional barriers to arbitrage trading, making it accessible 
            to everyone regardless of capital requirements.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {benefits.map((benefit, index) => (
            <motion.div
              key={benefit.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="bg-gray-900/50 border-gray-700 h-full hover:bg-gray-800/50 transition-colors duration-300">
                <CardHeader>
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${benefit.color} flex items-center justify-center mb-4`}>
                    <benefit.icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-white text-xl">
                    {benefit.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-300 leading-relaxed">
                    {benefit.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          viewport={{ once: true }}
          className="mt-16 text-center"
        >
          <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-2xl p-8 border border-blue-700/30">
            <h3 className="text-2xl font-bold text-white mb-4">
              How It Works
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
              <div>
                <div className="text-3xl font-bold text-blue-400 mb-2">1</div>
                <h4 className="text-lg font-semibold text-white mb-2">Detect Opportunity</h4>
                <p className="text-gray-300">AI agents scan multiple DEXs for price discrepancies</p>
              </div>
              <div>
                <div className="text-3xl font-bold text-purple-400 mb-2">2</div>
                <h4 className="text-lg font-semibold text-white mb-2">Execute Flash Loan</h4>
                <p className="text-gray-300">Borrow assets instantly from AAVE or other protocols</p>
              </div>
              <div>
                <div className="text-3xl font-bold text-green-400 mb-2">3</div>
                <h4 className="text-lg font-semibold text-white mb-2">Profit & Repay</h4>
                <p className="text-gray-300">Complete the arbitrage and keep the profit</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
