'use client';

/**
 * 🚀 PARALLEL DASHBOARD PAGE
 * Main page for live Balancer & 0x parallel analytics
 * Base Sepolia Testnet - Production Grade Real-Time Data
 */

import React from 'react';
import { Suspense } from 'react';
import ParallelDashboard from '@/components/dashboard/ParallelDashboard';
import { Card, CardContent } from '@/components/ui/card';
import { RefreshCw } from 'lucide-react';

// Loading component
const DashboardLoading = () => (
  <div className="container mx-auto p-6">
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center space-y-4">
        <RefreshCw className="h-12 w-12 animate-spin mx-auto text-blue-500" />
        <div>
          <h2 className="text-xl font-semibold">Loading ATOM Dashboard</h2>
          <p className="text-muted-foreground">
            Connecting to Balancer & 0x services...
          </p>
        </div>
      </div>
    </div>
  </div>
);

// Error boundary component
class DashboardErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Dashboard error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="container mx-auto p-6">
          <Card className="border-red-200">
            <CardContent className="p-6">
              <div className="text-center space-y-4">
                <div className="text-red-500">
                  <svg
                    className="h-12 w-12 mx-auto"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                    />
                  </svg>
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-red-700">
                    Dashboard Error
                  </h2>
                  <p className="text-muted-foreground mt-2">
                    Failed to load the parallel dashboard. Please check:
                  </p>
                  <ul className="text-sm text-left mt-4 space-y-1 max-w-md mx-auto">
                    <li>• Backend API is running (port 8000)</li>
                    <li>• Balancer GraphQL API is accessible</li>
                    <li>• 0x API key is configured</li>
                    <li>• Network connection is stable</li>
                  </ul>
                  <button
                    onClick={() => window.location.reload()}
                    className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Reload Dashboard
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// Main page component
export default function ParallelDashboardPage() {
  return (
    <DashboardErrorBoundary>
      <div className="min-h-screen bg-background">
        {/* Page Header */}
        <div className="border-b bg-card">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">ATOM Parallel Dashboard</h1>
                <p className="text-sm text-muted-foreground">
                  Real-time Balancer & 0x analytics for Base Sepolia testnet
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-muted-foreground">Live Data</span>
              </div>
            </div>
          </div>
        </div>

        {/* Dashboard Content */}
        <Suspense fallback={<DashboardLoading />}>
          <ParallelDashboard />
        </Suspense>

        {/* Footer */}
        <footer className="border-t bg-card mt-12">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <div>
                <p>ATOM Arbitrage Engine • Base Sepolia Testnet</p>
              </div>
              <div className="flex items-center space-x-4">
                <span>Balancer GraphQL API</span>
                <span>•</span>
                <span>0x REST API</span>
                <span>•</span>
                <span>WebSocket Live Updates</span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </DashboardErrorBoundary>
  );
}
