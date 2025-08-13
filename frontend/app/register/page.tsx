"use client";

import { SignUp } from "@clerk/nextjs";
import { dark } from "@clerk/themes";

export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-6">
      <SignUp routing="path" path="/register" signInUrl="/login" redirectUrl="/dashboard" appearance={{ baseTheme: dark as any }} />
    </div>
  );
}

