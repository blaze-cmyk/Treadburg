import { NextResponse } from "next/server";

// Mock version - returns empty array for UI-only mode
export async function GET() {
  try {
    // Return empty array - UI will work without chats
    return NextResponse.json([], { status: 200 });
  } catch (error) {
    console.log(error);
    return NextResponse.json(
      { error: "Something went wrong!" },
      { status: 500 }
    );
  }
}
