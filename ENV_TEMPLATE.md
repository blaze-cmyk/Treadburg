# Environment Variables Template for Production

# ==============================================
# FRONTEND ENVIRONMENT VARIABLES (Vercel)
# ==============================================

# API Configuration
NEXT_PUBLIC_API_URL=https://your-backend-api.railway.app/api

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://pcxscejarxztezfeucgs.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# NextAuth Configuration
NEXTAUTH_URL=https://your-app.vercel.app
NEXTAUTH_SECRET=generate_with_openssl_rand_base64_32

# ==============================================
# BACKEND ENVIRONMENT VARIABLES (Railway/Render)
# ==============================================

# Server Configuration
HOST=0.0.0.0
PORT=8080
ENVIRONMENT=production

# CORS Origins (update with your Vercel URL)
CORS_ORIGINS=https://your-app.vercel.app

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Stripe (optional)
STRIPE_SECRET_KEY=your_stripe_secret_key_here
