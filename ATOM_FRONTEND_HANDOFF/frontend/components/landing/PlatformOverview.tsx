"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Globe, Coins, Bot, Shield, TrendingUp, Zap, ExternalLink } from "lucide-react";

export function PlatformOverview() {
  const chains = [
    { name: "Ethereum", color: "text-blue-400", url: "https://ethereum.org" },
    { name: "Base", color: "text-blue-500", url: "https://base.org" },
    { name: "Arbitrum", color: "text-blue-600", url: "https://arbitrum.io" },
    { name: "Polygon", color: "text-purple-400", url: "https://polygon.technology" },
  ];

  const dexs = [
    { name: "Uniswap", color: "text-pink-400", url: "https://uniswap.org" },
    { name: "Curve", color: "text-yellow-400", url: "https://curve.fi" },
    { name: "SushiSwap", color: "text-blue-400", url: "https://sushi.com" },
    { name: "Balancer", color: "text-green-400", url: "https://balancer.fi" },
  ];

  const protocols = [
    { name: "AAVE", color: "text-purple-400", url: "https://aave.com" },
    { name: "Compound", color: "text-green-400", url: "https://compound.finance" },
    { name: "1inch", color: "text-red-400", url: "https://1inch.io" },
    { name: "MakerDAO", color: "text-orange-400", url: "https://makerdao.com" },
    { name: "Chainlink", color: "text-blue-400", url: "https://chain.link" },
  ];

  const features = [
    {
      icon: Shield,
      title: "Risk-Free Arbitrage",
      description: "Flash loans eliminate capital requirements and guarantee atomic transactions",
      color: "from-green-500 to-emerald-600"
    },
    {
      icon: Zap,
      title: "Instant Execution",
      description: "AI agents detect and execute opportunities in milliseconds",
      color: "from-blue-500 to-cyan-600"
    },
    {
      icon: Bot,
      title: "AI Agents",
      description: "ATOM, ADOM, and MEV Sentinel work 24/7 to maximize profits",
      color: "from-purple-500 to-violet-600"
    },
  ];

  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Platform Overview
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            ATOM operates across multiple chains and protocols to maximize arbitrage opportunities
          </p>
        </motion.div>

        {/* Supported Networks */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <Card className="bg-gray-900/50 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <Globe className="h-6 w-6 mr-2 text-blue-400" />
                  Chains
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {chains.map((chain) => (
                    <Button
                      key={chain.name}
                      variant="ghost"
                      className={`w-full justify-between ${chain.color} hover:bg-gray-800/50 font-medium`}
                      onClick={() => window.open(chain.url, '_blank')}
                    >
                      {chain.name}
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            viewport={{ once: true }}
          >
            <Card className="bg-gray-900/50 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <TrendingUp className="h-6 w-6 mr-2 text-purple-400" />
                  DEXs
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {dexs.map((dex) => (
                    <Button
                      key={dex.name}
                      variant="ghost"
                      className={`w-full justify-between ${dex.color} hover:bg-gray-800/50 font-medium`}
                      onClick={() => window.open(dex.url, '_blank')}
                    >
                      {dex.name}
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            viewport={{ once: true }}
          >
            <Card className="bg-gray-900/50 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <Coins className="h-6 w-6 mr-2 text-green-400" />
                  Protocols
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {protocols.map((protocol) => (
                    <Button
                      key={protocol.name}
                      variant="ghost"
                      className={`w-full justify-between ${protocol.color} hover:bg-gray-800/50 font-medium`}
                      onClick={() => window.open(protocol.url, '_blank')}
                    >
                      {protocol.name}
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Key Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              viewport={{ once: true }}
            >
              <Card className="bg-gray-900/50 border-gray-700 h-full">
                <CardHeader>
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${feature.color} flex items-center justify-center mb-4`}>
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-white">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-300">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
