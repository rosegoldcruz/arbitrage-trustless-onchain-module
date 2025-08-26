"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface TriSignal {
  a: string;
  b: string;
  c: string;
  a_symbol: string;
  b_symbol: string;
  c_symbol: string;
  dex_ab: string;
  dex_bc: string;
  dex_ca: string;
  p_ab: number;
  p_bc: number;
  p_ca: number;
  net_profit_usd: number;
  amount_usd: number;
  ts: number;
}

export function TriangularWidget() {
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "https://api.smart4technology.com";
  const [status, setStatus] = useState<{ total_recent: number; best_net_profit_usd: number; last_update: number } | null>(null);
  const [signals, setSignals] = useState<TriSignal[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      setError(null);
      const [st, sg] = await Promise.all([
        fetch(`${API_BASE}/triangular/status`).then(r => r.json()),
        fetch(`${API_BASE}/triangular/signals?limit=10`).then(r => r.json()),
      ]);
      if (st?.status === "ok") setStatus(st);
      if (sg?.status === "success") setSignals(sg.data?.signals || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load triangular data");
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
          <span>Triangular Arbitrage</span>
          {status ? (
            <div className="flex items-center gap-2 text-xs text-gray-300">
              <Badge variant="outline" className="border-blue-500 text-blue-300">signals {status.total_recent}</Badge>
              <Badge variant="outline" className="border-green-500 text-green-300">best PnL ${status.best_net_profit_usd?.toFixed?.(2) ?? status.best_net_profit_usd}</Badge>
            </div>
          ) : (
            <span className="text-xs text-gray-400">loading…</span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error && <div className="text-sm text-red-400">{error}</div>}
        {!error && signals.length === 0 && (
          <div className="text-sm text-gray-400">No recent triangles.</div>
        )}
        {!error && signals.length > 0 && (
          <div className="space-y-2">
            {signals.map((s, idx) => (
              <div key={idx} className="rounded-md border border-white/10 bg-black/20 px-3 py-2 text-xs text-gray-300">
                <div className="flex items-center justify-between">
                  <div className="font-medium text-white/90">{s.a_symbol} → {s.b_symbol} → {s.c_symbol} → {s.a_symbol}</div>
                  <div className="text-green-300 font-medium">${s.net_profit_usd.toFixed(2)}</div>
                </div>
                <div className="mt-1 text-gray-400">
                  <span className="mr-3">AB: {s.dex_ab}</span>
                  <span className="mr-3">BC: {s.dex_bc}</span>
                  <span>CA: {s.dex_ca}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
} 