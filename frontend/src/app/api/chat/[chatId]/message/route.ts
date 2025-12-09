import { NextRequest, NextResponse } from "next/server";

const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8080/api';

// ------------------ GET Messages ------------------
export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ chatId: string }> }
) {
  try {
    const { chatId } = await params;

    // Proxy request to FastAPI backend
    const response = await fetch(`${BACKEND_API_URL}/chat/${chatId}/messages`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch messages' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error('Error fetching messages:', error);
    return NextResponse.json(
      { error: "Failed to connect to backend" },
      { status: 500 }
    );
  }
}

// ------------------ POST Messages / AI Response ------------------
export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ chatId: string }> }
) {
  try {
    const { chatId } = await params;
    const { userPrompt, attachments, mode } = await req.json();

    if (!userPrompt) {
      return new Response("No prompt provided", { status: 400 });
    }

    // Proxy streaming request to FastAPI backend
    console.log(`[STREAM] Calling backend: ${BACKEND_API_URL}/chat/${chatId}/stream`);
    console.log(`[STREAM] Prompt: ${userPrompt}`);

    const controller = new AbortController();
    const timeout = setTimeout(() => {
      controller.abort();
      console.log('[STREAM] Request timed out after 30s');
    }, 30000); // 30 second timeout

    const response = await fetch(`${BACKEND_API_URL}/chat/${chatId}/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ userPrompt, attachments, mode }),
      signal: controller.signal,
      // Important for Next.js - prevents caching
      cache: 'no-store',
    });

    clearTimeout(timeout);
    console.log(`[STREAM] Response status: ${response.status}`);

    // Handle non-streaming responses
    if (response.headers.get('content-type')?.includes('application/json')) {
      console.log('[STREAM] Received JSON response instead of stream');
      const data = await response.json();
      console.log('[STREAM] JSON data:', data);

      if (!response.ok) {
        return new Response(JSON.stringify({
          error: data.detail || 'Backend returned an error',
          data
        }), {
          status: response.status,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }

    if (!response.ok) {
      // Try to get error details as text first
      const errorText = await response.text().catch(() => '');
      console.log(`[STREAM] Error response: ${errorText}`);

      try {
        // Try to parse as JSON if possible
        const errorJson = JSON.parse(errorText);
        return new Response(
          JSON.stringify({
            error: errorJson.detail || 'Failed to stream response',
            details: errorJson
          }),
          {
            status: response.status,
            headers: { 'Content-Type': 'application/json' }
          }
        );
      } catch (e) {
        // Not JSON, return as text
        return new Response(
          errorText || 'Failed to stream response',
          { status: response.status }
        );
      }
    }

    // Set up proper headers for streaming
    const headers = new Headers();
    headers.set('Content-Type', 'text/plain; charset=utf-8');
    headers.set('Cache-Control', 'no-cache, no-transform');
    headers.set('Connection', 'keep-alive');
    headers.set('Transfer-Encoding', 'chunked');

    // Return the streaming response directly with proper headers
    return new Response(response.body, { headers });
  } catch (error) {
    console.error('Error streaming response:', error);

    // Format error message for debugging
    let errorMessage = 'Unknown error';
    let errorDetails = {};

    if (error instanceof Error) {
      errorMessage = error.message;
      errorDetails = {
        name: error.name,
        stack: error.stack,
        cause: error.cause,
      };

      // Check for network errors
      if (errorMessage.includes('ECONNREFUSED')) {
        errorMessage = 'Cannot connect to backend server. Is it running?';
      } else if (errorMessage.includes('ECONNRESET')) {
        errorMessage = 'Connection to backend server was reset. The server might be restarting.';
      } else if (errorMessage.includes('timeout')) {
        errorMessage = 'Request to backend server timed out after 30s.';
      } else if (errorMessage.includes('aborted')) {
        errorMessage = 'Request was aborted due to timeout.';
      }
    }

    console.error('Formatted error:', { errorMessage, errorDetails });

    return new Response(JSON.stringify({
      error: 'Failed to connect to backend',
      message: errorMessage,
      details: errorDetails
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store'
      }
    });
  }
}
