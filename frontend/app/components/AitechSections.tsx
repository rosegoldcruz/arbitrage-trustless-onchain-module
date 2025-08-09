'use client';

import { motion } from 'framer-motion';

function SectionTitle({ label, title, subtitle }: { label: string; title: string; subtitle?: string }) {
  return (
    <div className="mb-8 text-center">
      <div className="text-xs uppercase tracking-[0.2em] text-white/50">{label}</div>
      <h2 className="mt-2 text-2xl md:text-4xl font-extrabold text-white">{title}</h2>
      {subtitle && <p className="mt-3 text-white/60 max-w-3xl mx-auto">{subtitle}</p>}
    </div>
  );
}

function Card({
  title,
  desc,
  img,
}: {
  title: string;
  desc: string;
  img?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.6 }}
      className="group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-5 hover:border-white/20"
    >
      {img && (
        <div className="mb-4 overflow-hidden rounded-xl bg-black">
          <img src={img} alt={title} className="h-40 w-full object-contain opacity-90 transition group-hover:opacity-100" />
        </div>
      )}
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm text-white/60">{desc}</p>
    </motion.div>
  );
}

export default function AitechSections() {
  return (
    <div className="relative">
      {/* Partners / Integrations */}
      <section className="mx-auto max-w-7xl px-6 py-12">
        <div className="mb-6 text-center text-xs uppercase tracking-[0.2em] text-white/50">Trusted Integrations</div>
        <div className="grid grid-cols-3 md:grid-cols-6 items-center gap-6 opacity-70">
          {["/1.png","/2.png","/3.png","/4.png","/5.png","/6.png"].map((src, i) => (
            <img key={i} src={src} alt="logo" className="mx-auto h-8 w-auto grayscale opacity-70 hover:opacity-100 transition" />
          ))}
        </div>
      </section>

      {/* Products Section */}
      <section className="mx-auto max-w-7xl px-6 py-12">
        <SectionTitle label="Products" title="Empowering Investors with Cutting-Edge Modules" subtitle="High-performance arbitrage execution with on-chain validation, gas-optimized routing, and risk controls." />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card title="Execution Guard" desc="MEV-aware protection and fail-safe routing with slippage locks and spread thresholds." img="/1.png" />
          <Card title="Path Finder" desc="Multi-DEX quotes with Curve/Balancer math validation and per-hop slippage controls." img="/2.png" />
          <Card title="Profit Engine" desc="ROI gating after gas, dynamic cooldowns, and Supabase audit trails for every trade." img="/3.png" />
        </div>
      </section>

      {/* SDK Center-like quick links */}
      <section className="mx-auto max-w-7xl px-6 py-12">
        <SectionTitle label="Docs Center" title="Plug In. Go Live." />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card title="API /trigger" desc="Fire spot arbitrage with validated routes." />
          <Card title="/flash-loan" desc="ADOM flashloan executor for high-gas cycles." />
          <Card title="/health" desc="Agent health + dashboard heartbeat." />
        </div>
      </section>

      {/* Showcase Banner */}
      <section className="relative mx-auto max-w-7xl px-6 py-16">
        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent">
          <img src="/4.png" alt="stage" className="h-64 w-full object-cover opacity-70" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="rounded-full border border-white/20 bg-black/40 px-6 py-3 text-sm uppercase tracking-[0.25em] text-white/80">ATOM • Base L2</div>
          </div>
        </div>
      </section>

      {/* More Products / Features */}
      <section className="mx-auto max-w-7xl px-6 py-12">
        <SectionTitle label="Capabilities" title="Concrete Results, Not Hype" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card title="Live Spread Scanner" desc="0x, Uniswap v3, 1inch — consolidated quotes and spreads." img="/live-spread-scanner.png" />
          <Card title="Virtual Price Sim" desc="Curve virtual price + Balancer invariants before every route." img="/virtual-price-sim.png" />
          <Card title="Gas Simulator" desc="Per-route gas estimates to ensure ROI-after-gas clarity." img="/gas-simulator.png" />
        </div>
      </section>
    </div>
  );
}

