"use client";

import { useEffect, useRef } from "react";
import Lottie, { LottieRefCurrentProps } from "lottie-react";
import { motion } from "framer-motion";
import rippleAnimation from "@/public/animations/ripple-loading.json";

export type RippleTheme = 
  | 'system'      // Multi-color for system initialization
  | 'agent'       // Purple/pink for AI processing
  | 'data'        // Blue/cyan for data loading
  | 'transaction' // Green/gold for trade execution
  | 'error'       // Red for errors
  | 'success';    // Green for success

export type RippleSize = 'small' | 'medium' | 'large' | 'xl';

interface RippleLoaderProps {
  theme?: RippleTheme;
  size?: RippleSize;
  speed?: number;
  message?: string;
  subMessage?: string;
  className?: string;
  showMessage?: boolean;
}

export function RippleLoader({
  theme = 'system',
  size = 'medium',
  speed = 1,
  message,
  subMessage,
  className = '',
  showMessage = true
}: RippleLoaderProps) {
  const lottieRef = useRef<LottieRefCurrentProps>(null);

  useEffect(() => {
    if (lottieRef.current) {
      lottieRef.current.setSpeed(speed);
    }
  }, [speed]);

  const getSizeClasses = () => {
    switch (size) {
      case 'small': return 'w-16 h-16';
      case 'medium': return 'w-24 h-24';
      case 'large': return 'w-32 h-32';
      case 'xl': return 'w-48 h-48';
      default: return 'w-24 h-24';
    }
  };

  const getThemeClasses = () => {
    switch (theme) {
      case 'system':
        return {
          container: 'bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-green-900/20',
          text: 'text-white',
          subText: 'text-gray-300',
          glow: 'shadow-lg shadow-blue-500/20'
        };
      case 'agent':
        return {
          container: 'bg-gradient-to-br from-purple-900/20 to-pink-900/20',
          text: 'text-purple-200',
          subText: 'text-purple-300',
          glow: 'shadow-lg shadow-purple-500/20'
        };
      case 'data':
        return {
          container: 'bg-gradient-to-br from-blue-900/20 to-cyan-900/20',
          text: 'text-blue-200',
          subText: 'text-blue-300',
          glow: 'shadow-lg shadow-blue-500/20'
        };
      case 'transaction':
        return {
          container: 'bg-gradient-to-br from-green-900/20 to-yellow-900/20',
          text: 'text-green-200',
          subText: 'text-green-300',
          glow: 'shadow-lg shadow-green-500/20'
        };
      case 'error':
        return {
          container: 'bg-gradient-to-br from-red-900/20 to-orange-900/20',
          text: 'text-red-200',
          subText: 'text-red-300',
          glow: 'shadow-lg shadow-red-500/20'
        };
      case 'success':
        return {
          container: 'bg-gradient-to-br from-green-900/20 to-emerald-900/20',
          text: 'text-green-200',
          subText: 'text-green-300',
          glow: 'shadow-lg shadow-green-500/20'
        };
      default:
        return {
          container: 'bg-gray-900/20',
          text: 'text-white',
          subText: 'text-gray-300',
          glow: 'shadow-lg shadow-gray-500/20'
        };
    }
  };

  const getDefaultMessage = () => {
    switch (theme) {
      case 'system': return 'Initializing ATOM...';
      case 'agent': return 'AI Processing...';
      case 'data': return 'Loading Data...';
      case 'transaction': return 'Executing Trade...';
      case 'error': return 'Error Occurred';
      case 'success': return 'Success!';
      default: return 'Loading...';
    }
  };

  const getDefaultSubMessage = () => {
    switch (theme) {
      case 'system': return 'Preparing the ultimate arbitrage system';
      case 'agent': return 'AI agents are analyzing opportunities';
      case 'data': return 'Fetching real-time market data';
      case 'transaction': return 'Processing blockchain transaction';
      case 'error': return 'Please try again';
      case 'success': return 'Operation completed successfully';
      default: return 'Please wait...';
    }
  };

  const themeClasses = getThemeClasses();
  const displayMessage = message || getDefaultMessage();
  const displaySubMessage = subMessage || getDefaultSubMessage();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.3 }}
      className={`flex flex-col items-center justify-center p-8 rounded-2xl ${themeClasses.container} ${themeClasses.glow} ${className}`}
    >
      {/* Ripple Animation */}
      <motion.div
        animate={{ 
          rotate: [0, 360],
          scale: [1, 1.05, 1]
        }}
        transition={{ 
          rotate: { duration: 20, repeat: Infinity, ease: "linear" },
          scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
        }}
        className={`${getSizeClasses()} mb-6`}
      >
        <Lottie
          lottieRef={lottieRef}
          animationData={rippleAnimation}
          loop={true}
          autoplay={true}
          style={{
            width: '100%',
            height: '100%',
            filter: `hue-rotate(${getHueRotation()}deg) saturate(${getSaturation()})`
          }}
        />
      </motion.div>

      {/* Loading Messages */}
      {showMessage && (
        <div className="text-center space-y-2">
          <motion.h3
            animate={{ opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            className={`text-lg font-semibold ${themeClasses.text}`}
          >
            {displayMessage}
          </motion.h3>
          
          {displaySubMessage && (
            <motion.p
              animate={{ opacity: [0.5, 0.8, 0.5] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
              className={`text-sm ${themeClasses.subText}`}
            >
              {displaySubMessage}
            </motion.p>
          )}
        </div>
      )}

      {/* Animated Dots */}
      <motion.div
        className="flex space-x-1 mt-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className={`w-2 h-2 rounded-full ${theme === 'system' ? 'bg-blue-400' : 
              theme === 'agent' ? 'bg-purple-400' :
              theme === 'data' ? 'bg-blue-400' :
              theme === 'transaction' ? 'bg-green-400' :
              theme === 'error' ? 'bg-red-400' :
              'bg-green-400'
            }`}
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: i * 0.2,
              ease: "easeInOut"
            }}
          />
        ))}
      </motion.div>
    </motion.div>
  );

  function getHueRotation(): number {
    switch (theme) {
      case 'system': return 0;     // Original colors
      case 'agent': return 280;    // Purple/pink
      case 'data': return 200;     // Blue/cyan
      case 'transaction': return 120; // Green/yellow
      case 'error': return 0;      // Red (close to original)
      case 'success': return 120;  // Green
      default: return 0;
    }
  }

  function getSaturation(): number {
    switch (theme) {
      case 'system': return 1.2;
      case 'agent': return 1.4;
      case 'data': return 1.3;
      case 'transaction': return 1.5;
      case 'error': return 1.6;
      case 'success': return 1.4;
      default: return 1.0;
    }
  }
}

// Preset components for common use cases
export function SystemRippleLoader(props: Omit<RippleLoaderProps, 'theme'>) {
  return <RippleLoader {...props} theme="system" />;
}

export function AgentRippleLoader(props: Omit<RippleLoaderProps, 'theme'>) {
  return <RippleLoader {...props} theme="agent" />;
}

export function DataRippleLoader(props: Omit<RippleLoaderProps, 'theme'>) {
  return <RippleLoader {...props} theme="data" />;
}

export function TransactionRippleLoader(props: Omit<RippleLoaderProps, 'theme'>) {
  return <RippleLoader {...props} theme="transaction" />;
}

export function ErrorRippleLoader(props: Omit<RippleLoaderProps, 'theme'>) {
  return <RippleLoader {...props} theme="error" />;
}

export function SuccessRippleLoader(props: Omit<RippleLoaderProps, 'theme'>) {
  return <RippleLoader {...props} theme="success" />;
}
