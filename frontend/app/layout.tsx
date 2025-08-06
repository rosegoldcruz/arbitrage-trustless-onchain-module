import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { dark } from "@clerk/themes";

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
    <ClerkProvider>
      <html lang="en" className="dark">
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased bg-black text-white min-h-screen`}
        >
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
