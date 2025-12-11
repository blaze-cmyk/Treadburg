import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api";

// GET handler - Google redirects here with the authorization code
export async function GET(request: NextRequest) {
    try {
        const searchParams = request.nextUrl.searchParams;
        const code = searchParams.get("code");
        const error = searchParams.get("error");

        // Handle OAuth errors
        if (error) {
            console.error("Google OAuth error:", error);
            return NextResponse.redirect(new URL(`/login?error=${error}`, request.url));
        }

        if (!code) {
            console.error("No authorization code received");
            return NextResponse.redirect(new URL("/login?error=no_code", request.url));
        }

        // Exchange code for tokens via backend
        const response = await fetch(`${BACKEND_URL}/auth/google/callback`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ code }),
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            console.error("Backend Google callback failed:", data);
            return NextResponse.redirect(new URL(`/login?error=auth_failed`, request.url));
        }

        // Set auth tokens in httpOnly cookies
        const redirectResponse = NextResponse.redirect(new URL("/dashboard", request.url));
        
        if (data.access_token) {
            redirectResponse.cookies.set("access_token", data.access_token, {
                httpOnly: true,
                secure: process.env.NODE_ENV === "production",
                sameSite: "lax",
                maxAge: 60 * 60 * 24 * 7, // 7 days
                path: "/",
            });

            if (data.refresh_token) {
                redirectResponse.cookies.set("refresh_token", data.refresh_token, {
                    httpOnly: true,
                    secure: process.env.NODE_ENV === "production",
                    sameSite: "lax",
                    maxAge: 60 * 60 * 24 * 30, // 30 days
                    path: "/",
                });
            }
        }

        return redirectResponse;
    } catch (error) {
        console.error("Google callback error:", error);
        return NextResponse.redirect(new URL("/login?error=unexpected", request.url));
    }
}

// POST handler - for programmatic calls (kept for backward compatibility)
export async function POST(request: NextRequest) {
    try {
        const { code } = await request.json();

        const response = await fetch(`${BACKEND_URL}/auth/google/callback`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ code }),
        });

        const data = await response.json();

        if (!response.ok) {
            return NextResponse.json(data, { status: response.status });
        }

        // Set auth tokens in httpOnly cookies
        const res = NextResponse.json(data);
        if (data.access_token) {
            res.cookies.set("access_token", data.access_token, {
                httpOnly: true,
                secure: process.env.NODE_ENV === "production",
                sameSite: "lax",
                maxAge: 60 * 60 * 24 * 7, // 7 days
                path: "/",
            });

            if (data.refresh_token) {
                res.cookies.set("refresh_token", data.refresh_token, {
                    httpOnly: true,
                    secure: process.env.NODE_ENV === "production",
                    sameSite: "lax",
                    maxAge: 60 * 60 * 24 * 30, // 30 days
                    path: "/",
                });
            }
        }

        return res;
    } catch (error) {
        console.error("Google callback error:", error);
        return NextResponse.json(
            { success: false, message: "Google authentication failed" },
            { status: 500 }
        );
    }
}
