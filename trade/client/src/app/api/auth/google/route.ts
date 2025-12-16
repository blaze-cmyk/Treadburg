import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api";

export async function POST(request: NextRequest) {
    try {
        const { redirectUrl } = await request.json();

        const response = await fetch(`${BACKEND_URL}/auth/google/init`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ redirect_url: redirectUrl }),
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
