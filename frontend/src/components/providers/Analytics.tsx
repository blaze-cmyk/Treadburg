"use client";

import { useEffect, Suspense } from "react";
import { usePathname, useSearchParams } from "next/navigation";

declare global {
    interface Window {
        gtag?: (...args: any[]) => void;
    }
}

// Inner component that uses useSearchParams
function AnalyticsContent() {
    const pathname = usePathname();
    const searchParams = useSearchParams();

    useEffect(() => {
        if (typeof window.gtag !== "undefined") {
            window.gtag("config", process.env.NEXT_PUBLIC_GA_ID || "", {
                page_path: pathname + (searchParams?.toString() ? `?${searchParams.toString()}` : ""),
            });
        }
    }, [pathname, searchParams]);

    return null;
}

// Main Analytics component wrapped in Suspense
export function Analytics() {
    // Only render in production
    if (process.env.NODE_ENV !== "production" || !process.env.NEXT_PUBLIC_GA_ID) {
        return null;
    }

    return (
        <>
            <script async src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`} />
            <script
                dangerouslySetInnerHTML={{
                    __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}', {
              page_path: window.location.pathname,
            });
          `,
                }}
            />
            <Suspense fallback={null}>
                <AnalyticsContent />
            </Suspense>
        </>
    );
}

// Event tracking helpers
export const trackEvent = (action: string, category: string, label?: string, value?: number) => {
    if (typeof window.gtag !== "undefined") {
        window.gtag("event", action, {
            event_category: category,
            event_label: label,
            value,
        });
    }
};

export const trackPurchase = (value: number, currency: string = "USD", items?: any[]) => {
    if (typeof window.gtag !== "undefined") {
        window.gtag("event", "purchase", {
            currency,
            value,
            items,
        });
    }
};

export const trackSignup = (method: string) => {
    if (typeof window.gtag !== "undefined") {
        window.gtag("event", "sign_up", {
            method,
        });
    }
};

export const trackLogin = (method: string) => {
    if (typeof window.gtag !== "undefined") {
        window.gtag("event", "login", {
            method,
        });
    }
};
