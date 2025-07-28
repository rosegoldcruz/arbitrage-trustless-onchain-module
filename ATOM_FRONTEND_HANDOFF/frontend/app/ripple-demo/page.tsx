"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  SystemRippleLoader,
  AgentRippleLoader,
  DataRippleLoader,
  TransactionRippleLoader,
  ErrorRippleLoader,
  SuccessRippleLoader
} from "@/components/ui/RippleLoader";

export default function RippleDemo() {
  const [activeDemo, setActiveDemo] = useState<string>('all');

  const demos = [
    {
      id: 'system',
      name: 'System Loading',
      component: <SystemRippleLoader size="large" message="Initializing ATOM..." />,
      description: 'Used for system startup and initialization'
    },
    {
      id: 'agent',
      name: 'AI Agent Processing',
      component: <AgentRippleLoader size="large" message="AI Processing..." />,
      description: 'When AI agents are analyzing and thinking'
    },
    {
      id: 'data',
      name: 'Data Loading',
      component: <DataRippleLoader size="large" message="Loading Market Data..." />,
      description: 'For fetching real-time market information'
    },
    {
      id: 'transaction',
      name: 'Transaction Processing',
      component: <TransactionRippleLoader size="large" message="Executing Trade..." />,
      description: 'During arbitrage execution and blockchain transactions'
    },
    {
      id: 'error',
      name: 'Error State',
      component: <ErrorRippleLoader size="large" message="Connection Failed" />,
      description: 'When errors occur in the system'
    },
    {
      id: 'success',
      name: 'Success State',
      component: <SuccessRippleLoader size="large" message="Trade Successful!" />,
      description: 'When operations complete successfully'
    }
  ];

  const sizes = [
    { id: 'small', name: 'Small', component: <SystemRippleLoader size="small" /> },
    { id: 'medium', name: 'Medium', component: <SystemRippleLoader size="medium" /> },
    { id: 'large', name: 'Large', component: <SystemRippleLoader size="large" /> },
    { id: 'xl', name: 'Extra Large', component: <SystemRippleLoader size="xl" /> }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-4">
            🌊 ATOM Ripple Loading System
          </h1>
          <p className="text-gray-300 text-lg">
            Beautiful, contextual loading animations for the ultimate arbitrage experience
          </p>
        </motion.div>

        {/* Navigation */}
        <div className="flex flex-wrap justify-center gap-2 mt-8">
          <Button
            variant={activeDemo === 'all' ? 'default' : 'outline'}
            onClick={() => setActiveDemo('all')}
            className="text-sm"
          >
            All Themes
          </Button>
          <Button
            variant={activeDemo === 'sizes' ? 'default' : 'outline'}
            onClick={() => setActiveDemo('sizes')}
            className="text-sm"
          >
            Size Variants
          </Button>
          {demos.map((demo) => (
            <Button
              key={demo.id}
              variant={activeDemo === demo.id ? 'default' : 'outline'}
              onClick={() => setActiveDemo(demo.id)}
              className="text-sm"
            >
              {demo.name}
            </Button>
          ))}
        </div>
      </div>

      {/* Demo Content */}
      <div className="max-w-7xl mx-auto">
        {activeDemo === 'all' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {demos.map((demo, index) => (
              <motion.div
                key={demo.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="bg-gray-900/50 border-gray-700 h-full">
                  <CardHeader>
                    <CardTitle className="text-white text-lg">{demo.name}</CardTitle>
                    <p className="text-gray-400 text-sm">{demo.description}</p>
                  </CardHeader>
                  <CardContent className="flex justify-center py-8">
                    {demo.component}
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}

        {activeDemo === 'sizes' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {sizes.map((size, index) => (
              <motion.div
                key={size.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="bg-gray-900/50 border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white text-center">{size.name}</CardTitle>
                  </CardHeader>
                  <CardContent className="flex justify-center py-8">
                    {size.component}
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}

        {activeDemo !== 'all' && activeDemo !== 'sizes' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex justify-center"
          >
            <Card className="bg-gray-900/50 border-gray-700 max-w-2xl w-full">
              <CardHeader className="text-center">
                <CardTitle className="text-white text-2xl">
                  {demos.find(d => d.id === activeDemo)?.name}
                </CardTitle>
                <p className="text-gray-400">
                  {demos.find(d => d.id === activeDemo)?.description}
                </p>
              </CardHeader>
              <CardContent className="flex justify-center py-12">
                {demos.find(d => d.id === activeDemo)?.component}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Speed Controls Demo */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-12"
        >
          <Card className="bg-gray-900/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white text-center">Speed Variations</CardTitle>
              <p className="text-gray-400 text-center">Different animation speeds for different contexts</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="text-center">
                  <Badge className="mb-4 bg-blue-500/20 text-blue-400">Slow (0.5x)</Badge>
                  <SystemRippleLoader size="medium" speed={0.5} message="Thinking deeply..." />
                </div>
                <div className="text-center">
                  <Badge className="mb-4 bg-green-500/20 text-green-400">Normal (1x)</Badge>
                  <SystemRippleLoader size="medium" speed={1} message="Processing..." />
                </div>
                <div className="text-center">
                  <Badge className="mb-4 bg-red-500/20 text-red-400">Fast (2x)</Badge>
                  <SystemRippleLoader size="medium" speed={2} message="Urgent action!" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Integration Examples */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mt-12"
        >
          <Card className="bg-gray-900/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white text-center">Real-World Integration Examples</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-white">Dashboard Loading States</h3>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-4 p-4 bg-gray-800/50 rounded-lg">
                      <DataRippleLoader size="small" showMessage={false} />
                      <div>
                        <p className="text-white font-medium">Loading market data...</p>
                        <p className="text-gray-400 text-sm">Fetching real-time prices</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4 p-4 bg-gray-800/50 rounded-lg">
                      <AgentRippleLoader size="small" showMessage={false} />
                      <div>
                        <p className="text-white font-medium">AI agent analyzing...</p>
                        <p className="text-gray-400 text-sm">Finding arbitrage opportunities</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4 p-4 bg-gray-800/50 rounded-lg">
                      <TransactionRippleLoader size="small" showMessage={false} />
                      <div>
                        <p className="text-white font-medium">Executing trade...</p>
                        <p className="text-gray-400 text-sm">Broadcasting to blockchain</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-white">Modal & Overlay States</h3>
                  <div className="bg-gray-800/30 rounded-lg p-8 border border-gray-700">
                    <div className="text-center">
                      <SystemRippleLoader 
                        size="large" 
                        message="Connecting to Networks..."
                        subMessage="Ethereum, Base, Arbitrum"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
