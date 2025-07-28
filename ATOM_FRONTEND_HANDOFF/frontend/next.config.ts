import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  experimental: {
    optimizePackageImports: ['lucide-react', 'recharts'],
  },
  images: {
    domains: ['localhost'],
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
        ],
      },
    ];
  },
};

export default nextConfig;
