"use client";

import { SignIn } from "@clerk/nextjs";
import { dark } from "@clerk/themes";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-6">
      <SignIn routing="path" path="/login" signUpUrl="/register" redirectUrl="/dashboard" appearance={{ baseTheme: dark as any }} />
    </div>
  );
}
