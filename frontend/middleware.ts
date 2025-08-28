import { clerkMiddleware } from "@clerk/nextjs/server";

export default clerkMiddleware(async (auth, req) => {
  await auth.protect();
});

// Only invoke Clerk on private zones. Do NOT include "/" here.
export const config = {
  matcher: [
    "/dashboard/:path*",      // authenticated app
    "/account/:path*",        // user settings area (if used)
    "/admin/:path*",          // admin area (if used)
    // Next API routes that require auth (most APIs are FastAPI on separate domain)
    "/api/private/:path*",
  ],
};
