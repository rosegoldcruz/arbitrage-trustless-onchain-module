"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useUser } from '@clerk/nextjs';

interface Web3ContextType {
  isConnected: boolean;
  address: string | null;
  chainId: number | null;
  connectWallet: () => Promise<void>;
  disconnectWallet: () => Promise<void>;
  switchChain: (chainId: number) => Promise<void>;
}

const Web3Context = createContext<Web3ContextType | undefined>(undefined);

export function Web3Provider({ children }: { children: React.ReactNode }) {
  const { user, isLoaded } = useUser();
  const [isConnected, setIsConnected] = useState(false);
  const [address, setAddress] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);

  useEffect(() => {
    if (isLoaded && user) {
      // Check if user has connected Web3 wallets through Clerk
      const web3Wallets = user.web3Wallets;
      if (web3Wallets && web3Wallets.length > 0) {
        const primaryWallet = web3Wallets[0];
        setIsConnected(true);
        setAddress(primaryWallet.web3Wallet);
        // Base Sepolia chain ID
        setChainId(84532);
      }
    }
  }, [user, isLoaded]);

  const connectWallet = async () => {
    try {
      // Clerk handles wallet connection through their UI components
      // This function can trigger the Clerk sign-in modal with Web3 options
      console.log('Wallet connection handled by Clerk authentication');
    } catch (error) {
      console.error('Failed to connect wallet:', error);
    }
  };

  const disconnectWallet = async () => {
    try {
      setIsConnected(false);
      setAddress(null);
      setChainId(null);
    } catch (error) {
      console.error('Failed to disconnect wallet:', error);
    }
  };

  const switchChain = async (targetChainId: number) => {
    try {
      if (window.ethereum) {
        await window.ethereum.request({
          method: 'wallet_switchEthereumChain',
          params: [{ chainId: `0x${targetChainId.toString(16)}` }],
        });
        setChainId(targetChainId);
      }
    } catch (error) {
      console.error('Failed to switch chain:', error);
    }
  };

  const value: Web3ContextType = {
    isConnected,
    address,
    chainId,
    connectWallet,
    disconnectWallet,
    switchChain,
  };

  return (
    <Web3Context.Provider value={value}>
      {children}
    </Web3Context.Provider>
  );
}

export function useWeb3() {
  const context = useContext(Web3Context);
  if (context === undefined) {
    throw new Error('useWeb3 must be used within a Web3Provider');
  }
  return context;
}

// Type declaration for window.ethereum
// declare global {
//   interface Window {
//     ethereum?: {
//       request: (args: { method: string; params?: any[] }) => Promise<any>;
//       on: (event: string, callback: (...args: any[]) => void) => void;
//       removeListener: (event: string, callback: (...args: any[]) => void) => void;
//     };
//   }
// }
