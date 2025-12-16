export function LoadingSpinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
    const sizeClasses = {
        sm: "w-4 h-4 border-2",
        md: "w-8 h-8 border-3",
        lg: "w-12 h-12 border-4",
    };

    return (
        <div
            className={`${sizeClasses[size]} border-[var(--tradeberg-accent-color)] border-t-transparent rounded-full animate-spin`}
        />
    );
}

export function LoadingPage() {
    return (
        <div className="flex items-center justify-center min-h-screen bg-[var(--tradeberg-bg)]">
            <div className="text-center">
                <LoadingSpinner size="lg" />
                <p className="mt-4 text-muted-foreground">Loading...</p>
            </div>
        </div>
    );
}

export function LoadingSkeleton({ className }: { className?: string }) {
    return (
        <div
            className={`animate-pulse bg-[var(--tradeberg-card-bg)] rounded ${className || "h-4 w-full"}`}
        />
    );
}

export function ProfileSkeleton() {
    return (
        <div className="space-y-6 animate-pulse">
            <div className="flex items-center gap-4">
                <div className="w-20 h-20 rounded-full bg-[var(--tradeberg-card-bg)]" />
                <div className="space-y-2 flex-1">
                    <div className="h-6 bg-[var(--tradeberg-card-bg)] rounded w-1/3" />
                    <div className="h-4 bg-[var(--tradeberg-card-bg)] rounded w-1/4" />
                </div>
            </div>
            <div className="space-y-3">
                <div className="h-4 bg-[var(--tradeberg-card-bg)] rounded w-full" />
                <div className="h-4 bg-[var(--tradeberg-card-bg)] rounded w-5/6" />
                <div className="h-4 bg-[var(--tradeberg-card-bg)] rounded w-4/6" />
            </div>
        </div>
    );
}

export function PricingCardSkeleton() {
    return (
        <div className="border border-[var(--tradeberg-card-border)] rounded-xl p-6 space-y-4 animate-pulse">
            <div className="h-6 bg-[var(--tradeberg-card-bg)] rounded w-1/3" />
            <div className="h-10 bg-[var(--tradeberg-card-bg)] rounded w-1/2" />
            <div className="space-y-2">
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="h-4 bg-[var(--tradeberg-card-bg)] rounded" />
                ))}
            </div>
            <div className="h-12 bg-[var(--tradeberg-card-bg)] rounded" />
        </div>
    );
}
