import { NextResponse } from "next/server";

const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api';

export async function GET() {
  try {
    // Proxy request to FastAPI backend
    const response = await fetch(`${BACKEND_API_URL}/chat`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
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
