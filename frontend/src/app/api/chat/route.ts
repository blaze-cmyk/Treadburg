import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8080/api';

export async function GET(request: NextRequest) {
  try {
    // Get access token from cookies
    const cookieStore = await cookies();
    const accessToken = cookieStore.get("access_token")?.value;

    if (!accessToken) {
      console.error('No access token found in cookies');
      return NextResponse.json([], { status: 200 });
    }

    // Proxy request to FastAPI backend with user token
    const response = await fetch(`${BACKEND_API_URL}/chat`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      console.error('Backend error:', response.status);
      // Return empty array on error so frontend doesn't break
      return NextResponse.json([], { status: 200 });
    }

    const data = await response.json();
    
    // Ensure we always return an array
    if (!Array.isArray(data)) {
      console.error('Backend returned non-array:', data);
      return NextResponse.json([], { status: 200 });
    }
    
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error('Error fetching chats:', error);
    // Return empty array on error so frontend doesn't break
    return NextResponse.json([], { status: 200 });
  }
}
