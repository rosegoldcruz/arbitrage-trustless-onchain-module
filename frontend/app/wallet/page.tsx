'use client';

/**
 * Wallet Demo Page
 * Showcase MetaMask integration and Web3 functionality
 * Following AEON platform standards and Vercel best practices
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

import { useWeb3Auth } from '@/components/web3/web3auth-provider';
import { 
  Wallet, 
  Network, 
  Coins, 
  Shield, 
  CheckCircle2, 
  AlertTriangle,
  ExternalLink 
} from 'lucide-react';
import Link from 'next/link';

export default function WalletPage() {
  const {
    isConnected,
    address,
    chainId,
    balance,
    isCorrectNetwork
  } = useWeb3Auth();

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Wallet Integration
              </h1>
              <p className="text-gray-400 mt-2">
                Connect your MetaMask wallet to start using ATOM
              </p>
            </div>
            <Link href="/dashboard">
              <Button variant="outline" className="border-gray-700">
                Back to Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Connection Panel */}
          <div className="space-y-6">
            <Card className="bg-gray-900/50 border-gray-800">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Wallet className="h-5 w-5" />
                  <span>Wallet Connection</span>
                </CardTitle>
                <CardDescription>
                  Connect your MetaMask wallet to interact with ATOM
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-400 mb-4">
                  Use Web3Auth to connect your wallet securely.
                </p>
                <Button
                  onClick={() => window.location.href = '/dashboard'}
                  className="w-full"
                >
                  Go to Dashboard to Connect
                </Button>
              </CardContent>
            </Card>

            {/* Network Status */}
            {isConnected && (
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Network className="h-5 w-5" />
                    <span>Network Status</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Current Network:</span>
                    <div className="flex items-center space-x-2">
                      {isCorrectNetwork ? (
                        <>
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                          <Badge variant="secondary" className="bg-green-500/20 text-green-400">
                            Base Sepolia
                          </Badge>
                        </>
                      ) : (
                        <>
                          <AlertTriangle className="h-4 w-4 text-yellow-500" />
                          <Badge variant="destructive">
                            Wrong Network
                          </Badge>
                        </>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Chain ID:</span>
                    <span className="font-mono text-sm">
                      {chainId || 'Not connected'}
                    </span>
                  </div>

                  {isCorrectNetwork && (
                    <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                      <div className="flex items-center space-x-2 text-green-400">
                        <Shield className="h-4 w-4" />
                        <span className="text-sm font-medium">
                          Ready for ATOM operations
                        </span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Account Information */}
          <div className="space-y-6">
            {isConnected ? (
              <>
                <Card className="bg-gray-900/50 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Coins className="h-5 w-5" />
                      <span>Account Details</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm text-gray-400">Wallet Address</label>
                      <div className="mt-1 p-3 bg-gray-800 rounded-lg font-mono text-sm break-all">
                        {address}
                      </div>
                    </div>

                    <div>
                      <label className="text-sm text-gray-400">ETH Balance</label>
                      <div className="mt-1 p-3 bg-gray-800 rounded-lg">
                        <span className="text-2xl font-bold">
                          {balance || '0.0000'} ETH
                        </span>
                      </div>
                    </div>

                    <Button
                      onClick={() => window.open(`https://sepolia-explorer.base.org/address/${address}`, '_blank')}
                      variant="outline"
                      className="w-full border-gray-700"
                    >
                      <ExternalLink className="mr-2 h-4 w-4" />
                      View on Base Sepolia Explorer
                    </Button>
                  </CardContent>
                </Card>

                {/* Features Available */}
                <Card className="bg-gray-900/50 border-gray-800">
                  <CardHeader>
                    <CardTitle>Available Features</CardTitle>
                    <CardDescription>
                      What you can do with your connected wallet
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center space-x-3">
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                      <span>Execute flash loan arbitrage</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                      <span>Monitor arbitrage opportunities</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                      <span>Configure trading parameters</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                      <span>View transaction history</span>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle>Connect to Get Started</CardTitle>
                  <CardDescription>
                    Connect your wallet to access all ATOM features
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8">
                    <Wallet className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400">
                      Your account details will appear here once connected
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Next Steps */}
        {isConnected && isCorrectNetwork && (
          <div className="mt-8">
            <Card className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/20">
              <CardHeader>
                <CardTitle className="text-blue-400">Ready to Start Trading!</CardTitle>
                <CardDescription>
                  Your wallet is connected and configured. Start exploring ATOM's features.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-4">
                  <Link href="/dashboard">
                    <Button className="bg-blue-600 hover:bg-blue-700">
                      Go to Dashboard
                    </Button>
                  </Link>
                  <Link href="/settings">
                    <Button variant="outline" className="border-gray-700">
                      Configure Settings
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
