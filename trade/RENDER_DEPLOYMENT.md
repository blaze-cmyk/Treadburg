# 🚀 Deploy TradeBerg on Render.com (Single Platform)

Deploy your entire `trade` folder on Render.com - both frontend and backend on the same platform with easy communication.

## ✅ Why Render.com?

- **Free Tier Available**: Start with free tier for both services
- **Easy Setup**: Connect your GitHub repo and deploy
- **Automatic HTTPS**: Free SSL certificates
- **Auto-Deploy**: Automatic deployments on git push
- **Environment Variables**: Easy management through dashboard
- **Single Platform**: Both services on one platform, easy communication
- **PostgreSQL Support**: Free PostgreSQL database if needed

## 📋 Prerequisites

1. **GitHub Account**: Your code needs to be on GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Environment Variables**: Have all your API keys ready

## 🎯 Step-by-Step Deployment

### Step 1: Push Code to GitHub

```bash
cd trade
git init
git add .
git commit -m "Initial commit - TradeBerg unified app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tradeberg.git
git push -u origin main
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Deploy Backend (Server)

1. **Click "New +" → "Web Service"**

2. **Connect Repository**
   - Select your `tradeberg` repository
   - Click "Connect"

3. **Configure Service**
   ```
   Name: tradeberg-backend
   Region: Oregon (US West) or closest to you
   Branch: main
   Root Directory: server
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

4. **Select Plan**
   - Free tier (for testing)
   - Or Starter ($7/month for production)

5. **Add Environment Variables**
   Click "Advanced" → "Add Environment Variable"
   
   Add these variables:
   ```
   PYTHON_VERSION=3.11.0
   ENVIRONMENT=production
   PORT=8080
   
   # Supabase
   SUPABASE_URL=https://pcxscejarxztezfeucgs.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   
   # Stripe
   STRIPE_SECRET_KEY=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
   
   # AI APIs
   GEMINI_API_KEY=your_gemini_key
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   PERPLEXITY_API_KEY=your_perplexity_key
   
   # Security
   SECRET_KEY=your_random_secret_key_here
   ALLOWED_ORIGINS=https://tradeberg-frontend.onrender.com
   ```

6. **Click "Create Web Service"**
   - Wait 5-10 minutes for deployment
   - Note your backend URL: `https://tradeberg-backend.onrender.com`

### Step 4: Deploy Frontend (Client)

1. **Click "New +" → "Web Service"**

2. **Connect Same Repository**
   - Select your `tradeberg` repository

3. **Configure Service**
   ```
   Name: tradeberg-frontend
   Region: Oregon (US West) - same as backend
   Branch: main
   Root Directory: client
   Runtime: Node
   Build Command: npm install && npm run build
   Start Command: npm start
   ```

4. **Select Plan**
   - Free tier (for testing)
   - Or Starter ($7/month for production)

5. **Add Environment Variables**
   ```
   NODE_VERSION=18.17.0
   NODE_ENV=production
   
   # Backend URL (use your actual backend URL from Step 3)
   NEXT_PUBLIC_API_URL=https://tradeberg-backend.onrender.com
   NEXT_PUBLIC_APP_URL=https://tradeberg-frontend.onrender.com
   
   # Supabase
   NEXT_PUBLIC_SUPABASE_URL=https://pcxscejarxztezfeucgs.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   
   # Stripe
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
   
   # NextAuth
   NEXTAUTH_SECRET=generate_random_secret_here
   NEXTAUTH_URL=https://tradeberg-frontend.onrender.com
   
   # Google OAuth
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   ```

6. **Click "Create Web Service"**
   - Wait 5-10 minutes for deployment
   - Your app will be live at: `https://tradeberg-frontend.onrender.com`

### Step 5: Update CORS Settings

After both services are deployed, update the backend's CORS settings:

1. Go to backend service settings
2. Update `ALLOWED_ORIGINS` environment variable:
   ```
   ALLOWED_ORIGINS=https://tradeberg-frontend.onrender.com
   ```
3. Click "Save Changes" (this will redeploy)

### Step 6: Update OAuth Redirect URLs

Update your OAuth providers with the new URLs:

**Google OAuth Console**:
- Authorized JavaScript origins: `https://tradeberg-frontend.onrender.com`
- Authorized redirect URIs: `https://tradeberg-frontend.onrender.com/api/auth/callback/google`

**Supabase Dashboard**:
- Site URL: `https://tradeberg-frontend.onrender.com`
- Redirect URLs: `https://tradeberg-frontend.onrender.com/auth/callback`

## 🔧 Configuration Files Needed

### Update `client/next.config.js`

Make sure the API URL is configurable:

```javascript
env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
    // ... other env vars
}
```

### Update `server/config.py`

Ensure CORS origins are read from environment:

```python
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
```

## 💰 Pricing

### Free Tier
- **Backend**: 750 hours/month (sleeps after 15 min inactivity)
- **Frontend**: 750 hours/month (sleeps after 15 min inactivity)
- **Total**: $0/month (with limitations)

### Starter Plan (Recommended for Production)
- **Backend**: $7/month (always on, 512MB RAM)
- **Frontend**: $7/month (always on, 512MB RAM)
- **Total**: $14/month

### Pro Plan
- **Each Service**: $25/month (2GB RAM, better performance)
- **Total**: $50/month for both

## 🎨 Custom Domain (Optional)

1. Go to service settings
2. Click "Custom Domain"
3. Add your domain (e.g., `app.tradeberg.com`)
4. Update DNS records as instructed
5. Render provides free SSL automatically

## 🔄 Auto-Deploy Setup

Render automatically deploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push

# Render automatically detects and deploys!
```

## 📊 Monitoring

**View Logs**:
1. Go to your service dashboard
2. Click "Logs" tab
3. See real-time logs

**Metrics**:
- CPU usage
- Memory usage
- Request count
- Response times

## 🐛 Troubleshooting

### Build Fails

**Check build logs**:
- Look for missing dependencies
- Verify Python/Node versions
- Check environment variables

### Service Sleeps (Free Tier)

**Solutions**:
1. Upgrade to Starter plan ($7/month)
2. Use a cron job to ping every 10 minutes
3. Accept 30-second cold start delay

### CORS Errors

**Fix**:
1. Verify `ALLOWED_ORIGINS` includes frontend URL
2. Check both services are deployed
3. Ensure URLs match exactly (https, no trailing slash)

### Database Connection Issues

**Check**:
1. Supabase credentials are correct
2. Supabase project is active
3. Network connectivity from Render to Supabase

## ✅ Post-Deployment Checklist

- [ ] Both services deployed successfully
- [ ] Frontend can reach backend API
- [ ] Database connections working
- [ ] Authentication (Google OAuth) working
- [ ] Stripe payments configured
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificates active
- [ ] Monitoring and alerts set up

## 🚀 You're Live!

Your TradeBerg app is now deployed on Render.com!

- **Frontend**: https://tradeberg-frontend.onrender.com
- **Backend**: https://tradeberg-backend.onrender.com
- **API Docs**: https://tradeberg-backend.onrender.com/docs

## 📝 Next Steps

1. Test all features thoroughly
2. Set up monitoring and alerts
3. Configure backups
4. Add custom domain
5. Optimize performance
6. Set up CI/CD pipeline

---

**Need Help?** Check [Render Documentation](https://render.com/docs) or contact support.
