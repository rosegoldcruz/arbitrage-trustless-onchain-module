import React from 'react';
import ArbitrageMonitor from '@/components/ArbitrageMonitor';

export default function MonitorPage() {
  return (
    <div className="min-h-screen bg-gray-900">
      <ArbitrageMonitor />
    </div>
  );
}

export const metadata = {
  title: 'AEON Arbitrage Monitor | Real-time Trading Dashboard',
  description: 'Monitor live arbitrage opportunities, system health, and trading performance in real-time',
};
