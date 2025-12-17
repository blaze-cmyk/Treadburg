import { NextRequest, NextResponse } from "next/server";

// This route handles the redirect from backend after successful Google OAuth
// Backend redirects here with token parameter
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const token = searchParams.get("token");
    const newUser = searchParams.get("new_user");
    const error = searchParams.get("error");

    // Get the correct origin for redirects
    const origin = request.headers.get('origin') || request.nextUrl.origin;

    // Handle errors
    if (error) {
      console.error("OAuth callback error:", error);
      return NextResponse.redirect(new URL(`/login?error=${error}`, origin));
    }

    if (!token) {
      console.error("No token received from backend");
      return NextResponse.redirect(new URL("/login?error=no_token", origin));
    }

    // Create redirect response
    const redirectUrl = newUser === "true" ? "/?welcome=true" : "/";
    const redirectResponse = NextResponse.redirect(new URL(redirectUrl, origin));

    // Store token in httpOnly cookie
    redirectResponse.cookies.set("auth_token", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24, // 24 hours
      path: "/",
    });

    console.log("Successfully authenticated, redirecting to:", redirectUrl);
    return redirectResponse;
  } catch (error) {
    console.error("Callback handler error:", error);
    const origin = request.headers.get('origin') || request.nextUrl.origin;
    return NextResponse.redirect(new URL("/login?error=callback_failed", origin));
  }
}
