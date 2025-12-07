"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface SubscriptionTier {
  id: string;
  name: string;
  price_monthly: number;
  price_yearly: number;
  stripe_price_id_monthly?: string;
  stripe_price_id_yearly?: string;
  features: string[];
  popular: boolean;
}

interface CreditPackage {
  id: string;
  name: string;
  credits: number;
  price: number;
  stripe_price_id?: string;
  savings?: string;
}

export default function PricingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [billingPeriod, setBillingPeriod] = useState<"monthly" | "yearly">("monthly");
  const [subscriptions, setSubscriptions] = useState<SubscriptionTier[]>([]);
  const [creditPackages, setCreditPackages] = useState<CreditPackage[]>([]);

  useEffect(() => {
    fetchPricing();
  }, []);

  const fetchPricing = async () => {
    try {
      const response = await fetch("/api/billing/pricing");
      const data = await response.json();

      if (data.success) {
        setSubscriptions(data.subscriptions || []);
        setCreditPackages(data.credits || []);
      }
    } catch (error) {
      console.error("Error fetching pricing:", error);
    }
  };

  const handleSubscribe = async (priceId: string | undefined) => {
    if (!priceId) {
      alert("Price ID not configured. Please contact support.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/billing/create-checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          price_id: priceId,
          mode: "subscription"
        })
      });

      const data = await response.json();

      if (data.success && data.url) {
        window.location.href = data.url;
      } else {
        alert("Failed to create checkout session");
      }
    } catch (error) {
      console.error("Error creating checkout:", error);
      alert("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleBuyCredits = async (priceId: string | undefined) => {
    if (!priceId) {
      alert("Price ID not configured. Please contact support.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/billing/create-checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          price_id: priceId,
          mode: "payment"
        })
      });

      const data = await response.json();

      if (data.success && data.url) {
        window.location.href = data.url;
      } else {
        alert("Failed to create checkout session");
      }
    } catch (error) {
      console.error("Error creating checkout:", error);
      alert("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--tradeberg-bg)] text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4">Choose Your Plan</h1>
          <p className="text-xl text-gray-400">
            Unlock the full power of AI-driven trading analysis
          </p>
        </div>

        {/* Billing Period Toggle */}
        <div className="flex justify-center mb-12">
          <div className="bg-gray-800 rounded-lg p-1 inline-flex">
            <button
              onClick={() => setBillingPeriod("monthly")}
              className={`px-6 py-2 rounded-md transition-colors ${billingPeriod === "monthly"
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white"
                }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod("yearly")}
              className={`px-6 py-2 rounded-md transition-colors ${billingPeriod === "yearly"
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white"
                }`}
            >
              Yearly
              <span className="ml-2 text-sm text-green-400">(Save 17%)</span>
            </button>
          </div>
        </div>

        {/* Subscription Tiers */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {subscriptions.map((tier) => (
            <div
              key={tier.id}
              className={`relative rounded-2xl p-8 ${tier.popular
                  ? "bg-gradient-to-br from-blue-600 to-purple-600 transform scale-105"
                  : "bg-gray-800"
                }`}
            >
              {tier.popular && (
                <div className="absolute top-0 right-0 bg-yellow-500 text-black px-4 py-1 rounded-bl-lg rounded-tr-2xl text-sm font-bold">
                  POPULAR
                </div>
              )}

              <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
              <div className="mb-6">
                <span className="text-4xl font-bold">
                  ${billingPeriod === "monthly" ? tier.price_monthly : Math.round(tier.price_yearly / 12)}
                </span>
                <span className="text-gray-400">/month</span>
                {billingPeriod === "yearly" && (
                  <div className="text-sm text-gray-400 mt-1">
                    Billed ${tier.price_yearly}/year
                  </div>
                )}
              </div>

              <ul className="space-y-3 mb-8">
                {tier.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <svg
                      className="w-5 h-5 text-green-400 mr-2 mt-0.5 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => {
                  if (tier.id === "free") {
                    router.push("/");
                  } else {
                    const priceId = billingPeriod === "monthly"
                      ? tier.stripe_price_id_monthly
                      : tier.stripe_price_id_yearly;
                    handleSubscribe(priceId);
                  }
                }}
                disabled={loading}
                className={`w-full py-3 rounded-lg font-semibold transition-colors ${tier.popular
                    ? "bg-white text-blue-600 hover:bg-gray-100"
                    : "bg-blue-600 hover:bg-blue-700 text-white"
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {tier.id === "free" ? "Get Started" : loading ? "Processing..." : "Subscribe Now"}
              </button>
            </div>
          ))}
        </div>

        {/* Credit Packages */}
        <div className="border-t border-gray-700 pt-16">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">One-Time Credit Packages</h2>
            <p className="text-xl text-gray-400">
              Purchase credits for pay-as-you-go usage
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {creditPackages.map((pkg) => (
              <div
                key={pkg.id}
                className="bg-gray-800 rounded-2xl p-8 hover:bg-gray-750 transition-colors"
              >
                <h3 className="text-2xl font-bold mb-2">{pkg.name}</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold">${pkg.price}</span>
                  {pkg.savings && (
                    <span className="ml-2 text-sm text-green-400">{pkg.savings}</span>
                  )}
                </div>
                <p className="text-gray-400 mb-6">{pkg.credits} credits</p>

                <button
                  onClick={() => handleBuyCredits(pkg.stripe_price_id)}
                  disabled={loading}
                  className="w-full py-3 rounded-lg font-semibold bg-gray-700 hover:bg-gray-600 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "Processing..." : "Buy Now"}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-16 text-center">
          <h3 className="text-2xl font-bold mb-4">Questions?</h3>
          <p className="text-gray-400 mb-4">
            Contact us at{" "}
            <a href="mailto:support@tradeberg.com" className="text-blue-400 hover:underline">
              support@tradeberg.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
