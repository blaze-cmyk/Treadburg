import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api";

export async function POST(request: NextRequest) {
    try {
        const cookieStore = await cookies();
        const accessToken = cookieStore.get("access_token")?.value;

        if (accessToken) {
            // Call backend logout
            await fetch(`${BACKEND_URL}/auth/logout`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
            });
        }

        // Clear cookies
        const res = NextResponse.json({ success: true, message: "Logged out successfully" });
        res.cookies.delete("access_token");
        res.cookies.delete("refresh_token");

        return res;
    } catch (error) {
        console.error("Logout API error:", error);
        // Still clear cookies even if backend call fails
        const res = NextResponse.json({ success: true, message: "Logged out" });
        res.cookies.delete("access_token");
        res.cookies.delete("refresh_token");
        return res;
    }
}
