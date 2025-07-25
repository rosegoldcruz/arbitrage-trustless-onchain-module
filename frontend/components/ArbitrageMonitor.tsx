'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Activity, 
  TrendingUp, 
  Zap, 
  DollarSign, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw
} from 'lucide-react';

interface ArbitrageOpportunity {
  token_triple: string[];
  spread_bps: number;
  expected_profit: number;
  confidence: number;
  last_updated: string;
  status: string;
}

interface SystemHealth {
  rpc_connection: string;
  contract_status: string;
  flashloan_provider: string;
  gas_price_gwei: number;
  network_congestion: string;
  last_health_check: string;
}

interface LiveMetrics {
  total_scans_today: number;
  opportunities_found: number;
  successful_executions: number;
  total_profit_today: number;
  success_rate: number;
  avg_execution_time: number;
  current_gas_price: number;
  network_utilization: number;
}

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  source: string;
}

const ArbitrageMonitor: React.FC = () => {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [liveMetrics, setLiveMetrics] = useState<LiveMetrics | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logs to bottom
  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  // Fetch arbitrage status
  const fetchStatus = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/arbitrage/status`);
      if (response.ok) {
        const data = await response.json();
        setOpportunities(data.current_opportunities);
        setSystemHealth(data.system_health);
        setLiveMetrics(data.live_metrics);
        setIsConnected(true);
        setLastUpdate(new Date().toLocaleTimeString());
      } else {
        setIsConnected(false);
      }
    } catch (error) {
      console.error('Failed to fetch arbitrage status:', error);
      setIsConnected(false);
    }
  };

  // Fetch logs
  const fetchLogs = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/arbitrage/logs?limit=20`);
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs);
      }
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  };

  // Setup polling
  useEffect(() => {
    fetchStatus();
    fetchLogs();
    
    const statusInterval = setInterval(fetchStatus, 5000); // 5 seconds
    const logsInterval = setInterval(fetchLogs, 3000); // 3 seconds
    
    return () => {
      clearInterval(statusInterval);
      clearInterval(logsInterval);
    };
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready_to_execute': return 'bg-green-500';
      case 'monitoring': return 'bg-blue-500';
      case 'below_threshold': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready_to_execute': return <CheckCircle className="w-4 h-4" />;
      case 'monitoring': return <Activity className="w-4 h-4" />;
      case 'below_threshold': return <AlertTriangle className="w-4 h-4" />;
      default: return <XCircle className="w-4 h-4" />;
    }
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'SUCCESS': return 'text-green-400';
      case 'WARNING': return 'text-yellow-400';
      case 'ERROR': return 'text-red-400';
      default: return 'text-blue-400';
    }
  };

  return (
    <div className="space-y-6 p-6 bg-gray-900 min-h-screen text-white">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">🧬 AEON Arbitrage Monitor</h1>
          <p className="text-gray-400">Real-time arbitrage opportunities and system status</p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant={isConnected ? "default" : "destructive"}>
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </Badge>
          <span className="text-sm text-gray-400">Last update: {lastUpdate}</span>
          <Button onClick={() => { fetchStatus(); fetchLogs(); }} size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Live Metrics */}
      {liveMetrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                <div>
                  <p className="text-sm text-gray-400">Total Profit Today</p>
                  <p className="text-2xl font-bold text-green-400">${liveMetrics.total_profit_today.toFixed(2)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-blue-400" />
                <div>
                  <p className="text-sm text-gray-400">Success Rate</p>
                  <p className="text-2xl font-bold text-blue-400">{(liveMetrics.success_rate * 100).toFixed(1)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Clock className="w-5 h-5 text-purple-400" />
                <div>
                  <p className="text-sm text-gray-400">Avg Execution</p>
                  <p className="text-2xl font-bold text-purple-400">{liveMetrics.avg_execution_time.toFixed(1)}s</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <DollarSign className="w-5 h-5 text-yellow-400" />
                <div>
                  <p className="text-sm text-gray-400">Gas Price</p>
                  <p className="text-2xl font-bold text-yellow-400">{liveMetrics.current_gas_price} gwei</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Opportunities */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span>Current Opportunities</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {opportunities.map((opp, index) => (
                <div key={index} className="p-4 bg-gray-700 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(opp.status)}
                      <span className="font-medium">{opp.token_triple.join(' → ')}</span>
                    </div>
                    <Badge className={getStatusColor(opp.status)}>
                      {opp.spread_bps}bps
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Expected Profit:</span>
                      <span className="ml-2 text-green-400">${opp.expected_profit.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Confidence:</span>
                      <span className="ml-2">{opp.confidence}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Live Terminal */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span>AEON Engine Logs</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-96 w-full">
              <div className="space-y-1 font-mono text-sm">
                {logs.map((log, index) => (
                  <div key={index} className="flex space-x-2">
                    <span className="text-gray-500 text-xs">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span className={getLogLevelColor(log.level)}>
                      {log.level}
                    </span>
                    <span className="text-gray-300">{log.message}</span>
                  </div>
                ))}
                <div ref={logsEndRef} />
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* System Health */}
      {systemHealth && (
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle>System Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${systemHealth.rpc_connection === 'healthy' ? 'bg-green-400' : 'bg-red-400'}`} />
                <span>RPC Connection: {systemHealth.rpc_connection}</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${systemHealth.contract_status === 'deployed' ? 'bg-green-400' : 'bg-red-400'}`} />
                <span>Contract: {systemHealth.contract_status}</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${systemHealth.flashloan_provider === 'available' ? 'bg-green-400' : 'bg-red-400'}`} />
                <span>Flashloan: {systemHealth.flashloan_provider}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ArbitrageMonitor;
