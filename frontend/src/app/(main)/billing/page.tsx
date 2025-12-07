"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface Subscription {
  id: string;
  status: string;
  current_period_end: number;
  cancel_at_period_end: boolean;
  plan: string;
}

export default function BillingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [tier, setTier] = useState("free");

  useEffect(() => {
    fetchSubscriptionStatus();
  }, []);

  const fetchSubscriptionStatus = async () => {
    try {
      // TODO: Get actual customer_id from user session
      const customerId = null; // Replace with actual customer ID

      const response = await fetch(`/api/billing/subscription-status?customer_id=${customerId || ""}`);
      const data = await response.json();

      if (data.success) {
        setSubscription(data.subscription);
        setTier(data.tier);
      }
    } catch (error) {
      console.error("Error fetching subscription:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleManageSubscription = async () => {
    if (!subscription) {
      router.push("/pricing");
      return;
    }

    setLoading(true);
    try {
      // TODO: Get actual customer_id from user session
      const customerId = "cus_xxx"; // Replace with actual customer ID

      const response = await fetch("/api/billing/create-portal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: customerId
        })
      });

      const data = await response.json();

      if (data.success && data.url) {
        window.location.href = data.url;
      } else {
        alert("Failed to open customer portal");
      }
    } catch (error) {
      console.error("Error opening portal:", error);
      alert("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--tradeberg-bg)] text-white flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--tradeberg-bg)] text-white p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Billing & Subscription</h1>
          <p className="text-gray-400">Manage your subscription and payment methods</p>
        </div>

        {/* Current Plan */}
        <div className="bg-gray-800 rounded-2xl p-8 mb-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Current Plan</h2>
              <p className="text-3xl font-bold text-blue-400 capitalize">{tier}</p>
            </div>
            <button
              onClick={handleManageSubscription}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {subscription ? "Manage Subscription" : "Upgrade Plan"}
            </button>
          </div>

          {subscription && (
            <div className="space-y-4">
              <div className="flex justify-between py-3 border-b border-gray-700">
                <span className="text-gray-400">Status</span>
                <span className="font-semibold capitalize">{subscription.status}</span>
              </div>
              <div className="flex justify-between py-3 border-b border-gray-700">
                <span className="text-gray-400">Plan</span>
                <span className="font-semibold">{subscription.plan}</span>
              </div>
              <div className="flex justify-between py-3 border-b border-gray-700">
                <span className="text-gray-400">Renewal Date</span>
                <span className="font-semibold">
                  {new Date(subscription.current_period_end * 1000).toLocaleDateString()}
                </span>
              </div>
              {subscription.cancel_at_period_end && (
                <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4 mt-4">
                  <p className="text-yellow-400">
                    Your subscription will be cancelled at the end of the current billing period.
                  </p>
                </div>
              )}
            </div>
          )}

          {!subscription && (
            <div className="text-center py-8">
              <p className="text-gray-400 mb-4">
                You're currently on the Free plan. Upgrade to unlock premium features!
              </p>
              <button
                onClick={() => router.push("/pricing")}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg font-semibold transition-colors"
              >
                View Plans
              </button>
            </div>
          )}
        </div>

        {/* Usage Stats */}
        <div className="bg-gray-800 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-bold mb-6">Usage This Month</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-400 mb-2">--</div>
              <div className="text-gray-400">Messages</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-400 mb-2">--</div>
              <div className="text-gray-400">Credits Used</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-400 mb-2">--</div>
              <div className="text-gray-400">API Calls</div>
            </div>
          </div>
        </div>

        {/* Payment History */}
        <div className="bg-gray-800 rounded-2xl p-8">
          <h2 className="text-2xl font-bold mb-6">Payment History</h2>
          <div className="text-center py-8 text-gray-400">
            No payment history available
          </div>
        </div>
      </div>
    </div>
  );
}
