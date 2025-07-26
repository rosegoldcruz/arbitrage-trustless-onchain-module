"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Shield, Zap, Wallet, ArrowRight, CheckCircle2 } from "lucide-react";
import Web3AuthButton from "@/components/web3/Web3AuthButton";
import { useWeb3Auth } from "@/components/web3/web3auth-provider";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export function LoginSection() {
  const { isConnected, address, balance, userInfo } = useWeb3Auth();

  return (
    <section id="login" className="py-20 bg-gradient-to-br from-gray-900 via-black to-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-4xl md:text-5xl font-bold mb-6"
          >
            {isConnected ? (
              <span className="bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
                Welcome Back!
              </span>
            ) : (
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Connect Your Wallet
              </span>
            )}
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-xl text-gray-300 max-w-3xl mx-auto"
          >
            {isConnected 
              ? "You're connected and ready to start earning with ATOM's AI-powered arbitrage bots."
              : "Get started with ATOM in seconds. Connect your wallet to access the most advanced DeFi arbitrage platform."
            }
          </motion.p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left side - Login/Connection */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-8"
          >
            <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
              <CardHeader className="text-center">
                <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
                  <Wallet className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-2xl text-white">
                  {isConnected ? "Wallet Connected" : "Connect Wallet"}
                </CardTitle>
                <CardDescription className="text-gray-300">
                  {isConnected 
                    ? "Your wallet is connected and ready to use"
                    : "Secure, fast, and easy wallet connection with Web3Auth"
                  }
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {isConnected ? (
                  // Connected state
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                      <CheckCircle2 className="h-5 w-5 text-green-400" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-green-400">Connected</p>
                        <p className="text-xs text-gray-400 font-mono">
                          {address?.slice(0, 6)}...{address?.slice(-4)}
                        </p>
                      </div>
                    </div>
                    
                    {userInfo && (
                      <div className="p-4 bg-gray-700/30 rounded-lg">
                        <p className="text-sm text-gray-300">
                          <span className="font-medium">Account:</span> {userInfo.name || userInfo.email}
                        </p>
                        <p className="text-sm text-gray-300">
                          <span className="font-medium">Balance:</span> {balance || '0.0000'} ETH
                        </p>
                      </div>
                    )}

                    <Link href="/dashboard" className="block">
                      <Button className="w-full bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white">
                        Go to Dashboard
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                ) : (
                  // Not connected state
                  <div className="space-y-6">
                    <div className="text-center">
                      <Web3AuthButton 
                        className="w-full text-lg py-6" 
                        size="lg"
                      />
                    </div>
                    
                    <div className="text-center text-sm text-gray-400">
                      <p>Supports Google, Discord, Twitter, and more</p>
                      <p className="mt-1">No seed phrases required</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Right side - Benefits */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-6"
          >
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="bg-blue-500/20 p-3 rounded-lg">
                  <Shield className="h-6 w-6 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Secure & Private</h3>
                  <p className="text-gray-300">
                    Your keys, your crypto. Web3Auth provides enterprise-grade security with social login convenience.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="bg-purple-500/20 p-3 rounded-lg">
                  <Zap className="h-6 w-6 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Instant Access</h3>
                  <p className="text-gray-300">
                    Connect in seconds and start earning immediately. No complex setup or technical knowledge required.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="bg-green-500/20 p-3 rounded-lg">
                  <CheckCircle2 className="h-6 w-6 text-green-400" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Ready to Earn</h3>
                  <p className="text-gray-300">
                    Once connected, you'll have immediate access to ATOM's AI agents and arbitrage opportunities.
                  </p>
                </div>
              </div>
            </div>

            {!isConnected && (
              <div className="mt-8 p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-lg">
                <h4 className="text-lg font-semibold text-white mb-2">What happens after connecting?</h4>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="h-4 w-4 text-green-400" />
                    <span>Access your personalized dashboard</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="h-4 w-4 text-green-400" />
                    <span>Configure AI arbitrage bots</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="h-4 w-4 text-green-400" />
                    <span>Start earning risk-free profits</span>
                  </li>
                </ul>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
