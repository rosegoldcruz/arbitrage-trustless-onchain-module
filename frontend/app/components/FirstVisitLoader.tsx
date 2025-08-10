'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { SystemRippleLoader } from '@/components/ui/RippleLoader'

interface FirstVisitLoaderProps {
  children: React.ReactNode
}

export default function FirstVisitLoader({ children }: FirstVisitLoaderProps) {
  const [isFirstVisit, setIsFirstVisit] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [currentStep, setCurrentStep] = useState(0)

  const loadingSteps = [
    'Initializing ATOM System...',
    'Connecting to Base Network...',
    'Loading Arbitrage Modules...',
    'Preparing Interface...'
  ]

  useEffect(() => {
    // Check if this is the first visit
    const hasVisited = localStorage.getItem('atom-visited')
    
    if (!hasVisited) {
      // First visit - show loading screen
      setIsFirstVisit(true)
      localStorage.setItem('atom-visited', 'true')
      
      // Simulate loading steps
      const stepInterval = setInterval(() => {
        setCurrentStep(prev => {
          if (prev < loadingSteps.length - 1) {
            return prev + 1
          } else {
            clearInterval(stepInterval)
            // Complete loading after final step
            setTimeout(() => {
              setIsLoading(false)
            }, 1000)
            return prev
          }
        })
      }, 800)

      return () => clearInterval(stepInterval)
    } else {
      // Not first visit - skip loading
      setIsFirstVisit(false)
      setIsLoading(false)
    }
  }, [])

  if (!isFirstVisit || !isLoading) {
    return <>{children}</>
  }

  return (
    <AnimatePresence>
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 1.1 }}
          transition={{ duration: 0.8 }}
          className="fixed inset-0 bg-black flex items-center justify-center z-50"
        >
          {/* Animated Background */}
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-green-900/20" />
            
            {/* Floating Particles */}
            {[...Array(15)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-blue-400 rounded-full opacity-30"
                animate={{
                  x: [0, Math.random() * 100 - 50],
                  y: [0, Math.random() * 100 - 50],
                  scale: [0, 1, 0],
                }}
                transition={{
                  duration: 3 + Math.random() * 2,
                  repeat: Infinity,
                  delay: Math.random() * 2,
                }}
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                }}
              />
            ))}
          </div>

          {/* Main Loading Content */}
          <div className="relative z-10 text-center max-w-md mx-auto px-6">
            {/* Ripple Animation */}
            <div className="mb-8">
              <SystemRippleLoader
                size="xl"
                speed={1.2}
                message={loadingSteps[currentStep]}
                subMessage="The Ultimate Arbitrage System"
                showMessage={false}
              />
            </div>

            {/* ATOM Logo */}
            <motion.div
              animate={{
                scale: [1, 1.05, 1]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="text-6xl mb-4"
            >
              ⚛️
            </motion.div>

            {/* Title */}
            <motion.h1
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"
            >
              ATOM
            </motion.h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-gray-400 mb-6"
            >
              Arbitrage Trustless On-Chain Module
            </motion.p>

            {/* Loading Step Text */}
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-white/80 text-lg font-medium mb-4"
            >
              {loadingSteps[currentStep]}
            </motion.div>

            {/* Progress Dots */}
            <div className="flex justify-center space-x-2">
              {loadingSteps.map((_, i) => (
                <motion.div
                  key={i}
                  className={`w-2 h-2 rounded-full ${
                    i <= currentStep ? 'bg-blue-400' : 'bg-gray-600'
                  }`}
                  animate={i === currentStep ? {
                    scale: [1, 1.3, 1],
                    opacity: [0.7, 1, 0.7]
                  } : {}}
                  transition={{
                    duration: 1,
                    repeat: i === currentStep ? Infinity : 0,
                  }}
                />
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
