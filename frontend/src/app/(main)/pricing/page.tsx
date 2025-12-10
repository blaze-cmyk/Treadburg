"use client";

import { motion } from "framer-motion";
import {
  Check,
  Sparkles,
  Zap,
  Crown,
  MessageSquare,
  TrendingUp,
  Shield,
  Headphones,
  Code,
  BarChart3,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { useMouseWheelScroll } from "@/hooks/use-mouse-wheel-scroll";
import { useRouter } from "next/navigation";

interface PricingTier {
  id: string;
  name: string;
  price_monthly: number;
  price_yearly: number;
  features: string[];
  popular: boolean;
  stripe_price_id_monthly?: string;
  stripe_price_id_yearly?: string;
}

interface PricingData {
  success: boolean;
  subscriptions: PricingTier[];
}

const tierIcons: Record<string, any> = {
  free: Sparkles,
  pro: Zap,
  max: Crown,
};

const featureIcons: Record<string, any> = {
  default: Check,
  "Unlimited messages": MessageSquare,
  "Advanced AI": TrendingUp,
  "SEC filing analysis": BarChart3,
  "Priority support": Headphones,
  "API access": Code,
  "Dedicated support": Shield,
};

export default function PricingPage() {
  const [billingPeriod, setBillingPeriod] = useState<"monthly" | "yearly">("monthly");
  const [pricingData, setPricingData] = useState<PricingTier[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useMouseWheelScroll<HTMLDivElement>();
  const router = useRouter();

  useEffect(() => {
    fetchPricing();
  }, []);

  const fetchPricing = async () => {
    try {
      const response = await fetch("/api/billing/pricing");
      const data: PricingData = await response.json();

      if (data.success && data.subscriptions) {
        setPricingData(data.subscriptions);
      } else {
        setError("Failed to load pricing");
      }
    } catch (err) {
      setError("Failed to connect to server");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (tier: PricingTier) => {
    if (tier.id === "free") {
      return; // Already free tier
    }

    const priceId = billingPeriod === "monthly"
      ? tier.stripe_price_id_monthly
      : tier.stripe_price_id_yearly;

    if (!priceId) {
      alert("Price ID not configured. Please contact support.");
      return;
    }

    try {
      const response = await fetch("/api/billing/create-checkout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          price_id: priceId,
          mode: "subscription",
          success_url: `${window.location.origin}/billing/success?session_id={CHECKOUT_SESSION_ID}`,
          cancel_url: `${window.location.origin}/pricing`,
        }),
      });

      const data = await response.json();

      if (data.success && data.url) {
        // Redirect to Stripe Checkout
        window.location.href = data.url;
      } else {
        alert(data.error || "Failed to create checkout session");
      }
    } catch (err) {
      alert("Failed to initiate checkout. Please try again.");
      console.error(err);
    }
  };

  const getPrice = (tier: PricingTier) => {
    if (tier.price_monthly === 0) return "$0";
    const price = billingPeriod === "monthly" ? tier.price_monthly : tier.price_yearly;
    return `$${price}`;
  };

  const getPeriodLabel = () => {
    return billingPeriod === "monthly" ? "per month" : "per year";
  };

  const getSavings = (tier: PricingTier) => {
    if (billingPeriod === "yearly" && tier.price_yearly > 0) {
      const monthlyCost = tier.price_monthly * 12;
      const yearlyCost = tier.price_yearly;
      const savings = monthlyCost - yearlyCost;
      if (savings > 0) {
        return `Save $${savings}`;
      }
    }
    return null;
  };

  const getFeatureIcon = (feature: string) => {
    for (const [key, Icon] of Object.entries(featureIcons)) {
      if (feature.includes(key)) {
        return Icon;
      }
    }
    return featureIcons.default;
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center h-full bg-background">
        <div className="text-foreground">Loading pricing...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center h-full bg-background">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <Button onClick={fetchPricing}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={scrollRef}
      className="flex-1 flex flex-col h-full overflow-y-auto show-scrollbar-on-hover bg-background"
    >
      <div className="max-w-7xl mx-auto px-4 py-12 w-full">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold text-foreground mb-4">
            Choose Your Plan
          </h1>
          <p className="text-muted-foreground text-lg mb-8">
            Unlock the full power of AI-driven trading insights
          </p>

          {/* Billing Period Toggle */}
          <div className="inline-flex rounded-full border border-[var(--tradeberg-card-border)] bg-[var(--tradeberg-card-bg)] p-1 shadow-[0_10px_30px_rgba(0,0,0,0.55)]">
            <button
              onClick={() => setBillingPeriod("monthly")}
              className={`px-6 py-2 rounded-full text-sm font-medium transition-colors ${billingPeriod === "monthly"
                  ? "bg-white text-black shadow-sm"
                  : "text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)]"
                }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod("yearly")}
              className={`px-6 py-2 rounded-full text-sm font-medium transition-colors ${billingPeriod === "yearly"
                  ? "bg-white text-black shadow-sm"
                  : "text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)]"
                }`}
            >
              Yearly
              <span className="ml-2 text-xs text-green-500">Save up to 17%</span>
            </button>
          </div>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {pricingData.map((tier, index) => {
            const TierIcon = tierIcons[tier.id] || Sparkles;
            const savings = getSavings(tier);

            return (
              <motion.div
                key={tier.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className={`flex flex-col rounded-2xl p-8 bg-[var(--tradeberg-card-bg)] border shadow-[0_20px_45px_rgba(0,0,0,0.65)] relative ${tier.popular
                    ? "border-[var(--tradeberg-accent-color)] ring-2 ring-[var(--tradeberg-accent-color)]/20 scale-105"
                    : "border-[var(--tradeberg-card-border)]"
                  }`}
              >
                {/* Popular Badge */}
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-[var(--tradeberg-accent-color)] text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </div>
                )}

                {/* Icon */}
                <div className="mb-4">
                  <div className="w-12 h-12 rounded-lg bg-[var(--tradeberg-accent-color)]/10 flex items-center justify-center">
                    <TierIcon className="w-6 h-6 text-[var(--tradeberg-accent-color)]" />
                  </div>
                </div>

                {/* Tier Name */}
                <h3 className="text-2xl font-bold text-foreground mb-2">
                  {tier.name}
                </h3>

                {/* Price */}
                <div className="mb-6">
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold text-foreground">
                      {getPrice(tier)}
                    </span>
                    {tier.price_monthly > 0 && (
                      <span className="text-muted-foreground">
                        {getPeriodLabel()}
                      </span>
                    )}
                  </div>
                  {savings && (
                    <div className="mt-2 text-sm text-green-500 font-semibold">
                      {savings}
                    </div>
                  )}
                </div>

                {/* Subscribe Button */}
                <Button
                  onClick={() => handleSubscribe(tier)}
                  disabled={tier.id === "free"}
                  className={`w-full mb-6 rounded-full ${tier.popular
                      ? "bg-[var(--tradeberg-accent-color)] hover:bg-[var(--tradeberg-accent-color)]/90 text-white"
                      : "bg-white text-black hover:bg-gray-200"
                    }`}
                >
                  {tier.id === "free" ? "Current Plan" : `Get ${tier.name}`}
                </Button>

                {/* Features */}
                <ul className="space-y-3 flex-1">
                  {tier.features.map((feature, idx) => {
                    const FeatureIcon = getFeatureIcon(feature);
                    return (
                      <li key={idx} className="flex items-start gap-3">
                        <FeatureIcon className="w-5 h-5 text-[var(--tradeberg-accent-color)] flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-foreground">{feature}</span>
                      </li>
                    );
                  })}
                </ul>
              </motion.div>
            );
          })}
        </div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-12 text-center text-muted-foreground text-sm"
        >
          <p>
            All plans include a 14-day money-back guarantee.{" "}
            <a href="#" className="text-[var(--tradeberg-accent-color)] hover:underline">
              Learn more
            </a>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
