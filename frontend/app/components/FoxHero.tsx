"use client";

import Image from "next/image";
import { useEffect, useRef } from "react";

/**
 * FoxHero — cursor-reactive fox head hero
 * Default image is /33f.png from public
 */

type Props = {
  src?: string;
  title?: string;
  subtitle?: string;
};

export default function FoxHero({
  src = "/33f.png",
  title = "Powered by the Advanced Efficient Optimized Network",
  subtitle,
}: Props) {
  const heroRef = useRef<HTMLDivElement | null>(null);
  const headRef = useRef<HTMLDivElement | null>(null);
  const eyesRef = useRef<HTMLDivElement | null>(null);
  const glowRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const hero = heroRef.current;
    const head = headRef.current;
    const eyes = eyesRef.current;
    const glow = glowRef.current;
    if (!hero || !head || !eyes || !glow) return;

    // Respect user preference
    const reduceMotion =
      typeof window !== "undefined" &&
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let raf = 0;
    let target = { rx: 0, ry: 0, tz: 0, ex: 0, ey: 0, gx: 0, gy: 0 };
    const current = { ...target } as typeof target;

    const clamp = (v: number, min: number, max: number) => Math.max(min, Math.min(max, v));

    const onMove = (e: PointerEvent) => {
      const rect = hero.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // normalized center (-1..1)
      const nx = (x / rect.width) * 2 - 1;
      const ny = (y / rect.height) * 2 - 1;

      // Map to rotations (MetaMask-ish tilt)
      const maxTilt = 12; // degrees
      const maxPan = 14; // px translate for parallax
      const eyePan = 10; // px eye/parallax
      const glowPan = 30; // px hero spotlight

      target.ry = clamp(-nx * maxTilt, -maxTilt, maxTilt); // Y-rotation (left/right)
      target.rx = clamp(ny * maxTilt, -maxTilt, maxTilt); // X-rotation (up/down)
      target.tz = clamp((1 - Math.hypot(nx, ny)) * 24, 0, 24); // slight pop-out
      target.ex = clamp(nx * eyePan, -eyePan, eyePan);
      target.ey = clamp(ny * eyePan, -eyePan, eyePan);
      target.gx = clamp(nx * glowPan, -glowPan, glowPan);
      target.gy = clamp(ny * glowPan, -glowPan, glowPan);

      if (!raf) raf = requestAnimationFrame(tick);
    };

    const onLeave = () => {
      target = { rx: 0, ry: 0, tz: 0, ex: 0, ey: 0, gx: 0, gy: 0 };
      if (!raf) raf = requestAnimationFrame(tick);
    };

    const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

    const tick = () => {
      raf = 0;
      const ease = reduceMotion ? 1 : 0.12;

      current.rx = lerp(current.rx, target.rx, ease);
      current.ry = lerp(current.ry, target.ry, ease);
      current.tz = lerp(current.tz, target.tz, ease);
      current.ex = lerp(current.ex, target.ex, ease);
      current.ey = lerp(current.ey, target.ey, ease);
      current.gx = lerp(current.gx, target.gx, ease);
      current.gy = lerp(current.gy, target.gy, ease);

      head.style.transform = `perspective(900px) rotateX(${current.rx}deg) rotateY(${current.ry}deg) translateZ(${current.tz}px)`;
      eyes.style.transform = `translate(${current.ex}px, ${current.ey}px)`;
      glow.style.transform = `translate(${current.gx}px, ${current.gy}px)`;

      // keep animating until we settle
      const err =
        Math.abs(current.rx - target.rx) +
        Math.abs(current.ry - target.ry) +
        Math.abs(current.tz - target.tz);
      if (err > 0.02 && !reduceMotion) raf = requestAnimationFrame(tick);
    };

    hero.addEventListener("pointermove", onMove, { passive: true });
    hero.addEventListener("pointerleave", onLeave);

    return () => {
      hero.removeEventListener("pointermove", onMove);
      hero.removeEventListener("pointerleave", onLeave);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <section
      ref={heroRef}
      className="
        relative isolate w-full h-[72vh] min-h-[520px] overflow-hidden
        bg-black text-white
        flex items-center justify-center
      "
    >
      {/* Soft concentric rings background */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-60"
        style={{
          background:
            "radial-gradient(closest-side, rgba(255,255,255,0.06), transparent 60%)",
        }}
      />

      {/* Movable golden glow that follows cursor */}
      <div
        ref={glowRef}
        aria-hidden="true"
        className="pointer-events-none absolute size-[520px] rounded-full blur-3xl opacity-40"
        style={{
          background:
            "radial-gradient(circle, rgba(255,185,80,0.35) 0%, rgba(255,140,0,0.08) 40%, transparent 70%)",
        }}
      />

      {/* Fox head container with perspective */}
      <div
        ref={headRef}
        className="relative will-change-transform select-none"
        style={{ transformStyle: "preserve-3d" }}
      >
        {/* The fox image */}
        <Image
          src={src}
          alt="Vulpine — AEON interface"
          width={520}
          height={520}
          priority
          className="pointer-events-none drop-shadow-[0_20px_40px_rgba(255,160,60,0.25)]"
        />

        {/* Eye/glow layer (parallax) — optional: position over eye area */}
        <div
          ref={eyesRef}
          aria-hidden="true"
          className="absolute left-1/2 top-[55%] -translate-x-1/2 -translate-y-1/2"
        >
          <div
            className="h-24 w-40 rounded-full blur-2xl opacity-70"
            style={{
              background:
                "radial-gradient(60% 60% at 50% 50%, rgba(255,180,70,0.9), rgba(255,120,40,0.35), transparent 70%)",
            }}
          />
        </div>
      </div>

      {/* Copy */}
      <div className="absolute bottom-10 w-full px-6 text-center">
        <p className="text-lg text-zinc-200 font-medium">
          Powered by the{" "}
          <span className="font-bold text-amber-400 bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
            Advanced Efficient Optimized Network
          </span>
        </p>
        {subtitle && (
          <p className="mt-3 text-sm text-zinc-400">{subtitle}</p>
        )}

        {/* Additional tagline */}
        <div className="mt-4 flex items-center justify-center gap-2 text-xs text-zinc-500">
          <div className="w-8 h-px bg-gradient-to-r from-transparent to-zinc-600"></div>
          <span className="uppercase tracking-wider">Zero-Capital DeFi Arbitrage</span>
          <div className="w-8 h-px bg-gradient-to-l from-transparent to-zinc-600"></div>
        </div>
      </div>


    </section>
  );
}

