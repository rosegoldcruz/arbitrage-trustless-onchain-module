"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface LMOpp {
  protocol: string;
  pool_pid: number;
  lp_token: string;
  symbol0: string;
  symbol1: string;
  tvl_usd: number;
  reward_token_symbol: string;
  reward_apr: number;
  fee_apr: number;
  total_apr: number;
  il_risk: number;
  compound_hours: number;
  ts: number;
}

export function LiquidityWidget() {
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "https://api.smart4technology.com";
  const [status, setStatus] = useState<{ total_recent: number; best_total_apr: number; last_update: number } | null>(null);
  const [opps, setOpps] = useState<LMOpp[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      setError(null);
      const [st, op] = await Promise.all([
        fetch(`${API_BASE}/liquidity/status`).then(r => r.json()),
        fetch(`${API_BASE}/liquidity/opportunities?limit=12`).then(r => r.json()),
      ]);
      if (st?.status === "ok") setStatus(st);
      if (op?.status === "success") setOpps(op.data?.opportunities || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load liquidity data");
    }
  };

  useEffect(() => {
    load();
    const t = setInterval(load, 60000);
    return () => clearInterval(t);
  }, []);

  return (
    <Card className="bg-gray-900/50 border-gray-800">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Liquidity Mining</span>
          {status ? (
            <div className="flex items-center gap-2 text-xs text-gray-300">
              <Badge variant="outline" className="border-blue-500 text-blue-300">items {status.total_recent}</Badge>
              <Badge variant="outline" className="border-green-500 text-green-300">best APR {status.best_total_apr?.toFixed?.(2) ?? status.best_total_apr}%</Badge>
            </div>
          ) : (
            <span className="text-xs text-gray-400">loading…</span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error && <div className="text-sm text-red-400">{error}</div>}
        {!error && opps.length === 0 && (
          <div className="text-sm text-gray-400">No recent liquidity opps.</div>
        )}
        {!error && opps.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {opps.map((o, idx) => (
              <div key={idx} className="rounded-md border border-white/10 bg-black/20 px-3 py-2 text-xs text-gray-300">
                <div className="flex items-center justify-between">
                  <div className="font-medium text-white/90">{o.protocol.toUpperCase()} • {o.symbol0}/{o.symbol1}</div>
                  <div className="text-green-300 font-medium">{o.total_apr.toFixed(2)}%</div>
                </div>
                <div className="mt-1 text-gray-400 flex items-center gap-3">
                  <span>TVL ${o.tvl_usd.toLocaleString()}</span>
                  <span>reward {o.reward_token_symbol} {o.reward_apr.toFixed(2)}%</span>
                  <span>fee {o.fee_apr.toFixed(2)}%</span>
                  <span>IL {(o.il_risk * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
} 