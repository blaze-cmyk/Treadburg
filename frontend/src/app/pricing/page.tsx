"use client";

import React, { useState, useEffect } from "react";
import { useUser } from "@/contexts/UserContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Check, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api-client";

interface SubscriptionTier {
  id: string;
  name: string;
  price_monthly: number;
  price_yearly?: number;
  features: string[];
  stripe_price_id_monthly?: string;
  stripe_price_id_yearly?: string;
  popular?: boolean;
}

export default function PricingPage() {
  const { user, profile } = useUser();
  const [tiers, setTiers] = useState<SubscriptionTier[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingTier, setProcessingTier] = useState<string | null>(null);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');

  useEffect(() => {
    loadTiers();
  }, []);

  const loadTiers = async () => {
    try {
      const data = await apiClient.getSubscriptionTiers();
      setTiers(data);
    } catch (error) {
      console.error('Error loading tiers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (tier: SubscriptionTier) => {
    if (!user) {
      window.location.href = '/login';
      return;
    }

    if (tier.id === 'free') {
      return; // Already on free tier
    }

    setProcessingTier(tier.id);

    try {
      const priceId = billingPeriod === 'monthly' 
        ? tier.stripe_price_id_monthly 
        : tier.stripe_price_id_yearly;

      if (!priceId) {
        alert('Price ID not configured');
        return;
      }

      // Create checkout session through backend
      const response = await apiClient.createCheckoutSession(
        priceId,
        user.email || undefined
      );

      if (response.url) {
        // Redirect to Stripe checkout
        window.location.href = response.url;
      }
    } catch (error) {
      console.error('Error creating checkout:', error);
      alert('Failed to start checkout process');
    } finally {
      setProcessingTier(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container max-w-7xl mx-auto px-4 py-16">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
        <p className="text-xl text-muted-foreground mb-8">
          Unlock the full power of TradeBerg AI
        </p>

        {/* Billing Period Toggle */}
        <div className="inline-flex items-center gap-2 p-1 bg-muted rounded-lg">
          <button
            onClick={() => setBillingPeriod('monthly')}
            className={`px-4 py-2 rounded-md transition-colors ${
              billingPeriod === 'monthly'
                ? 'bg-background shadow-sm'
                : 'hover:bg-background/50'
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingPeriod('yearly')}
            className={`px-4 py-2 rounded-md transition-colors ${
              billingPeriod === 'yearly'
                ? 'bg-background shadow-sm'
                : 'hover:bg-background/50'
            }`}
          >
            Yearly
            <span className="ml-2 text-xs text-green-600 font-semibold">Save 17%</span>
          </button>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        {tiers.map((tier) => {
          const price = billingPeriod === 'monthly' 
            ? tier.price_monthly 
            : (tier.price_yearly || tier.price_monthly * 10);
          
          const isProcessing = processingTier === tier.id;

          return (
            <Card
              key={tier.id}
              className={`relative ${
                tier.popular ? 'border-primary shadow-lg scale-105' : ''
              }`}
            >
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground px-4 py-1 rounded-full text-sm font-semibold">
                  Most Popular
                </div>
              )}

              <CardHeader>
                <CardTitle className="text-2xl">{tier.name}</CardTitle>
                <CardDescription>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-foreground">
                      ${price}
                    </span>
                    <span className="text-muted-foreground">
                      /{billingPeriod === 'monthly' ? 'month' : 'year'}
                    </span>
                  </div>
                </CardDescription>
              </CardHeader>

              <CardContent>
                <Button
                  onClick={() => handleSubscribe(tier)}
                  disabled={isProcessing || tier.id === 'free'}
                  className="w-full mb-6"
                  variant={tier.popular ? 'default' : 'outline'}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : tier.id === 'free' ? (
                    'Current Plan'
                  ) : (
                    'Subscribe'
                  )}
                </Button>

                <ul className="space-y-3">
                  {tier.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Credits Info */}
      {user && profile && (
        <div className="mt-12 text-center">
          <Card className="max-w-md mx-auto">
            <CardHeader>
              <CardTitle>Your Credits</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary mb-2">
                {profile.credits_balance || 0}
              </div>
              <p className="text-sm text-muted-foreground">
                Credits are used for AI chat messages and analysis
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
