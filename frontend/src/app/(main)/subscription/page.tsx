"use client";

import { motion } from "framer-motion";
import {
  CheckCircle2,
  XCircle,
  Calendar,
  CreditCard,
  Zap,
  Crown,
  Sparkle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useMouseWheelScroll } from "@/hooks/use-mouse-wheel-scroll";

const currentSubscription = {
  plan: "Free",
  price: "$0",
  status: "active",
  nextBilling: "N/A",
  features: [
    "Basic stock and crypto prices",
    "Limited trading conversations",
    "Standard market data",
    "Community support",
  ],
  icon: Sparkle,
};

const availablePlans = [
  {
    name: "Go",
    price: "₹399",
    period: "per month",
    description: "For active traders",
    features: [
      "Real-time stock and crypto prices",
      "Advanced technical analysis",
      "Portfolio tracking",
      "Trading strategy suggestions",
      "Market alerts and notifications",
      "Priority support",
    ],
    icon: Zap,
    popular: true,
  },
  {
    name: "Pro",
    price: "₹19,900",
    period: "per month",
    description: "For professional traders and institutions",
    features: [
      "Unlimited market data access",
      "Institutional-grade analysis",
      "AI trading assistant",
      "Advanced charting tools",
      "API access for algorithmic trading",
      "Dedicated support",
      "Custom trading strategies",
    ],
    icon: Crown,
    popular: false,
  },
];

export default function SubscriptionPage() {
  const PlanIcon = currentSubscription.icon;
  const scrollRef = useMouseWheelScroll<HTMLDivElement>();

  return (
    <div
      ref={scrollRef}
      className="flex-1 flex flex-col h-full overflow-y-auto show-scrollbar-on-hover bg-background"
    >
      <div className="max-w-6xl mx-auto px-4 py-12 w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-2xl font-semibold text-foreground mb-2">
            Subscription
          </h1>
          <p className="text-muted-foreground">
            Manage your trading platform subscription and access levels.
          </p>
        </motion.div>

        {/* Current Subscription */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="glass-strong rounded-2xl p-8 mb-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="p-4 rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
                <PlanIcon className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-1">
                  {currentSubscription.plan} Plan
                </h2>
                <div className="flex items-center gap-2">
                  {currentSubscription.status === "active" ? (
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500" />
                  )}
                  <span className="text-muted-foreground capitalize">
                    {currentSubscription.status}
                  </span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-semibold text-foreground mb-1">
                {currentSubscription.price}
              </div>
              <div className="text-sm text-muted-foreground">per month</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="flex items-center gap-3 p-4 rounded-lg border border-border glass-light">
              <Calendar className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Next Billing</p>
                <p className="font-medium text-foreground">
                  {currentSubscription.nextBilling}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 rounded-lg border border-border glass-light">
              <CreditCard className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Payment Method</p>
                <p className="font-medium text-foreground">Not configured</p>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-foreground mb-3">
              Current Plan Features
            </h3>
            <ul className="space-y-2">
              {currentSubscription.features.map((feature, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                  <span className="text-foreground">{feature}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="flex gap-3">
            <Button asChild>
              <Link href="/pricing">Upgrade Plan</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/billing">Manage Billing</Link>
            </Button>
          </div>
        </motion.div>

        {/* Available Plans */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-6"
        >
          <h2 className="text-xl font-semibold text-foreground mb-4">
            Available Plans
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {availablePlans.map((plan, index) => {
              const PlanIcon = plan.icon;
              return (
                <motion.div
                  key={plan.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                  className={`glass-strong rounded-2xl p-6 ${
                    plan.popular
                      ? "ring-2 ring-indigo-500 dark:ring-indigo-400"
                      : ""
                  }`}
                >
                  {plan.popular && (
                    <div className="mb-4">
                      <span className="bg-indigo-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                        Most Popular
                      </span>
                    </div>
                  )}
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-3 rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
                      <PlanIcon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-foreground">
                        {plan.name}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {plan.description}
                      </p>
                    </div>
                  </div>
                  <div className="mb-4">
                    <div className="flex items-baseline gap-2">
                      <span className="text-xl font-semibold text-foreground">
                        {plan.price}
                      </span>
                      {plan.price !== "Custom" && (
                        <span className="text-muted-foreground">
                          /{plan.period}
                        </span>
                      )}
                    </div>
                  </div>
                  <ul className="space-y-2 mb-6">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                        <span className="text-sm text-foreground">
                          {feature}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <Button
                    variant={plan.popular ? "default" : "outline"}
                    className="w-full"
                    asChild
                  >
                    <Link href="/pricing">
                      {plan.price === "Custom" ? "Contact Sales" : "Upgrade"}
                    </Link>
                  </Button>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
