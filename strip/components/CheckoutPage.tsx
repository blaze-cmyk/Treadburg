import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Check, Lock, Loader2, AlertTriangle, PartyPopper } from 'lucide-react';
import { Plan } from '../types';
import { useStripe, useElements, PaymentElement, Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';

// Load Stripe with your publishable key outside of the component render tree
const stripePromise = loadStripe('pk_live_51PHqTQKGS1cHUXXStuI96OXZz47zXQzFOoo1KqjixV7fc2Pz3HuJVwTarOGe6DWuThprbgPHGcWYrtd8BplEyaro00JyOe8IWi');

interface CheckoutPageProps {
  plan: Plan;
  onBack: () => void;
  onClose: () => void;
}

// This function now securely calls the backend to create a subscription.
// The Stripe secret key is never exposed to the client.
const createSubscription = async (plan: Plan, billingCycle: 'monthly' | 'yearly'): Promise<{ clientSecret: string | null; error?: string }> => {
  try {
    const response = await fetch('/api/create-subscription', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ plan, billingCycle }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to initialize payment.');
    }

    return { clientSecret: data.clientSecret };
  } catch (error: any) {
    console.error("API Error:", error);
    return { clientSecret: null, error: error.message };
  }
};


interface CheckoutFormProps {
  plan: Plan;
  billingCycle: 'monthly' | 'yearly';
  onClose: () => void;
}

const CheckoutForm = ({ plan, billingCycle, onClose }: CheckoutFormProps) => {
    const stripe = useStripe();
    const elements = useElements();
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<string | null>(null);
    const [subscriptionComplete, setSubscriptionComplete] = useState(false);

    const isPro = plan === 'pro';
    const monthlyPrice = isPro ? 20 : 200;
    const yearlyPrice = isPro ? 200 : 2000;
    const planPrice = billingCycle === 'monthly' ? monthlyPrice : yearlyPrice;
    const planName = isPro ? 'Pro' : 'Max';

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!stripe || !elements) return;

        setIsLoading(true);
        setMessage(null);

        const { error } = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: window.location.href.split('?')[0], // Use base URL
            },
        });

        if (error) {
           if (error.type === "card_error" || error.type === "validation_error") {
               setMessage(error.message || "An unexpected error occurred.");
           } else {
               setMessage("An unexpected error occurred.");
           }
        }
        
        setIsLoading(false);
    };
    
    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('payment_intent') && urlParams.get('redirect_status') === 'succeeded') {
            setSubscriptionComplete(true);
        }
    }, []);

    if (subscriptionComplete) {
      return (
        <div className="text-center">
            <PartyPopper size={48} className="mx-auto text-teal-500 mb-4" />
            <h2 className="text-2xl font-bold">Payment Successful!</h2>
            <p className="text-gray-600 mt-2">Welcome to TradeBerg {planName}. Your subscription is now active.</p>
            <button onClick={onClose} className="mt-8 bg-accent text-white font-semibold py-3 px-6 rounded-lg hover:bg-accent/90 transition-colors">
              Start Analyzing
            </button>
        </div>
      )
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <PaymentElement />
            {message && <div className="p-3 bg-red-100 border border-red-300 text-red-800 rounded-md text-sm flex items-center gap-2"><AlertTriangle size={16} />{message}</div>}
            <button
                disabled={isLoading || !stripe || !elements}
                className="w-full mt-4 bg-accent text-white font-semibold py-3 rounded-lg hover:bg-accent/90 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
            >
                {isLoading ? <Loader2 className="animate-spin" /> : `Subscribe for $${planPrice.toFixed(2)}`}
            </button>
        </form>
    );
};

