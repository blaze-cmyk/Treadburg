# Backend Deployment Instructions

This guide will help you deploy the TradeBerg backend successfully.

## Fixed Issues

1. **Database Initialization Error**: Updated `init_db()` function to properly handle Supabase REST API mode, avoiding the `NoneType` error.
2. **CORS Configuration**: Added production URLs to CORS settings to allow requests from the deployed frontend.
3. **Security Headers**: Updated CSP and TrustedHosts to work with production domains.

## Deployment Steps

### 1. Push Changes to GitHub

```bash
git add .
git commit -m "Fix backend database initialization and CORS settings"
git push
```

### 2. Set Environment Variables on Render

Ensure these environment variables are set in your Render deployment:

```
USE_SUPABASE_REST=true
DATABASE_URL=<your-supabase-connection-string>
ENVIRONMENT=production
CORS_ORIGINS=https://tradeberg-frontend.onrender.com,https://supa.vercel.app
```

### 3. Deploy the Backend

In the Render dashboard:
1. Select your backend service
2. Click "Manual Deploy" > "Deploy latest commit"
3. Wait for the deployment to complete

## Checking Deployment Success

Once deployed, verify the following in the Render logs:

1. You should see: "🔌 Using Supabase REST API (direct PostgreSQL connection disabled)"
2. You should see: "⚠️ Database initialization skipped - will connect on first API call"
3. You should NOT see any "NoneType has no attribute..." errors

## Testing the API

Make a request to the base URL to verify the API is running:
```
https://treadburg.onrender.com/
```

## Troubleshooting

If you still encounter issues:

1. **Check Logs**: Look at the Render deployment logs for any errors.
2. **Verify Environment Variables**: Ensure all environment variables are correctly set.
3. **Test Endpoints**: Use a tool like Postman to test basic API endpoints.

## Need More Help?

If you continue to experience issues, please provide:
1. The specific error messages from the Render logs
2. Any environment variable changes you made
3. Any modifications to the deployment process
