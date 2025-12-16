import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api";

export async function GET(request: NextRequest) {
    try {
        // Get access token from backend cookies (NOT Supabase directly)
        const cookieStore = await cookies();
        const accessToken = cookieStore.get("access_token")?.value;

        if (!accessToken) {
            return NextResponse.json(
                { success: false, error: "Not authenticated" },
                { status: 401 }
            );
        }

        // Call backend with auth token
        const response = await fetch(`${BACKEND_URL}/users/profile`, {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Profile fetch error:", error);
        return NextResponse.json(
            { success: false, error: "Failed to fetch profile" },
            { status: 500 }
        );
    }
}

export async function PUT(request: NextRequest) {
    try {
        // Get access token from backend cookies (NOT Supabase directly)
        const cookieStore = await cookies();
        const accessToken = cookieStore.get("access_token")?.value;

        if (!accessToken) {
            return NextResponse.json(
                { success: false, error: "Not authenticated" },
                { status: 401 }
            );
        }

        const body = await request.json();

        // Call backend with auth token
        const response = await fetch(`${BACKEND_URL}/users/profile`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify(body),
        });

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Profile update error:", error);
        return NextResponse.json(
            { success: false, error: "Failed to update profile" },
            { status: 500 }
        );
    }
}
