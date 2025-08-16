"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface TradeRow {
  id: string;
  timestamp: string;
  pair: string;
  type: string;
  profit: number;
  gas_cost: number;
  status: string;
  agent: string;
  network: string;
  tx_hash?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "https://api.aeoninvestmentstechnologies.com";

export function RecentTradesTable() {
  const [rows, setRows] = useState<TradeRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        // Preferred: /health with embedded recent trades
        let res = await fetch(`${API_BASE}/health`);
        let rows: TradeRow[] = [];
        if (res.ok) {
          const health = await res.json();
          const list = (health.recent_trades || health.recentTrades) as any[] | undefined;
          if (Array.isArray(list)) {
            rows = list as TradeRow[];
          }
        }
        if (!rows || rows.length === 0) {
          // Fallback: dedicated trades endpoint
          res = await fetch(`${API_BASE}/trades/recent?limit=10`);
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          rows = await res.json();
        }
        setRows(rows);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load trades");
      }
    };
    load();
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return <div className="text-sm text-red-400">Failed to load recent trades: {error}</div>;
  }

  if (rows.length === 0) {
    return <div className="text-sm text-gray-400">No recent trades.</div>;
  }

  return (
    <Card className="bg-gray-900/50 border-gray-800">
      <CardContent className="p-0">
        <div className="max-h-64 overflow-y-auto">
          <table className="min-w-full text-sm">
            <thead className="sticky top-0 bg-gray-900/80">
              <tr>
                <th className="text-left p-3 text-gray-300">Time</th>
                <th className="text-left p-3 text-gray-300">Pair</th>
                <th className="text-left p-3 text-gray-300">Agent</th>
                <th className="text-left p-3 text-gray-300">Profit</th>
                <th className="text-left p-3 text-gray-300">Tx</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((t) => (
                <tr key={t.id} className="border-t border-gray-800 hover:bg-gray-800/40">
                  <td className="p-3 text-gray-300">{new Date(t.timestamp).toLocaleTimeString()}</td>
                  <td className="p-3 text-white">{t.pair}</td>
                  <td className="p-3">
                    <Badge className="bg-blue-600/30 text-blue-300 border border-blue-600/30">{t.agent}</Badge>
                  </td>
                  <td className="p-3">
                    <span className={t.profit > 0 ? "text-green-400" : "text-gray-400"}>
                      ${t.profit.toFixed(2)}
                    </span>
                  </td>
                  <td className="p-3">
                    {t.tx_hash ? (
                      <a
                        href={`https://basescan.org/tx/${t.tx_hash}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-400 hover:text-blue-300"
                      >
                        {t.tx_hash.slice(0, 10)}...
                      </a>
                    ) : (
                      <span className="text-gray-500">pending</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

