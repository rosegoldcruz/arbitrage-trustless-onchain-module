"use client";

import { SignIn } from "@clerk/nextjs";
import { dark } from "@clerk/themes";

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-6">
      <SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" redirectUrl="/dashboard" appearance={{ baseTheme: dark as any }} />
    </div>
  );
}

