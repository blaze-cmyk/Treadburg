import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        const response = await fetch(`${BACKEND_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });

        const data = await response.json();

        if (!response.ok) {
            return NextResponse.json(data, { status: response.status });
        }

        // Set auth token in httpOnly cookie
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
        console.error("Login API error:", error);
        return NextResponse.json(
            { success: false, message: "Login failed" },
            { status: 500 }
        );
    }
}
