"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface VolSignal {
  token: string;
  symbol: string;
  source_dex: string;
  price_usd: number;
  ret_5m: number;
  ret_15m: number;
  vol_std: number;
  vol_spike: number;
  pattern: string;
  confidence: number;
  net_profit_usd: number;
  ts: number;
}

export function VolatilityWidget() {
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "https://api.smart4technology.com";
  const [status, setStatus] = useState<{ total_recent: number; best_confidence: number; best_net_profit_usd: number; last_update: number } | null>(null);
  const [signals, setSignals] = useState<VolSignal[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      setError(null);
      const [st, sg] = await Promise.all([
        fetch(`${API_BASE}/volatility/status`).then(r => r.json()),
        fetch(`${API_BASE}/volatility/signals?limit=10`).then(r => r.json()),
      ]);
      if (st?.status === "ok") {
        setStatus(st);
      }
      if (sg?.status === "success") {
        setSignals(sg.data?.signals || []);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load volatility data");
    }
  };

  useEffect(() => {
    load();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, []);

  return (
    <Card className="bg-gray-900/50 border-gray-800">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Volatility Scanner</span>
          {status ? (
            <div className="flex items-center gap-2 text-xs text-gray-300">
              <Badge variant="outline" className="border-blue-500 text-blue-300">signals {status.total_recent}</Badge>
              <Badge variant="outline" className="border-green-500 text-green-300">best PnL ${status.best_net_profit_usd?.toFixed?.(2) ?? status.best_net_profit_usd}</Badge>
              <Badge variant="outline" className="border-purple-500 text-purple-300">conf {(status.best_confidence * 100).toFixed(0)}%</Badge>
            </div>
          ) : (
            <span className="text-xs text-gray-400">loading…</span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error && <div className="text-sm text-red-400">{error}</div>}
        {!error && signals.length === 0 && (
          <div className="text-sm text-gray-400">No recent volatility signals.</div>
        )}
        {!error && signals.length > 0 && (
          <div className="space-y-2">
            {signals.map((s, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-md border border-white/10 bg-black/20 px-3 py-2">
                <div className="flex items-center gap-3">
                  <Badge variant="outline" className="border-white/20 text-white/80 w-16 justify-center">{s.symbol}</Badge>
                  <div className="text-xs text-gray-300">
                    <div className="font-medium text-white/90">{s.pattern.toUpperCase()} • {s.source_dex}</div>
                    <div className="text-gray-400">5m {(s.ret_5m*100).toFixed(2)}% • 15m {(s.ret_15m*100).toFixed(2)}% • σ {s.vol_std.toFixed(3)}</div>
                  </div>
                </div>
                <div className="text-right text-xs">
                  <div className="text-green-300">${s.net_profit_usd.toFixed(2)}</div>
                  <div className="text-gray-400">${s.price_usd.toFixed(4)}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
} 