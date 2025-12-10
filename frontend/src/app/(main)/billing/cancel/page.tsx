"use client";

import { useRouter } from "next/navigation";

export const dynamic = 'force-dynamic';

export default function CancelPage() {
    const router = useRouter();

    return (
        <div className="min-h-screen bg-[var(--tradeberg-bg)] text-white flex items-center justify-center">
            <div className="text-center max-w-md">
                <div className="mb-8">
                    <svg
                        className="w-24 h-24 text-yellow-400 mx-auto"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                    </svg>
                </div>
                <h1 className="text-4xl font-bold mb-4">Payment Cancelled</h1>
                <p className="text-xl text-gray-400 mb-8">
                    Your payment was cancelled. No charges were made to your account.
                </p>
                <div className="space-x-4">
                    <button
                        onClick={() => router.push("/pricing")}
                        className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
                    >
                        View Plans
                    </button>
                    <button
                        onClick={() => router.push("/")}
                        className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg font-semibold transition-colors"
                    >
                        Go Home
                    </button>
                </div>
            </div>
        </div>
    );
}
