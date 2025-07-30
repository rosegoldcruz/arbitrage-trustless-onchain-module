"use client";

// Force dynamic rendering to avoid SSG issues with Clerk
export const dynamic = 'force-dynamic';

import React from 'react';
import { useUser } from '@clerk/nextjs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import Navbar from '@/components/Navbar';
import WalletConnection from '@/components/WalletConnection';
import { useWeb3 } from '@/lib/web3-context';
import { Wallet, User, Shield, CheckCircle, AlertCircle } from 'lucide-react';

export default function WalletTestPage() {
  const { user, isLoaded } = useUser();
  const { isConnected, address, chainId } = useWeb3();

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
        <Navbar />
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Web3 Authentication Test
            </h1>
            <p className="text-gray-300">
              Test Clerk's Web3 wallet integration for ATOM platform
            </p>
          </div>

          {/* Authentication Status */}
          <Card className="bg-gray-900/50 border-gray-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <User className="h-5 w-5" />
                Authentication Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Clerk Authentication</span>
                <Badge variant={user ? "default" : "destructive"} className={user ? "bg-green-600" : "bg-red-600"}>
                  {user ? (
                    <>
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Authenticated
                    </>
                  ) : (
                    <>
                      <AlertCircle className="h-3 w-3 mr-1" />
                      Not Authenticated
                    </>
                  )}
                </Badge>
              </div>
              
              {user && (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">User ID</span>
                    <span className="text-white font-mono text-sm">
                      {user.id.slice(0, 8)}...{user.id.slice(-8)}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Email</span>
                    <span className="text-white">
                      {user.primaryEmailAddress?.emailAddress || 'No email'}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Web3 Wallets</span>
                    <Badge variant="outline" className="border-blue-500 text-blue-400">
                      {user.web3Wallets?.length || 0} connected
                    </Badge>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Web3 Context Status */}
          <Card className="bg-gray-900/50 border-gray-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Shield className="h-5 w-5" />
                Web3 Context Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Connection Status</span>
                <Badge variant={isConnected ? "default" : "destructive"} className={isConnected ? "bg-green-600" : "bg-red-600"}>
                  {isConnected ? 'Connected' : 'Disconnected'}
                </Badge>
              </div>
              
              {address && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Wallet Address</span>
                  <span className="text-white font-mono text-sm">
                    {address.slice(0, 6)}...{address.slice(-4)}
                  </span>
                </div>
              )}
              
              {chainId && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Chain ID</span>
                  <Badge variant="outline" className="border-blue-500 text-blue-400">
                    {chainId} {chainId === 84532 ? '(Base Sepolia)' : ''}
                  </Badge>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Wallet Connection Component */}
          <WalletConnection />

          {/* Debug Information */}
          {user && (
            <Card className="bg-gray-900/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Debug Information</CardTitle>
                <CardDescription>
                  Raw data for debugging purposes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="text-xs text-gray-300 bg-gray-800 p-4 rounded-lg overflow-auto">
                  {JSON.stringify({
                    userId: user.id,
                    web3Wallets: user.web3Wallets,
                    isConnected,
                    address,
                    chainId
                  }, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
