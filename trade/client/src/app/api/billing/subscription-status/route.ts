import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api";

export async function GET(request: NextRequest) {
    const { searchParams } = new URL(request.url);
    const customerId = searchParams.get("customer_id");

    try {
        const url = customerId
            ? `${BACKEND_URL}/billing/subscription-status?customer_id=${customerId}`
            : `${BACKEND_URL}/billing/subscription-status`;

        const response = await fetch(url);
        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        return NextResponse.json(
            { success: false, error: "Failed to fetch subscription status" },
            { status: 500 }
        );
    }
}
