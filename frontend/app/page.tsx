"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, Zap, Shield, TrendingUp, Bot, Coins, Globe } from "lucide-react";
import Link from "next/link";
import { HeroSection } from "@/components/landing/HeroSection";
import { PlatformOverview } from "@/components/landing/PlatformOverview";
import { PricingSection } from "@/components/landing/PricingSection";
import { AboutSection } from "@/components/landing/AboutSection";
import { FAQSection } from "@/components/landing/FAQSection";
import { ContactSection } from "@/components/landing/ContactSection";
import { Navigation } from "@/components/landing/Navigation";
import { Footer } from "@/components/landing/Footer";


export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
      <Navigation />
      <HeroSection />
      <PlatformOverview />
      <PricingSection />
      <AboutSection />
      <FAQSection />
      <ContactSection />
      <Footer />
    </div>
  );
}
