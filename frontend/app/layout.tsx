import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { ClerkProvider, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";

import { Analytics } from "@vercel/analytics/react";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ATOM - Arbitrage Trustless On-Chain Module",
  description: "Zero-capital DeFi arbitrage with flash loans + AI agents",
  keywords: ["DeFi", "arbitrage", "flash loans", "AI agents", "blockchain", "crypto"],
  authors: [{ name: "ATOM Team" }],
  openGraph: {
    title: "ATOM - Arbitrage Trustless On-Chain Module",
    description: "Zero-capital DeFi arbitrage with flash loans + AI agents",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider signInUrl="/sign-in" signUpUrl="/sign-up" afterSignInUrl="/dashboard" afterSignUpUrl="/dashboard">
      <html lang="en" className="dark">
        <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-black text-white min-h-screen`}>
          {/* Global top nav with Clerk auth */}
          <header className="sticky top-0 z-50 border-b border-white/10 bg-black/60 backdrop-blur">
            <div className="mx-auto max-w-7xl px-6 py-3 flex items-center justify-between">
              <Link href="/" className="flex items-center">
                <img src="/1.png" alt="ATOM Home" className="h-9 w-9 object-contain hover:opacity-90 transition-opacity" />
                <span className="sr-only">Home</span>
              </Link>
              <nav className="flex items-center gap-4">
                <SignedOut>
                  <Link href="/sign-in" className="rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm hover:bg-white/20">Sign in</Link>
                </SignedOut>
                <SignedIn>
                  <UserButton afterSignOutUrl="/" />
                </SignedIn>
              </nav>
            </div>
          </header>

          {children}
          <Analytics />
        </body>
      </html>
    </ClerkProvider>
  );
}
