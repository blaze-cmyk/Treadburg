import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8080/api';

export async function POST(req: NextRequest) {
  try {
    // Get access token from cookies
    const cookieStore = await cookies();
    const accessToken = cookieStore.get("access_token")?.value;

    if (!accessToken) {
      return NextResponse.json(
        { error: 'Authentication required. Please log in.' },
        { status: 401 }
      );
    }

    const { prompt } = await req.json();

    // Allow empty prompt for new chat
    // if (!prompt) { ... }

    // Proxy request to FastAPI backend with user token
    const response = await fetch(`${BACKEND_API_URL}/chat/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || 'Failed to create chat' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error('Error creating chat:', error);
    return NextResponse.json(
      { error: "Failed to connect to backend" },
      { status: 500 }
    );
  }
}
