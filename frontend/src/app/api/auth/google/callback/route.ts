import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api";

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
            });

            if (data.refresh_token) {
                res.cookies.set("refresh_token", data.refresh_token, {
                    httpOnly: true,
                    secure: process.env.NODE_ENV === "production",
                    sameSite: "lax",
                    maxAge: 60 * 60 * 24 * 30, // 30 days
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
