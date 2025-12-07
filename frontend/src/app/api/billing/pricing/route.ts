import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api";

export async function GET(request: NextRequest) {
    const { searchParams } = new URL(request.url);

    try {
        const response = await fetch(`${BACKEND_URL}/billing/pricing`);
        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        return NextResponse.json(
            { success: false, error: "Failed to fetch pricing" },
            { status: 500 }
        );
    }
}
