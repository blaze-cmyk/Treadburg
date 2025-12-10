import { NextResponse } from "next/server";

const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api';

export async function GET() {
  try {
    // Proxy request to FastAPI backend
    const response = await fetch(`${BACKEND_API_URL}/chat/limit`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch token limit' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error('Error fetching token limit:', error);
    // Fallback to mock data if backend is unavailable
    return NextResponse.json({ token: 15000 }, { status: 200 });
  }
}
