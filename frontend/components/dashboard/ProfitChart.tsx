"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { TrendingUp } from "lucide-react";

export function ProfitChart() {
  // Mock data for the chart
  const data = [
    { date: "Jan 1", profit: 0 },
    { date: "Jan 2", profit: 45.67 },
    { date: "Jan 3", profit: 123.45 },
    { date: "Jan 4", profit: 89.12 },
    { date: "Jan 5", profit: 234.56 },
    { date: "Jan 6", profit: 345.67 },
    { date: "Jan 7", profit: 456.78 },
    { date: "Jan 8", profit: 567.89 },
    { date: "Jan 9", profit: 678.90 },
    { date: "Jan 10", profit: 789.01 },
    { date: "Jan 11", profit: 890.12 },
    { date: "Jan 12", profit: 1001.23 },
    { date: "Jan 13", profit: 1112.34 },
    { date: "Jan 14", profit: 1234.56 },
  ];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-600 rounded-lg p-3 shadow-lg">
          <p className="text-gray-300 text-sm">{label}</p>
          <p className="text-green-400 font-semibold">
            Profit: ${payload[0].value.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
    >
      <Card className="bg-gray-900/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center text-white">
            <TrendingUp className="h-5 w-5 mr-2 text-green-400" />
            Cumulative Profit (7 Days)
          </CardTitle>
          <CardDescription className="text-gray-300">
            Track your arbitrage profits over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="date" 
                  stroke="#9CA3AF"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#9CA3AF"
                  fontSize={12}
                  tickFormatter={(value) => `$${value}`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="profit"
                  stroke="#10B981"
                  strokeWidth={3}
                  dot={{ fill: "#10B981", strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: "#10B981", strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-400">Total Profit</p>
              <p className="text-lg font-semibold text-green-400">$1,234.56</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-400">Average Daily</p>
              <p className="text-lg font-semibold text-blue-400">$88.18</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-400">Best Day</p>
              <p className="text-lg font-semibold text-purple-400">$234.56</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
