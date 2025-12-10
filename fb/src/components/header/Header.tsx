"use client";

import { Button } from "@/components/ui/button";
import { Sparkle } from "lucide-react";
import ThemeToggle from "@/components/theme/ThemeToggle";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useUser } from "@/contexts/UserContext";

export default function Header() {
  const { profile } = useUser();
  const router = useRouter();
  const pathname = usePathname();

  const showCenterUpgradeButton =
    pathname !== "/trade" && pathname !== "/charts";

  // On Trade & Historical charts pages, the header is handled inside the right chat panel.
  if (pathname === "/trade" || pathname === "/charts") {
    return null;
  }

  return (
    <header
      className="p-2 flex items-center justify-between bg-transparent dark:bg-background"
      suppressHydrationWarning
    >
      <div className="flex items-center">{/* Left side intentionally empty */}</div>
      <div>
        {showCenterUpgradeButton && (
          <Button
            variant="outline"
            className="text-[#5d5bd0] border-0 bg-[#f1f1fb] hover:text-[#5d5bd0] hover:bg-[#f1f1fb] cursor-pointer"
            asChild
          >
            <Link href="/pricing">
              <Sparkle />
              Upgrade to Pro
            </Link>
          </Button>
        )}
      </div>
      <div className="flex items-center gap-2">
        <ThemeToggle />
      </div>
    </header>
  );
}
