'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import Web3AuthButton from '@/components/web3/Web3AuthButton'
import { useWeb3Auth } from '@/contexts/Web3AuthContext'
import { 
  Home, 
  BarChart3, 
  Settings, 
  Monitor,
  Zap,
  CheckCircle2,
  AlertTriangle,
  User
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Arbitrage', href: '/arbitrage', icon: Zap },
  { name: 'Monitor', href: '/monitor', icon: Monitor },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Navbar() {
  const pathname = usePathname()
  const { 
    isConnected, 
    isCorrectNetwork,
    userInfo,
    address 
  } = useWeb3Auth()
  
  return (
    <nav className="bg-black/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                ATOM
              </span>
            </Link>
          </div>
          
          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </div>
          
          {/* Auth & Status Section */}
          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <Badge variant="default" className="bg-green-600 text-white">
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  {isCorrectNetwork ? 'Connected' : 'Wrong Network'}
                </Badge>
              ) : (
                <Badge variant="outline" className="border-gray-600 text-gray-400">
                  Not Connected
                </Badge>
              )}
            </div>
            
            {/* User Info (when connected) */}
            {isConnected && userInfo && (
              <div className="hidden sm:flex items-center space-x-2 text-sm text-gray-300">
                <User className="h-4 w-4" />
                <span>{userInfo.name || userInfo.email}</span>
              </div>
            )}
            
            {/* Web3Auth Button */}
            <Web3AuthButton size="sm" />
          </div>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      <div className="md:hidden border-t border-gray-800">
        <div className="px-2 pt-2 pb-3 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`block px-3 py-2 rounded-md text-base font-medium transition-colors flex items-center space-x-2 ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.name}</span>
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
