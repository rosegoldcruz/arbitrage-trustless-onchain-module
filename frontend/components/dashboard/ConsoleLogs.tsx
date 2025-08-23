"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Terminal, Trash2, Download, Pause, Play, RefreshCw, AlertCircle, CheckCircle, Info, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

interface LogEntry {
  id: string;
  timestamp: string;
  level: "info" | "success" | "warning" | "error";
  message: string;
  agent?: string;
}

export function ConsoleLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: "1",
      timestamp: new Date().toLocaleTimeString(),
      level: "info",
      message: "ATOM agent initialized successfully",
      agent: "ATOM",
    },
    {
      id: "2",
      timestamp: new Date().toLocaleTimeString(),
      level: "success",
      message: "Arbitrage opportunity detected: ETH/USDC on Uniswap vs Curve",
      agent: "ATOM",
    },
    {
      id: "3",
      timestamp: new Date().toLocaleTimeString(),
      level: "success",
      message: "Flash loan executed: $10,000 USDC borrowed from AAVE",
      agent: "ATOM",
    },
    {
      id: "4",
      timestamp: new Date().toLocaleTimeString(),
      level: "success",
      message: "Arbitrage completed: Profit $45.67 (0.46%)",
      agent: "ATOM",
    },
    {
      id: "5",
      timestamp: new Date().toLocaleTimeString(),
      level: "info",
      message: "ADOM agent scanning for multi-hop opportunities",
      agent: "ADOM",
    },
  ]);

  const [isAutoScroll, setIsAutoScroll] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const [isConnected, setIsConnected] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new logs are added
    if (isAutoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, isAutoScroll]);

  useEffect(() => {
    // Simulate real-time logs
    const interval = setInterval(() => {
      const messages = [
        { level: "success" as const, message: "💰 Arbitrage executed: ETH/USDC (+$67.89)", agent: "ATOM" },
        { level: "success" as const, message: "🎯 Flash loan completed: +$123.45 profit", agent: "ADOM" },
        { level: "info" as const, message: "🔍 Scanning 15 DEXes for opportunities", agent: "ATOM" },
        { level: "warning" as const, message: "⚠️ High gas detected: 42 gwei", agent: "SYSTEM" },
        { level: "success" as const, message: "✅ Multi-hop arbitrage: +$89.12", agent: "ADOM" },
        { level: "info" as const, message: "📊 Success rate: 94.2% (last 100 trades)", agent: "SYSTEM" },
        { level: "success" as const, message: "🚀 MEV protection saved $45.67", agent: "MEV_SENTINEL" },
        { level: "info" as const, message: "🌐 Monitoring 3 networks, 12 pairs", agent: "SYSTEM" },
      ];

      const randomMessage = messages[Math.floor(Math.random() * messages.length)];
      const newLog: LogEntry = {
        id: `log-${Date.now()}-${Math.random()}`,
        timestamp: new Date().toLocaleTimeString(),
        level: randomMessage.level,
        message: randomMessage.message,
        agent: randomMessage.agent,
      };

      setLogs(prev => {
        const updated = [...prev, newLog];
        return updated.slice(-50); // Keep last 50 logs
      });
    }, 2000 + Math.random() * 3000); // Random interval 2-5 seconds

    return () => clearInterval(interval);
  }, []);

  const getLevelColor = (level: LogEntry["level"]) => {
    switch (level) {
      case "success":
        return "text-green-400";
      case "warning":
        return "text-yellow-400";
      case "error":
        return "text-red-400";
      default:
        return "text-blue-400";
    }
  };

  const getLevelBg = (level: LogEntry["level"]) => {
    switch (level) {
      case "success":
        return "bg-green-400/10";
      case "warning":
        return "bg-yellow-400/10";
      case "error":
        return "bg-red-400/10";
      default:
        return "bg-blue-400/10";
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const downloadLogs = () => {
    const logText = logs
      .map(log => `[${log.timestamp}] ${log.level.toUpperCase()} ${log.agent ? `[${log.agent}]` : ""} ${log.message}`)
      .join("\n");
    
    const blob = new Blob([logText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `atom-logs-${new Date().toISOString().split("T")[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Card className="bg-gray-900/50 border-gray-700">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center text-white">
              <Terminal className="h-5 w-5 mr-2 text-green-400" />
              Console Logs
            </CardTitle>
            <CardDescription className="text-gray-300">
              Real-time system activity
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            {/* Connection Status */}
            <div className="flex items-center space-x-1 mr-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
              <span className="text-xs text-gray-400">
                {isConnected ? 'Live' : 'Offline'}
              </span>
            </div>

            {/* Pause/Play Button */}
            <Button
              size="sm"
              variant="outline"
              onClick={() => setIsPaused(!isPaused)}
              className={`border-gray-600 text-white hover:bg-gray-700 ${isPaused ? 'bg-yellow-500/20' : ''}`}
            >
              {isPaused ? <Play className="h-3 w-3" /> : <Pause className="h-3 w-3" />}
            </Button>

            {/* Auto-scroll Toggle */}
            <Button
              size="sm"
              variant="outline"
              onClick={() => setIsAutoScroll(!isAutoScroll)}
              className={`border-gray-600 text-white hover:bg-gray-700 ${isAutoScroll ? 'bg-blue-500/20' : ''}`}
            >
              <RefreshCw className={`h-3 w-3 ${isAutoScroll ? 'animate-spin' : ''}`} />
            </Button>

            <Button
              size="sm"
              variant="outline"
              onClick={downloadLogs}
              className="border-gray-600 text-white hover:bg-gray-700"
            >
              <Download className="h-3 w-3" />
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={clearLogs}
              className="border-gray-600 text-white hover:bg-gray-700"
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div
          ref={scrollRef}
          className="bg-black/50 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm space-y-1"
        >
          {logs.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              No logs available
            </div>
          ) : (
            logs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex items-start space-x-2 p-2 rounded ${getLevelBg(log.level)}`}
              >
                <span className="text-gray-500 text-xs whitespace-nowrap">
                  {log.timestamp}
                </span>
                <span className={`text-xs font-semibold uppercase ${getLevelColor(log.level)}`}>
                  {log.level}
                </span>
                {log.agent && (
                  <span className="text-purple-400 text-xs">
                    [{log.agent}]
                  </span>
                )}
                <span className="text-gray-300 text-xs flex-1">
                  {log.message}
                </span>
              </motion.div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
