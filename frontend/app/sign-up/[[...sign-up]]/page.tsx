"use client";

import { SignUp } from "@clerk/nextjs";
import { dark } from "@clerk/themes";

export default function SignUpPage() {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-6">
      <SignUp routing="path" path="/sign-up" signInUrl="/sign-in" redirectUrl="/dashboard" appearance={{ baseTheme: dark as any }} />
    </div>
  );
}

