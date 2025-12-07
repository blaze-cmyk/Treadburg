"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function SuccessPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const sessionId = searchParams.get("session_id");

    useEffect(() => {
        // Redirect to billing page after 3 seconds
        const timer = setTimeout(() => {
            router.push("/billing");
        }, 3000);

        return () => clearTimeout(timer);
    }, [router]);

    return (
        <div className="min-h-screen bg-[var(--tradeberg-bg)] text-white flex items-center justify-center">
            <div className="text-center max-w-md">
                <div className="mb-8">
                    <svg
                        className="w-24 h-24 text-green-400 mx-auto"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                    </svg>
                </div>
                <h1 className="text-4xl font-bold mb-4">Payment Successful!</h1>
                <p className="text-xl text-gray-400 mb-8">
                    Thank you for your subscription. Your account has been upgraded.
                </p>
                <p className="text-sm text-gray-500">
                    Redirecting to billing dashboard...
                </p>
            </div>
        </div>
    );
}
