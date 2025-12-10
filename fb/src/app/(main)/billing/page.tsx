"use client";

import { motion } from "framer-motion";
import {
  CreditCard,
  Calendar,
  Download,
  CheckCircle2,
  XCircle,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useState } from "react";
import { useMouseWheelScroll } from "@/hooks/use-mouse-wheel-scroll";

const mockBillingHistory = [
  {
    id: "1",
    date: "2024-01-15",
    amount: "$20.00",
    plan: "Go Plan",
    status: "paid",
    invoice: "#INV-001",
  },
  {
    id: "2",
    date: "2023-12-15",
    amount: "$20.00",
    plan: "Go Plan",
    status: "paid",
    invoice: "#INV-002",
  },
  {
    id: "3",
    date: "2023-11-15",
    amount: "$20.00",
    plan: "Go Plan",
    status: "paid",
    invoice: "#INV-003",
  },
];

const mockPaymentMethods = [
  {
    id: "1",
    type: "card",
    last4: "4242",
    brand: "Visa",
    expiry: "12/25",
    isDefault: true,
  },
];

export default function BillingPage() {
  const [currentPlan] = useState({
    name: "Free",
    price: "$0",
    nextBilling: "N/A",
    status: "active",
  });

  const scrollRef = useMouseWheelScroll<HTMLDivElement>();

  return (
    <div
      ref={scrollRef}
      className="flex-1 flex flex-col h-full overflow-y-auto show-scrollbar-on-hover bg-background"
    >
      <div className="max-w-4xl mx-auto px-4 py-12 w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-2xl font-semibold text-foreground mb-2">
            Billing
          </h1>
          <p className="text-muted-foreground">
            Manage your trading platform subscription, payment methods, and
            billing history.
          </p>
        </motion.div>

        {/* Current Plan */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="rounded-2xl p-6 mb-6 bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-card-border)] shadow-[0_18px_40px_rgba(0,0,0,0.6)]"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold text-foreground">
                Current Plan
              </h2>
              <p className="text-muted-foreground mt-1">
                {currentPlan.name} Plan
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-semibold text-foreground">
                {currentPlan.price}
              </div>
              <div className="text-sm text-muted-foreground">per month</div>
            </div>
          </div>

          <div className="flex items-center gap-4 pt-4 border-t border-[var(--tradeberg-card-border)]">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-[var(--tradeberg-accent-color)]" />
              <span className="text-foreground">
                Status: {currentPlan.status}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-muted-foreground" />
              <span className="text-muted-foreground">
                Next billing: {currentPlan.nextBilling}
              </span>
            </div>
          </div>

          <div className="mt-6">
            <Button asChild className="w-full md:w-auto rounded-full bg-white text-black hover:bg-gray-200">
              <Link href="/pricing">Upgrade Plan</Link>
            </Button>
          </div>
        </motion.div>

        {/* Payment Methods */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="rounded-2xl p-6 mb-6 bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-card-border)] shadow-[0_16px_32px_rgba(0,0,0,0.55)]"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-foreground">
              Payment Methods
            </h2>
            <Button variant="outline" size="sm" className="rounded-full border-[var(--tradeberg-card-border)] text-[var(--tradeberg-text-primary)]">
              Add Payment Method
            </Button>
          </div>

          {mockPaymentMethods.length > 0 ? (
            <div className="space-y-4">
              {mockPaymentMethods.map((method) => (
                <div
                  key={method.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-[var(--tradeberg-card-border)] bg-[var(--tradeberg-bg)]"
                >
                  <div className="flex items-center gap-4">
                    <CreditCard className="w-6 h-6 text-muted-foreground" />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-foreground">
                          {method.brand} •••• {method.last4}
                        </span>
                        {method.isDefault && (
                          <span className="text-xs bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 px-2 py-1 rounded">
                            Default
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Expires {method.expiry}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="sm" className="text-[var(--tradeberg-text-secondary)] hover:bg-[var(--tradeberg-card-border)]/40">
                      Edit
                    </Button>
                    {!method.isDefault && (
                      <Button variant="ghost" size="sm" className="text-[var(--tradeberg-text-secondary)] hover:bg-[var(--tradeberg-card-border)]/40">
                        Remove
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <CreditCard className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground mb-4">
                No payment methods added yet
              </p>
              <Button variant="outline" className="rounded-full border-[var(--tradeberg-card-border)] text-[var(--tradeberg-text-primary)]">
                Add Payment Method
              </Button>
            </div>
          )}
        </motion.div>

        {/* Billing History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="rounded-2xl p-6 bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-card-border)] shadow-[0_14px_28px_rgba(0,0,0,0.5)]"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-foreground">
              Billing History
            </h2>
            <Button variant="outline" size="sm" className="rounded-full border-[var(--tradeberg-card-border)] text-[var(--tradeberg-text-primary)]">
              <Download className="w-4 h-4 mr-2" />
              Export All
            </Button>
          </div>

          {mockBillingHistory.length > 0 ? (
            <div className="space-y-4">
              {mockBillingHistory.map((invoice) => (
                <div
                  key={invoice.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-[var(--tradeberg-card-border)] bg-[var(--tradeberg-bg)]"
                >
                  <div className="flex items-center gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-foreground">
                          {invoice.invoice}
                        </span>
                        {invoice.status === "paid" ? (
                          <CheckCircle2 className="w-5 h-5 text-[var(--tradeberg-accent-color)]" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-500" />
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {invoice.plan} • {invoice.date}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="font-semibold text-foreground">
                      {invoice.amount}
                    </span>
                    <Button variant="ghost" size="sm" className="text-[var(--tradeberg-text-secondary)] hover:bg-[var(--tradeberg-card-border)]/40">
                      <Download className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No billing history found</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
