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
  className,
  imgClassName,
}: {
  title: string;
  desc: string;
  img?: string;
  className?: string;
  imgClassName?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.6 }}
      className={`group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-5 hover:border-white/20 ${className ?? ''}`}
    >
      {img && (
        <div className="mb-4 overflow-hidden rounded-xl bg-black">
          <img src={img} alt={title} className={`h-40 w-full object-contain opacity-90 transition group-hover:opacity-100 ${imgClassName ?? ''}`} />
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
      {/* Partners / Integrations - Infinite Scroll */}
      <section className="mx-auto max-w-7xl px-6 py-12">
        <div className="mb-6 text-center text-xs uppercase tracking-[0.2em] text-white/50">Trusted Integrations</div>
        <div className="relative overflow-hidden">
          <div className="flex animate-scroll-left space-x-8">
            {/* First set of logos */}
            {[
              "/partners/0x.png", "/partners/aave.png", "/partners/alchemy.png", "/partners/balancer.png",
              "/partners/base.png", "/partners/bitquery.jpg", "/partners/chainlink.png", "/partners/clerk.jpg",
              "/partners/cowdao.png", "/partners/curve.png", "/partners/dune.png", "/partners/ethereum.png",
              "/partners/metamask.png", "/partners/postgre.png", "/partners/quicknode.png", "/partners/replicate.png",
              "/partners/supabase.png", "/partners/sushi.png", "/partners/uniswap.png", "/partners/vercel.png"
            ].map((src, i) => (
              <img key={i} src={src} alt="partner logo" className="h-12 w-20 object-contain grayscale opacity-70 hover:opacity-100 transition flex-shrink-0" />
            ))}
            {/* Duplicate set for seamless loop */}
            {[
              "/partners/0x.png", "/partners/aave.png", "/partners/alchemy.png", "/partners/balancer.png",
              "/partners/base.png", "/partners/bitquery.jpg", "/partners/chainlink.png", "/partners/clerk.jpg",
              "/partners/cowdao.png", "/partners/curve.png", "/partners/dune.png", "/partners/ethereum.png",
              "/partners/metamask.png", "/partners/postgre.png", "/partners/quicknode.png", "/partners/replicate.png",
              "/partners/supabase.png", "/partners/sushi.png", "/partners/uniswap.png", "/partners/vercel.png"
            ].map((src, i) => (
              <img key={`dup-${i}`} src={src} alt="partner logo" className="h-12 w-20 object-contain grayscale opacity-70 hover:opacity-100 transition flex-shrink-0" />
            ))}
          </div>
        </div>
      </section>

      {/* Products Section */}
      <section className="mx-auto max-w-7xl px-6 py-12">
        <SectionTitle label="Products" title="Empowering Investors with Cutting-Edge Modules" subtitle="High-performance arbitrage execution with on-chain validation, gas-optimized routing, and risk controls." />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card title="Execution Guard" desc="MEV-aware protection and fail-safe routing with slippage locks and spread thresholds." img="/execution-guard.png" />
          <Card title="Path Finder" desc="Multi-DEX quotes with Curve/Balancer math validation and per-hop slippage controls." img="/pathfinder.png" imgClassName="h-44 contrast-125" />
          <Card title="Profit Engine" desc="ROI gating after gas, dynamic cooldowns, and Supabase audit trails for every trade." img="/profit-engine.png" />
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

      {/* Showcase Banner — 3D Coin Flip (front ↔ back) */}
      <section className="relative mx-auto max-w-7xl px-6 py-16">
        <div
          className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent h-[420px] md:h-[520px] flex items-center justify-center perspective-1200"
        >
          {/* 3D stage */}
          <div className="relative h-full w-full max-w-4xl preserve-3d">
            {/* Rotating core */}
            <div
              className="absolute inset-0 motion-safe:animate-[spinY_8s_linear_infinite] will-change-transform preserve-3d"
            >
              {/* Front face */}
              <img
                src="/5.png"
                alt="gold coin front"
                className="absolute inset-0 h-full w-full object-contain backface-hidden"
              />
              {/* Back face (same asset; rotated so it isn't mirrored) */}
              <img
                src="/5.png"
                alt="gold coin back"
                className="absolute inset-0 h-full w-full object-contain backface-hidden rotate-y-180"
              />
            </div>
          </div>

          {/* Label moved to bottom-left */}
          <div className="absolute bottom-4 left-4">
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

