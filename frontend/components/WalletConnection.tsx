"use client";

import React from 'react';
import { useUser } from '@clerk/nextjs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Wallet, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react';
import { useWeb3 } from '@/lib/web3-context';

export default function WalletConnection() {
  const { user, isLoaded } = useUser();
  const { isConnected, address, chainId } = useWeb3();

  if (!isLoaded) {
    return (
      <Card className="bg-gray-900/50 border-gray-700">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!user) {
    return (
      <Card className="bg-gray-900/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Wallet className="h-5 w-5" />
            Wallet Connection
          </CardTitle>
          <CardDescription>
            Sign in to connect your Web3 wallet
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const web3Wallets = user.web3Wallets || [];
  const hasConnectedWallet = web3Wallets.length > 0;

  return (
    <Card className="bg-gray-900/50 border-gray-700">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Wallet className="h-5 w-5" />
          Wallet Connection
        </CardTitle>
        <CardDescription>
          {hasConnectedWallet 
            ? "Your Web3 wallet is connected" 
            : "Connect your Web3 wallet to access trading features"
          }
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {hasConnectedWallet ? (
          <div className="space-y-3">
            {web3Wallets.map((wallet, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <div>
                    <p className="text-white font-medium">
                      {wallet.web3Wallet.slice(0, 6)}...{wallet.web3Wallet.slice(-4)}
                    </p>
                    <p className="text-sm text-gray-400">
                      Connected via Clerk
                    </p>
                  </div>
                </div>
                <Badge variant="default" className="bg-green-600">
                  Connected
                </Badge>
              </div>
            ))}
            
            {chainId && (
              <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <div>
                    <p className="text-white font-medium">Network</p>
                    <p className="text-sm text-gray-400">
                      {chainId === 84532 ? 'Base Sepolia' : `Chain ID: ${chainId}`}
                    </p>
                  </div>
                </div>
                <Badge variant="outline" className="border-blue-500 text-blue-400">
                  {chainId === 84532 ? 'Testnet' : 'Unknown'}
                </Badge>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-3 bg-yellow-900/20 border border-yellow-700 rounded-lg">
              <AlertCircle className="h-5 w-5 text-yellow-500" />
              <div>
                <p className="text-yellow-200 font-medium">No wallet connected</p>
                <p className="text-sm text-yellow-300/70">
                  Connect a Web3 wallet to access trading features
                </p>
              </div>
            </div>
            
            <div className="space-y-2">
              <p className="text-sm text-gray-400">Supported wallets:</p>
              <div className="grid grid-cols-1 gap-2">
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  MetaMask
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  Coinbase Wallet
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <div className="w-2 h-2 bg-black rounded-full"></div>
                  OKX Wallet
                </div>
              </div>
            </div>
            
            <Button 
              onClick={() => {
                // Open user profile to manage Web3 wallets
                window.open('/user-profile', '_blank');
              }}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Manage Wallets in Profile
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