export const CheckoutPage: React.FC<CheckoutPageProps> = ({ plan, onBack, onClose }) => {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingSecret, setIsLoadingSecret] = useState(true);
  
  const isPro = plan === 'pro';
  const monthlyPrice = isPro ? 20 : 200;
  const yearlyPrice = isPro ? 200 : 2000;
  const yearlySavings = (monthlyPrice * 12) - yearlyPrice;
  const hasYearlyOption = false; // Set to true once you have yearly price IDs

  useEffect(() => {
      setIsLoadingSecret(true);
      setError(null);
      setClientSecret(null);
      createSubscription(plan, billingCycle).then(result => {
          if (result.clientSecret) {
              setClientSecret(result.clientSecret);
          } else {
              setError(result.error || "Failed to initialize payment.");
          }
          setIsLoadingSecret(false);
      });
  }, [plan, billingCycle]);

  const planPrice = billingCycle === 'monthly' ? monthlyPrice : yearlyPrice;
  const planName = isPro ? 'Pro' : 'Max';

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-white text-gray-800 z-50 overflow-y-auto"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button onClick={onBack} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 mb-8">
          <ArrowLeft size={16} />
          Back
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Left Side: Payment Form */}
          <div>
            <h2 className="text-lg font-semibold mb-4">1. Choose billing cycle</h2>
            <div className="grid grid-cols-2 gap-3 mb-8">
              <BillingCycleButton
                label="Pay monthly"
                price={`$${monthlyPrice.toFixed(2)} per month`}
                isActive={billingCycle === 'monthly'}
                onClick={() => setBillingCycle('monthly')}
              />
              <div className="relative group">
                <BillingCycleButton
                  label="Pay yearly"
                  price={`$${yearlyPrice.toFixed(2)} per year`}
                  isActive={billingCycle === 'yearly'}
                  onClick={() => hasYearlyOption && setBillingCycle('yearly')}
                  disabled={!hasYearlyOption}
                />
                {!hasYearlyOption && <div className="absolute inset-0 flex items-center justify-center text-xs font-semibold text-gray-500 bg-gray-50/80 rounded-lg cursor-not-allowed">Coming Soon</div>}
              </div>
            </div>

            <h2 className="text-lg font-semibold mb-4">2. Select your payment method</h2>
            {isLoadingSecret ? (
              <div className="p-4 border rounded-lg bg-gray-50 flex items-center justify-center h-40">
                <Loader2 className="animate-spin text-gray-400" />
              </div>
            ) : clientSecret ? (
              <Elements stripe={stripePromise} options={{ clientSecret }}>
                <CheckoutForm plan={plan} billingCycle={billingCycle} onClose={onClose} />
              </Elements>
            ) : (
                <div className="p-4 border rounded-lg bg-red-50 text-red-700">
                    <p className="font-semibold">Could not load payment form</p>
                    <p className="text-sm">{error}</p>
                </div>
            )}
            
          </div>

          {/* Right Side: Order Summary */}
          <div className="bg-gray-50 rounded-lg p-8 h-fit">
            <h3 className="text-xl font-bold mb-6">TradeBerg {planName}</h3>
             <ul className="space-y-3 text-sm text-gray-600 mb-8">
              {isPro ? (
                <>
                  <FeatureItem text="10x as many citations in answers" />
                  <FeatureItem text="Unlimited file and photo uploads" />
                  <FeatureItem text="Extended access to image generation" />
                  <FeatureItem text="One subscription to the latest AI models" />
                </>
              ) : (
                <>
                  <FeatureItem text="Everything in Pro" />
                  <FeatureItem text="Early access to our newest products" />
                  <FeatureItem text="Unlimited access to advanced AI models" />
                  <FeatureItem text="Enhanced access to video generation" />
                  <FeatureItem text="Priority support" />
                </>
              )}
            </ul>

            <div className="space-y-2 py-4 border-y">
               <div className="flex justify-between items-center text-sm">
                 <span className="text-gray-600">Billing cycle</span>
                 <span className="font-medium">{billingCycle === 'monthly' ? 'Monthly' : 'Annually'}</span>
               </div>
               {billingCycle === 'monthly' && hasYearlyOption && (
                  <button onClick={() => setBillingCycle('yearly')} className="text-accent text-sm font-semibold hover:underline">
                    Switch to annual and save ${yearlySavings.toFixed(2)} per year
                  </button>
               )}
            </div>
            
            <div className="space-y-2 py-4 border-b">
              <div className="flex justify-between items-center text-sm">
                 <span className="text-gray-600">Subtotal</span>
                 <span className="font-medium">${planPrice.toFixed(2)}</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-gray-600">Tax</span>
                 <span className="font-medium">—</span>
               </div>
            </div>

            <div className="flex justify-between items-center font-bold text-lg pt-4">
              <span>Total due today</span>
              <span>${planPrice.toFixed(2)}</span>
            </div>
            
            <p className="text-xs text-gray-500 mt-8 text-center">
              By confirming your subscription, you allow TradeBerg to charge you for future payments in accordance with their terms. You can always cancel your subscription.
            </p>
            
            <div className="flex items-center justify-center gap-2 mt-6 text-xs text-gray-400">
               <Lock size={12} />
               <span>Powered by <span className="font-semibold text-gray-600">Stripe</span></span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

const BillingCycleButton = ({ label, price, isActive, onClick, disabled = false }: { label: string, price: string, isActive: boolean, onClick: () => void, disabled?: boolean }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={`p-4 border rounded-lg text-left transition-colors relative ${isActive ? 'bg-teal-50 border-accent ring-2 ring-accent' : 'bg-gray-50 hover:border-gray-400'} ${disabled ? 'cursor-not-allowed opacity-60' : ''}`}
  >
    <span className="font-semibold block">{label}</span>
    <span className="text-sm text-gray-500">{price}</span>
  </button>
);

const FeatureItem = ({ text }: { text: string }) => (
  <li className="flex items-center gap-3">
    <Check size={16} className="text-accent flex-shrink-0" />
    <span>{text}</span>
  </li>
);
