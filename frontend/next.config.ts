import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    optimizePackageImports: ['lucide-react', 'recharts'],
  },
  images: {
    domains: ['localhost', 'aeoninvestmentstechnologies.com'],
  },
  env: {
    NEXT_PUBLIC_ATOM_CONTRACT_ADDRESS: process.env.ATOM_CONTRACT_ADDRESS,
    NEXT_PUBLIC_TRIANGULAR_ARBITRAGE_ADDRESS: process.env.TRIANGULAR_ARBITRAGE_ADDRESS,
    NEXT_PUBLIC_PRICE_MONITOR_ADDRESS: process.env.PRICE_MONITOR_ADDRESS,
    NEXT_PUBLIC_DAI_ADDRESS: process.env.DAI_ADDRESS,
    NEXT_PUBLIC_USDC_ADDRESS: process.env.USDC_ADDRESS,
    NEXT_PUBLIC_WETH_ADDRESS: process.env.WETH_ADDRESS,
    NEXT_PUBLIC_POLYGON_RPC_URL: process.env.POLYGON_RPC_URL,
    NEXT_PUBLIC_CHAIN_ID: process.env.CHAIN_ID,
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE,
  },
  webpack: (config, { isServer }) => {
    // Fix for Web3Auth and MetaMask SDK React Native dependencies
    config.resolve.fallback = {
      ...config.resolve.fallback,
      '@react-native-async-storage/async-storage': false,
      'react-native': false,
      'react-native-fs': false,
      'react-native-get-random-values': false,
      'pino-pretty': false,
      fs: false,
      net: false,
      tls: false,
    };

    // Ignore React Native and Node.js modules
    config.externals = config.externals || [];
    if (!isServer) {
      config.externals.push({
        '@react-native-async-storage/async-storage': 'false',
        'react-native': 'false',
        'pino-pretty': 'false',
        fs: 'false',
        net: 'false',
        tls: 'false',
      });
    }

    // Add module resolution for problematic packages
    config.module.rules.push({
      test: /\.m?js$/,
      resolve: {
        fullySpecified: false,
      },
    });

    return config;
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=31536000; includeSubDomains',
          },
        ],
      },
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: 'https://aeoninvestmentstechnologies.com',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
