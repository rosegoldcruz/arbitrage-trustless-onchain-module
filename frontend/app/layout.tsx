import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ClerkProvider, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { dark } from "@clerk/themes";
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
    <ClerkProvider signInUrl="/sign-in" signUpUrl="/sign-up" afterSignInUrl="/dashboard" afterSignUpUrl="/dashboard" appearance={{ baseTheme: dark }}>
      <html lang="en" className="dark">
        <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-black text-white min-h-screen`}>
          {/* Global top nav with Clerk auth */}
          <header className="sticky top-0 z-50 border-b border-white/10 bg-black/60 backdrop-blur">
            <div className="mx-auto max-w-7xl px-6 py-3 flex items-center justify-between">
              <a href="/" className="flex items-center gap-2">
                <img src="/1.png" alt="ATOM" className="h-8 w-8 object-contain" />
                <span className="font-semibold tracking-wide">ATOM</span>
              </a>
              <nav className="flex items-center gap-4">
                <a href="/dashboard" className="text-white/80 hover:text-white">Dashboard</a>
                <SignedOut>
                  <a href="/sign-in" className="rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm hover:bg-white/20">Log in</a>
                </SignedOut>
                <SignedIn>
                  <UserButton afterSignOutUrl="/" appearance={{ baseTheme: dark }} />
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
