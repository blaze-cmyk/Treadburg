// Using `require` for Stripe as this is a Node.js serverless function environment
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

/**
 * Serverless function to create a Stripe subscription.
 * Endpoint: /api/create-subscription (or similar, based on hosting)
 * Method: POST
 * Body: { plan: 'pro' | 'max', billingCycle: 'monthly' | 'yearly' }
 */
export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).send('Method Not Allowed');
  }

  // Check for Stripe secret key
  if (!process.env.STRIPE_SECRET_KEY) {
    console.error("Stripe secret key is not set in environment variables.");
    return res.status(500).json({ error: 'Server configuration error. Please contact support.' });
  }

  try {
    const { plan, billingCycle } = req.body;

    // Validate request body
    if (!plan || !billingCycle) {
      return res.status(400).json({ error: 'Missing required parameters: plan and billingCycle.' });
    }

    // --- IMPORTANT ---
    // Replace these placeholder IDs with your actual Stripe Price IDs from your Stripe Dashboard.
    const priceIds = {
      pro: {
        monthly: 'price_PRO_MONTHLY_PLACEHOLDER',
        // yearly: 'price_PRO_YEARLY_PLACEHOLDER',
      },
      max: {
        monthly: 'price_MAX_MONTHLY_PLACEHOLDER',
        // yearly: 'price_MAX_YEARLY_PLACEHOLDER',
      },
    };

    const priceId = priceIds[plan]?.[billingCycle];
    
    if (!priceId || priceId.includes('PLACEHOLDER')) {
        console.error(`Price ID for plan '${plan}' (${billingCycle}) is not configured or is a placeholder.`);
        return res.status(400).json({ error: 'The selected plan is currently unavailable. Please try again later.' });
    }

    // 1. Create a new Customer in Stripe
    const customer = await stripe.customers.create({
      description: `New customer for TradeBerg ${plan} (${billingCycle})`,
    });

    // 2. Create the Subscription.
    // The `payment_behavior: 'default_incomplete'` creates the subscription with a 'requires_payment_method' status.
    // The client-side Payment Element will handle the payment confirmation.
    const subscription = await stripe.subscriptions.create({
      customer: customer.id,
      items: [{ price: priceId }],
      payment_behavior: 'default_incomplete',
      payment_settings: { save_default_payment_method: 'on_subscription' },
      expand: ['latest_invoice.payment_intent'],
    });

    const latestInvoice = subscription.latest_invoice;
    const paymentIntent = latestInvoice.payment_intent;

    if (!paymentIntent || !paymentIntent.client_secret) {
        throw new Error("Failed to create a payment intent for the subscription.");
    }
    
    // 3. Send the `client_secret` from the Payment Intent to the frontend.
    // The frontend uses this to securely complete the payment with the Payment Element.
    res.status(200).json({
      clientSecret: paymentIntent.client_secret,
    });

  } catch (error) {
    console.error('Stripe API Error:', error.message);
    // Send a generic error message to the client for security
    res.status(500).json({ error: 'An internal server error occurred. Please try again.' });
  }
}
