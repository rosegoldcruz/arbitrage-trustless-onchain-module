'use client';

import { motion } from 'framer-motion';

function SectionTitle({ label, title, subtitle }: { label: string; title: string; subtitle?: string }) {
  return (
    <div className="mb-12 text-center">
      <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.25em] text-amber-400/80 font-semibold mb-4">
        <div className="w-8 h-px bg-gradient-to-r from-transparent to-amber-400/50"></div>
        {label}
        <div className="w-8 h-px bg-gradient-to-l from-transparent to-amber-400/50"></div>
      </div>
      <h2 className="text-3xl md:text-5xl font-bold text-white bg-gradient-to-r from-white via-white to-zinc-300 bg-clip-text text-transparent leading-tight">
        {title}
      </h2>
      {subtitle && (
        <p className="mt-4 text-lg text-zinc-400 max-w-4xl mx-auto leading-relaxed">
          {subtitle}
        </p>
      )}
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
      whileHover={{ y: -5, scale: 1.02 }}
      className={`group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-white/8 via-white/4 to-transparent p-6 backdrop-blur-sm transition-all duration-300 hover:border-amber-400/30 hover:shadow-2xl hover:shadow-amber-400/10 ${className ?? ''}`}
    >
      {/* Subtle glow effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-amber-400/5 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100 rounded-2xl"></div>

      {img && (
        <div className="relative mb-6 overflow-hidden rounded-xl bg-gradient-to-br from-zinc-900 to-black ring-1 ring-white/10">
          <img
            src={img}
            alt={title}
            className={`h-44 w-full object-contain opacity-90 transition-all duration-300 group-hover:opacity-100 group-hover:scale-105 ${imgClassName ?? ''}`}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
        </div>
      )}

      <div className="relative z-10">
        <h3 className="text-xl font-bold text-white mb-3 group-hover:text-amber-100 transition-colors duration-300">
          {title}
        </h3>
        <p className="text-zinc-400 leading-relaxed group-hover:text-zinc-300 transition-colors duration-300">
          {desc}
        </p>
      </div>

      {/* Corner accent */}
      <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-bl from-amber-400/10 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
    </motion.div>
  );
}

export default function AitechSections() {
  return (
    <div className="relative">
      {/* Partners / Integrations - Infinite Scroll */}
      <section className="mx-auto max-w-7xl px-6 py-16">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.25em] text-amber-400/60 font-medium mb-2">
            <div className="w-6 h-px bg-gradient-to-r from-transparent to-amber-400/30"></div>
            Trusted Integrations
            <div className="w-6 h-px bg-gradient-to-l from-transparent to-amber-400/30"></div>
          </div>
          <p className="text-zinc-500 text-sm">Powered by industry-leading protocols and infrastructure</p>
        </div>

        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-white/5 via-transparent to-white/5 py-8">
          {/* Gradient overlays for smooth fade */}
          <div className="absolute left-0 top-0 bottom-0 w-20 bg-gradient-to-r from-black to-transparent z-10"></div>
          <div className="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-black to-transparent z-10"></div>

          <div className="flex animate-scroll-left space-x-12">
            {/* First set of logos */}
            {[
              "/partners/0x.png", "/partners/aave.png", "/partners/alchemy.png", "/partners/balancer.png",
              "/partners/base.png", "/partners/bitquery.jpg", "/partners/chainlink.png", "/partners/clerk.jpg",
              "/partners/cowdao.png", "/partners/curve.png", "/partners/dune.png", "/partners/ethereum.png",
              "/partners/metamask.png", "/partners/postgre.png", "/partners/quicknode.png", "/partners/replicate.png",
              "/partners/supabase.png", "/partners/sushi.png", "/partners/uniswap.png", "/partners/vercel.png"
            ].map((src, i) => (
              <img
                key={i}
                src={src}
                alt="partner logo"
                className="h-14 w-24 object-contain grayscale opacity-60 hover:opacity-100 hover:grayscale-0 transition-all duration-300 flex-shrink-0 filter brightness-110"
              />
            ))}
            {/* Duplicate set for seamless loop */}
            {[
              "/partners/0x.png", "/partners/aave.png", "/partners/alchemy.png", "/partners/balancer.png",
              "/partners/base.png", "/partners/bitquery.jpg", "/partners/chainlink.png", "/partners/clerk.jpg",
              "/partners/cowdao.png", "/partners/curve.png", "/partners/dune.png", "/partners/ethereum.png",
              "/partners/metamask.png", "/partners/postgre.png", "/partners/quicknode.png", "/partners/replicate.png",
              "/partners/supabase.png", "/partners/sushi.png", "/partners/uniswap.png", "/partners/vercel.png"
            ].map((src, i) => (
              <img
                key={`dup-${i}`}
                src={src}
                alt="partner logo"
                className="h-14 w-24 object-contain grayscale opacity-60 hover:opacity-100 hover:grayscale-0 transition-all duration-300 flex-shrink-0 filter brightness-110"
              />
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
              className="absolute inset-0 animate-spinY will-change-transform preserve-3d"
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

