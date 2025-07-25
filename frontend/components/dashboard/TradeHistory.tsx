"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { History, ExternalLink } from "lucide-react";

interface Trade {
  id: string;
  date: string;
  pair: string;
  profit: number;
  gas: number;
  status: "success" | "failed" | "pending";
  txHash: string;
  network: string;
  agent: string;
}

export function TradeHistory() {
  const [currentPage] = useState(1);
  const [filter, setFilter] = useState<"all" | "success" | "failed">("all");
  
  const trades: Trade[] = [
    {
      id: "1",
      date: "2025-01-22 14:30:15",
      pair: "ETH/USDC",
      profit: 45.67,
      gas: 0.012,
      status: "success",
      txHash: "0x1234...5678",
      network: "Ethereum",
      agent: "ATOM",
    },
    {
      id: "2",
      date: "2025-01-22 14:25:42",
      pair: "WBTC/ETH",
      profit: 123.45,
      gas: 0.018,
      status: "success",
      txHash: "0x2345...6789",
      network: "Ethereum",
      agent: "ADOM",
    },
    {
      id: "3",
      date: "2025-01-22 14:20:18",
      pair: "USDC/DAI",
      profit: 23.89,
      gas: 0.008,
      status: "success",
      txHash: "0x3456...7890",
      network: "Base",
      agent: "ATOM",
    },
    {
      id: "4",
      date: "2025-01-22 14:15:33",
      pair: "ETH/USDT",
      profit: 0,
      gas: 0.015,
      status: "failed",
      txHash: "0x4567...8901",
      network: "Ethereum",
      agent: "ATOM",
    },
    {
      id: "5",
      date: "2025-01-22 14:10:07",
      pair: "MATIC/USDC",
      profit: 67.23,
      gas: 0.005,
      status: "success",
      txHash: "0x5678...9012",
      network: "Polygon",
      agent: "ADOM",
    },
  ];

  const filteredTrades = trades.filter(trade => 
    filter === "all" || trade.status === filter
  );

  const getStatusColor = (status: Trade["status"]) => {
    switch (status) {
      case "success":
        return "bg-green-500/20 text-green-400 border-green-500/30";
      case "failed":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      case "pending":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/30";
    }
  };

  const getNetworkColor = (network: string) => {
    switch (network.toLowerCase()) {
      case "ethereum":
        return "bg-blue-500/20 text-blue-400";
      case "base":
        return "bg-blue-600/20 text-blue-300";
      case "arbitrum":
        return "bg-blue-700/20 text-blue-200";
      case "polygon":
        return "bg-purple-500/20 text-purple-400";
      default:
        return "bg-gray-500/20 text-gray-400";
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.6 }}
    >
      <Card className="bg-gray-900/50 border-gray-700">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center text-white">
                <History className="h-5 w-5 mr-2 text-purple-400" />
                Trade History
              </CardTitle>
              <CardDescription className="text-gray-300">
                Recent arbitrage transactions
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                size="sm"
                variant={filter === "all" ? "default" : "outline"}
                onClick={() => setFilter("all")}
                className="text-xs"
              >
                All
              </Button>
              <Button
                size="sm"
                variant={filter === "success" ? "default" : "outline"}
                onClick={() => setFilter("success")}
                className="text-xs"
              >
                Success
              </Button>
              <Button
                size="sm"
                variant={filter === "failed" ? "default" : "outline"}
                onClick={() => setFilter("failed")}
                className="text-xs"
              >
                Failed
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">Date</th>
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">Pair</th>
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">Profit</th>
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">Gas</th>
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">Status</th>
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">Network</th>
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">Agent</th>
                  <th className="text-left py-3 px-2 text-gray-400 font-medium">Tx</th>
                </tr>
              </thead>
              <tbody>
                {filteredTrades.map((trade, index) => (
                  <motion.tr
                    key={trade.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    className="border-b border-gray-800 hover:bg-gray-800/30"
                  >
                    <td className="py-3 px-2 text-gray-300 font-mono text-xs">
                      {trade.date}
                    </td>
                    <td className="py-3 px-2 text-white font-medium">
                      {trade.pair}
                    </td>
                    <td className="py-3 px-2">
                      <span className={trade.profit > 0 ? "text-green-400" : "text-red-400"}>
                        ${trade.profit.toFixed(2)}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-gray-300">
                      {trade.gas.toFixed(3)} ETH
                    </td>
                    <td className="py-3 px-2">
                      <Badge className={getStatusColor(trade.status)}>
                        {trade.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-2">
                      <Badge className={getNetworkColor(trade.network)}>
                        {trade.network}
                      </Badge>
                    </td>
                    <td className="py-3 px-2 text-purple-400 font-medium">
                      {trade.agent}
                    </td>
                    <td className="py-3 px-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-blue-400 hover:text-blue-300 p-1"
                        onClick={() => window.open(`https://etherscan.io/tx/${trade.txHash}`, "_blank")}
                      >
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {filteredTrades.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No trades found for the selected filter
            </div>
          )}
          
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-700">
            <p className="text-sm text-gray-400">
              Showing {filteredTrades.length} of {trades.length} trades
            </p>
            <div className="flex space-x-2">
              <Button
                size="sm"
                variant="outline"
                disabled={currentPage === 1}
                className="border-gray-600 text-white hover:bg-gray-700"
              >
                Previous
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="border-gray-600 text-white hover:bg-gray-700"
              >
                Next
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
