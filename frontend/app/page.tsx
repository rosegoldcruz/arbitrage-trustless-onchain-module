"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowRight, Zap, Shield, TrendingUp } from "lucide-react";
import Link from "next/link";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";

import AtomHero3D from "./components/AtomHero3D";

export default function Home() {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 border-b border-gray-800">
        <div className="text-2xl font-bold">ATOM</div>
        <div className="flex items-center gap-4">
          <SignedOut>
            <SignInButton>
              <Button variant="outline" className="text-white border-white hover:bg-white hover:text-black">
                Sign In
              </Button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <Link href="/dashboard">
              <Button className="bg-blue-600 hover:bg-blue-700">
                Dashboard
              </Button>
            </Link>
            <UserButton />
          </SignedIn>
        </div>
      </nav>

      {/* Hero Section (3D) */}
      <div className="relative">
        {/* 3D Cinematic Hero */}
        <AtomHero3D />
      </div>

      {/* Existing Hero Content Below 3D */}
      <main className="flex flex-col items-center justify-center min-h-[60vh] text-center px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl"
        >
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
            ATOM
          </h1>
          <h2 className="text-3xl font-semibold mb-4">
            Arbitrage Trustless On-Chain Module
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Zero-capital DeFi arbitrage with flash loans + AI agents.
            Maximize yield through intelligent cross-DEX execution on Base L2. Dashboard Live!
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <SignedOut>
              <SignInButton>
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-3">
                  Get Started <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <Link href="/dashboard">
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-3">
                  Open Dashboard <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </SignedIn>
            <Button variant="outline" size="lg" className="text-white border-white hover:bg-white hover:text-black text-lg px-8 py-3">
              Learn More
            </Button>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="bg-gray-900 p-6 rounded-lg border border-gray-800"
            >
              <Zap className="h-12 w-12 text-blue-400 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-2">Flash Loans</h3>
              <p className="text-gray-400">Zero-capital arbitrage using AAVE flash loans for maximum efficiency</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="bg-gray-900 p-6 rounded-lg border border-gray-800"
            >
              <Shield className="h-12 w-12 text-green-400 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-2">AI Agents</h3>
              <p className="text-gray-400">Intelligent bots that monitor and execute profitable opportunities 24/7</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="bg-gray-900 p-6 rounded-lg border border-gray-800"
            >
              <TrendingUp className="h-12 w-12 text-purple-400 mb-4 mx-auto" />
              <h3 className="text-xl font-semibold mb-2">Base L2</h3>
              <p className="text-gray-400">Optimized for Base network with low fees and fast execution</p>
            </motion.div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
