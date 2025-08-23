"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, Play, Pause, Settings, DollarSign, Activity, Loader2, TrendingUp } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { AgentRippleLoader } from "@/components/ui/RippleLoader";

interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'paused' | 'error';
  profit: string;
  profit_24h: string;
  trades: number;
  trades_24h: number;
  success_rate: number;
  avatar: string;
  strategy: string;
  networks: string[];
  uptime: string;
  last_trade: string;
}

export function AgentPanel() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const response = await api.agents.getAll();

      if (response.success && response.data) {
        setAgents(response.data.agents);
      } else {
        toast.error("Failed to fetch agents");
      }
    } catch (error) {
      console.error("Error fetching agents:", error);
      toast.error("Error loading agents");
    } finally {
      setLoading(false);
    }
  };

  const toggleAgent = async (agentId: string, currentStatus: string) => {
    try {
      setActionLoading(agentId);

      const response = currentStatus === 'active'
        ? await api.agents.stop(agentId)
        : await api.agents.start(agentId);

      if (response.success) {
        // Update local state
        setAgents(agents.map(agent =>
          agent.id === agentId
            ? { ...agent, status: response.data.status }
            : agent
        ));

        toast.success(response.data.message);
      } else {
        toast.error("Failed to toggle agent");
      }
    } catch (error) {
      console.error("Error toggling agent:", error);
      toast.error("Error controlling agent");
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400';
      case 'paused': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-400/20';
      case 'paused': return 'bg-yellow-400/20';
      case 'error': return 'bg-red-400/20';
      default: return 'bg-gray-400/20';
    }
  };

  if (loading) {
    return (
      <Card className="bg-gray-900/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center text-white">
            <Bot className="h-5 w-5 mr-2 text-blue-400" />
            AI Agents
          </CardTitle>
          <CardDescription className="text-gray-300">
            Loading agent status...
          </CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-blue-400" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-gray-900/50 border-gray-700">
      <CardHeader>
        <CardTitle className="flex items-center text-white">
          <Bot className="h-5 w-5 mr-2 text-blue-400" />
          AI Agents
        </CardTitle>
        <CardDescription className="text-gray-300">
          Monitor and control your arbitrage agents
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {agents.map((agent, index) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="bg-gray-800/50 rounded-lg p-4 border border-gray-700"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="text-2xl">{agent.avatar}</div>
                <div>
                  <h3 className="font-semibold text-white">{agent.name}</h3>
                  <p className="text-sm text-gray-400">{agent.description}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBg(agent.status)} ${getStatusColor(agent.status)}`}>
                  {agent.status}
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => toggleAgent(agent.id, agent.status)}
                  className="border-gray-600 text-white hover:bg-gray-700"
                >
                  {agent.status === 'active' ? (
                    <Pause className="h-3 w-3" />
                  ) : (
                    <Play className="h-3 w-3" />
                  )}
                </Button>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <DollarSign className="h-4 w-4 text-green-400" />
                <div>
                  <p className="text-sm text-gray-400">Profit</p>
                  <p className="font-semibold text-white">{agent.profit}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Activity className="h-4 w-4 text-blue-400" />
                <div>
                  <p className="text-sm text-gray-400">Trades</p>
                  <p className="font-semibold text-white">{agent.trades}</p>
                </div>
              </div>
            </div>
            
            <div className="mt-3 pt-3 border-t border-gray-700">
              <Button
                size="sm"
                variant="ghost"
                className="w-full text-gray-400 hover:text-white hover:bg-gray-700"
              >
                <Settings className="h-3 w-3 mr-2" />
                Configure Agent
              </Button>
            </div>
          </motion.div>
        ))}
      </CardContent>
    </Card>
  );
}
