'use client'

import { useAccount, useConnect, useDisconnect, useSwitchChain, useBalance } from 'wagmi'
import { baseSepolia } from 'wagmi/chains'
import { toast } from 'sonner'
import { isCorrectNetwork, getChainName } from '@/lib/wagmi-config'

export function useWallet() {
  const { address, isConnected, chainId } = useAccount()
  const { connect, connectors, isPending: isConnecting } = useConnect()
  const { disconnect } = useDisconnect()
  const { switchChain } = useSwitchChain()
  const { data: balance } = useBalance({
    address,
    chainId: baseSepolia.id
  })
  
  const isCorrectNet = isCorrectNetwork(chainId)
  
  // Connect to wallet
  const connectWallet = async (connectorId?: string) => {
    try {
      const connector = connectorId 
        ? connectors.find(c => c.id === connectorId)
        : connectors[0] // Default to first connector (WalletConnect)
      
      if (!connector) {
        toast.error('No wallet connector found')
        return false
      }
      
      connect({ connector })
      return true
    } catch (error) {
      console.error('Failed to connect wallet:', error)
      toast.error('Failed to connect wallet')
      return false
    }
  }
  
  // Switch to Base Sepolia
  const switchToBaseSepolia = async () => {
    try {
      if (!isConnected) {
        toast.error('Please connect your wallet first')
        return false
      }
      
      await switchChain({ chainId: baseSepolia.id })
      toast.success('Switched to Base Sepolia')
      return true
    } catch (error) {
      console.error('Failed to switch network:', error)
      toast.error('Failed to switch to Base Sepolia')
      return false
    }
  }
  
  // Disconnect wallet
  const disconnectWallet = () => {
    try {
      disconnect()
      toast.success('Wallet disconnected')
    } catch (error) {
      console.error('Failed to disconnect wallet:', error)
      toast.error('Failed to disconnect wallet')
    }
  }
  
  // Format address for display
  const formatAddress = (addr?: string) => {
    if (!addr) return ''
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`
  }
  
  // Format balance for display
  const formatBalance = () => {
    if (!balance) return '0.0000'
    return parseFloat(balance.formatted).toFixed(4)
  }
  
  return {
    // State
    address,
    isConnected,
    chainId,
    isCorrectNetwork: isCorrectNet,
    isConnecting,
    balance: balance?.formatted,
    formattedBalance: formatBalance(),
    formattedAddress: formatAddress(address),
    chainName: getChainName(chainId),
    
    // Actions
    connectWallet,
    disconnectWallet,
    switchToBaseSepolia,
    
    // Available connectors
    connectors,
    
    // Utilities
    formatAddress,
  }
}
