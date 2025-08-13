'use client';

import Link from "next/link";
import { usePathname } from "next/navigation";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="fixed top-0 inset-x-0 z-50 bg-black/60 backdrop-blur border-b border-white/10">
      <nav className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-6">
        {/* Left: logo → home */}
        <Link href="/" className="flex items-center gap-2">
          <img src="/1.png" alt="ATOM" className="h-9 w-9 object-contain hover:opacity-90 transition-opacity" />
        </Link>

        {/* Right: auth controls */}
        <div className="flex items-center gap-3">
          <SignedOut>
            <SignInButton mode="modal" signUpFallbackRedirectUrl="/dashboard" signInForceRedirectUrl="/dashboard" signUpForceRedirectUrl="/dashboard">
              <button
                className="rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm hover:bg-white/20 transition-colors"
                aria-label="Sign in"
              >
                Sign in
              </button>
            </SignInButton>
          </SignedOut>

          <SignedIn>
            <UserButton
              afterSignOutUrl="/"
              appearance={{
                elements: { 
                  userButtonBox: "ring-1 ring-white/10 rounded-full",
                  userButtonTrigger: "focus:shadow-none"
                },
              }}
            />
          </SignedIn>
        </div>
      </nav>
    </header>
  );
}

