"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { SystemRippleLoader } from "@/components/ui/RippleLoader";
import {
  Rocket,
  Zap,
  Target,
  Brain,
  Shield,
  Crown,
  Sparkles,
  Flame
} from "lucide-react";

interface LoadingStep {
  id: string;
  text: string;
  icon: React.ReactNode;
  duration: number;
  color: string;
}

export function EpicLoadingScreen({ onComplete }: { onComplete: () => void }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  const loadingSteps: LoadingStep[] = [
    {
      id: 'init',
      text: 'Initializing ATOM Core Systems...',
      icon: <Rocket className="h-8 w-8" />,
      duration: 1000,
      color: 'from-blue-500 to-cyan-500'
    },
    {
      id: 'agents',
      text: 'Awakening AI Agents...',
      icon: <Brain className="h-8 w-8" />,
      duration: 1200,
      color: 'from-purple-500 to-pink-500'
    },
    {
      id: 'blockchain',
      text: 'Connecting to Blockchain Networks...',
      icon: <Zap className="h-8 w-8" />,
      duration: 800,
      color: 'from-green-500 to-emerald-500'
    },
    {
      id: 'opportunities',
      text: 'Scanning for Arbitrage Opportunities...',
      icon: <Target className="h-8 w-8" />,
      duration: 1500,
      color: 'from-orange-500 to-red-500'
    },
    {
      id: 'security',
      text: 'Activating MEV Protection...',
      icon: <Shield className="h-8 w-8" />,
      duration: 900,
      color: 'from-indigo-500 to-purple-500'
    },
    {
      id: 'ready',
      text: 'ATOM is Ready to Dominate!',
      icon: <Crown className="h-8 w-8" />,
      duration: 1000,
      color: 'from-yellow-500 to-orange-500'
    }
  ];

  useEffect(() => {
    const totalSteps = loadingSteps.length;
    let stepIndex = 0;
    let stepProgress = 0;

    const interval = setInterval(() => {
      const currentStepData = loadingSteps[stepIndex];
      stepProgress += 50; // Increment progress

      if (stepProgress >= currentStepData.duration) {
        stepIndex++;
        stepProgress = 0;
        setCurrentStep(stepIndex);
      }

      // Calculate overall progress
      const overallProgress = ((stepIndex * 100) + (stepProgress / currentStepData.duration * 100)) / totalSteps;
      setProgress(overallProgress);

      if (stepIndex >= totalSteps) {
        setIsComplete(true);
        setTimeout(() => {
          onComplete();
        }, 1000);
        clearInterval(interval);
      }
    }, 50);

    return () => clearInterval(interval);
  }, [onComplete]);

  if (isComplete) {
    return (
      <motion.div
        initial={{ opacity: 1 }}
        exit={{ opacity: 0, scale: 1.1 }}
        transition={{ duration: 0.8 }}
        className="fixed inset-0 bg-black flex items-center justify-center z-50"
      >
        <motion.div
          initial={{ scale: 1 }}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, ease: "easeInOut" }}
            className="text-8xl mb-4"
          >
            🚀
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent"
          >
            ATOM IS LIVE!
          </motion.h1>
        </motion.div>
      </motion.div>
    );
  }

  const currentStepData = loadingSteps[currentStep] || loadingSteps[0];

  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center z-50">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-green-900/20" />
        
        {/* Floating Particles */}
        {[...Array(20)].map((_, i) => (
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
        {/* Epic Ripple Animation */}
        <div className="mb-8">
          <SystemRippleLoader
            size="xl"
            speed={1.2}
            message={currentStepData.text}
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
          className="text-gray-400 mb-12 text-lg"
        >
          The Ultimate Arbitrage System
        </motion.p>

        {/* Current Step */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="mb-8"
          >
            <div className={`inline-flex items-center space-x-3 px-6 py-3 rounded-full bg-gradient-to-r ${currentStepData.color} bg-opacity-20 border border-current border-opacity-30`}>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="text-white"
              >
                {currentStepData.icon}
              </motion.div>
              <span className="text-white font-medium">
                {currentStepData.text}
              </span>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>Loading...</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-3 overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-green-500"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Loading Steps Indicator */}
        <div className="flex justify-center space-x-2">
          {loadingSteps.map((step, index) => (
            <motion.div
              key={step.id}
              className={`w-3 h-3 rounded-full ${
                index <= currentStep 
                  ? 'bg-gradient-to-r from-blue-500 to-purple-500' 
                  : 'bg-gray-700'
              }`}
              animate={index === currentStep ? { scale: [1, 1.3, 1] } : {}}
              transition={{ duration: 0.5, repeat: Infinity }}
            />
          ))}
        </div>

        {/* Fun Loading Messages */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
          className="mt-8 text-gray-500 text-sm"
        >
          <motion.p
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            🔥 Preparing to make you rich... 💰
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
}
