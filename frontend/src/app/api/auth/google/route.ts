import { NextRequest, NextResponse } from "next/server";
import { headers } from "next/headers";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api";

export async function POST(request: NextRequest) {
    try {
        const headersList = await headers();
        const host = headersList.get("host") || "localhost:3000";
        const protocol = host.includes("localhost") ? "http" : "https";

        // Build the callback URL dynamically based on the request
        const origin = `${protocol}://${host}`;
        const redirectUrl = `${origin}/api/auth/google/callback`;

        const response = await fetch(`${BACKEND_URL}/auth/google/init?redirect_url=${encodeURIComponent(redirectUrl)}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        });

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Google auth init error:", error);
        return NextResponse.json(
            { success: false, message: "Failed to initialize Google auth" },
            { status: 500 }
        );
    }
}
