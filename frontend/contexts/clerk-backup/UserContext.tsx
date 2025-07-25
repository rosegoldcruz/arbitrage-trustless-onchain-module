'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useUser } from '@clerk/nextjs'
import { useAccount, useDisconnect } from 'wagmi'
import { createClient } from '@supabase/supabase-js'

// Supabase client
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || '',
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
)

interface UserContextType {
  // Clerk user data
  clerkUser: any
  isClerkLoaded: boolean
  isClerkSignedIn: boolean
  
  // Wallet data
  walletAddress: string | undefined
  isWalletConnected: boolean
  chainId: number | undefined
  
  // Combined state
  isFullyAuthenticated: boolean
  
  // Actions
  syncWalletToSupabase: () => Promise<void>
  disconnectWallet: () => void
}

const UserContext = createContext<UserContextType | undefined>(undefined)

interface UserProviderProps {
  children: ReactNode
}

export function UserProvider({ children }: UserProviderProps) {
  const { user: clerkUser, isLoaded: isClerkLoaded, isSignedIn: isClerkSignedIn } = useUser()
  const { address: walletAddress, isConnected: isWalletConnected, chainId } = useAccount()
  const { disconnect } = useDisconnect()
  
  const [isSyncing, setIsSyncing] = useState(false)
  
  // User is fully authenticated when both Clerk and wallet are connected
  const isFullyAuthenticated = Boolean(isClerkSignedIn && isWalletConnected && walletAddress)
  
  // Sync wallet address to Supabase when wallet connects
  const syncWalletToSupabase = async () => {
    if (!clerkUser || !walletAddress || isSyncing) return
    
    setIsSyncing(true)
    try {
      // Update or insert user record with wallet address
      const { error } = await supabase
        .from('users')
        .upsert({
          id: clerkUser.id,
          email: clerkUser.emailAddresses[0]?.emailAddress,
          wallet_address: walletAddress.toLowerCase(),
          updated_at: new Date().toISOString()
        }, {
          onConflict: 'id'
        })
      
      if (error) {
        console.error('Error syncing wallet to Supabase:', error)
      } else {
        console.log('✅ Wallet synced to Supabase:', walletAddress)
      }
    } catch (error) {
      console.error('Error syncing wallet:', error)
    } finally {
      setIsSyncing(false)
    }
  }
  
  // Auto-sync when wallet connects and user is signed in
  useEffect(() => {
    if (isFullyAuthenticated && !isSyncing) {
      syncWalletToSupabase()
    }
  }, [isFullyAuthenticated, walletAddress, clerkUser?.id])
  
  // Disconnect wallet function
  const disconnectWallet = () => {
    disconnect()
  }
  
  const contextValue: UserContextType = {
    clerkUser,
    isClerkLoaded,
    isClerkSignedIn: isClerkSignedIn || false,
    walletAddress,
    isWalletConnected,
    chainId,
    isFullyAuthenticated,
    syncWalletToSupabase,
    disconnectWallet
  }
  
  return (
    <UserContext.Provider value={contextValue}>
      {children}
    </UserContext.Provider>
  )
}

export function useUserContext() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error('useUserContext must be used within a UserProvider')
  }
  return context
}
