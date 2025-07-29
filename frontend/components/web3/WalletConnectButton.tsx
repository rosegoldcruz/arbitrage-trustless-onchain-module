'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useWeb3Auth } from '@/contexts/Web3AuthContext'
import { getExplorerUrl } from '@/lib/wagmi-config'
import { useWallet } from '@/hooks/useWallet'
// import { useUserContext } from '@/contexts/clerk-backup/UserContext'
import { 
  Wallet, 
  ChevronDown, 
  Copy, 
  ExternalLink, 
  LogOut,
  AlertTriangle,
  Loader2,
  CheckCircle2
} from 'lucide-react'
import { toast } from 'sonner'

interface WalletConnectButtonProps {
  className?: string
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'default' | 'sm' | 'lg'
}

export default function WalletConnectButton({ 
  className = '', 
  variant = 'outline',
  size = 'default'
}: WalletConnectButtonProps) {
  const {
    address,
    isConnected,
    chainId,
    isCorrectNetwork,
    isConnecting,
    formattedAddress,
    formattedBalance,
    chainName,
    connectWallet,
    disconnectWallet,
    switchToBaseSepolia,
    connectors
  } = useWallet()
  
  // Temporarily commenting out UserContext until file is created
  // const { isClerkSignedIn, isFullyAuthenticated } = useUserContext()
  const isClerkSignedIn = true // Temporary fallback
  const isFullyAuthenticated = true // Temporary fallback
  
  const copyAddress = async () => {
    if (address) {
      await navigator.clipboard.writeText(address)
      toast.success('Address copied to clipboard')
    }
  }
  
  const openExplorer = () => {
    if (address && chainId) {
      window.open(getExplorerUrl(chainId, address), '_blank')
    }
  }
  
  const handleConnect = async () => {
    if (!isClerkSignedIn) {
      toast.error('Please sign in with Clerk first')
      return
    }
    
    try {
      await connectWallet()
    } catch (error) {
      console.error('Failed to connect wallet:', error)
      toast.error('Failed to connect wallet')
    }
  }
  
  const handleSwitchNetwork = async () => {
    try {
      await switchToBaseSepolia()
    } catch (error) {
      console.error('Failed to switch network:', error)
      toast.error('Failed to switch network')
    }
  }
  
  const handleDisconnect = () => {
    disconnectWallet()
  }
  
  // Show sign in message if Clerk not signed in
  if (!isClerkSignedIn) {
    return (
      <Button
        variant="ghost"
        disabled
        className={`text-gray-400 ${className}`}
        size={size}
      >
        <Wallet className="mr-2 h-4 w-4" />
        Sign in to connect wallet
      </Button>
    )
  }
  
  // Not connected state
  if (!isConnected) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant={variant}
            disabled={isConnecting}
            className={`bg-blue-600 hover:bg-blue-700 ${className}`}
            size={size}
          >
            {isConnecting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Connecting...
              </>
            ) : (
              <>
                <Wallet className="mr-2 h-4 w-4" />
                Connect Wallet
                <ChevronDown className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          {connectors.map((connector) => (
            <DropdownMenuItem
              key={connector.id}
              onClick={() => connectWallet(connector.id)}
              className="cursor-pointer"
            >
              <Wallet className="mr-2 h-4 w-4" />
              Connect with {connector.name}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    )
  }
  
  // Connected state
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant={variant}
          className={`border-gray-700 hover:border-gray-600 ${className}`}
          size={size}
        >
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                isCorrectNetwork ? 'bg-green-500' : 'bg-yellow-500'
              }`} />
              {isFullyAuthenticated && (
                <CheckCircle2 className="h-3 w-3 text-green-500" />
              )}
              <Wallet className="h-4 w-4" />
              <span className="font-mono text-sm">
                {formattedAddress}
              </span>
            </div>
            <ChevronDown className="h-4 w-4" />
          </div>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64">
        <div className="px-3 py-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Wallet Connected</span>
            <Badge variant={isCorrectNetwork ? "default" : "destructive"}>
              {chainName}
            </Badge>
          </div>
          <div className="mt-1 text-xs text-gray-400 font-mono">
            {address}
          </div>
          <div className="mt-1 text-xs text-gray-400">
            Balance: {formattedBalance} ETH
          </div>
        </div>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={copyAddress} className="cursor-pointer">
          <Copy className="mr-2 h-4 w-4" />
          Copy Address
        </DropdownMenuItem>
        
        <DropdownMenuItem onClick={openExplorer} className="cursor-pointer">
          <ExternalLink className="mr-2 h-4 w-4" />
          View on Explorer
        </DropdownMenuItem>
        
        {!isCorrectNetwork && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleSwitchNetwork} className="cursor-pointer text-yellow-600">
              <AlertTriangle className="mr-2 h-4 w-4" />
              Switch to Base Sepolia
            </DropdownMenuItem>
          </>
        )}
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={handleDisconnect} className="cursor-pointer text-red-600">
          <LogOut className="mr-2 h-4 w-4" />
          Disconnect
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}