# 🚀 TradeBerg - Deploy to Vercel

## Quick Deploy

### 1. Frontend (Vercel)
```bash
# Push to GitHub
git init
git add .
git commit -m "Production ready"
git push origin main

# Deploy on Vercel
1. Go to vercel.com
2. Import GitHub repo
3. Root directory: frontend
4. Add environment variables (see below)
5. Deploy!
```

### 2. Backend (Railway)
```bash
# Deploy on Railway
1. Go to railway.app
2. New Project → GitHub repo
3. Root directory: backend
4. Add environment variables
5. Deploy!
```

---

## Environment Variables

### Vercel (Frontend)
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api
NEXT_PUBLIC_SUPABASE_URL=https://pcxscejarxztezfeucgs.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<from Supabase>
NEXTAUTH_URL=https://your-app.vercel.app
NEXTAUTH_SECRET=<openssl rand -base64 32>
```

### Railway (Backend)
```
CORS_ORIGINS=https://your-app.vercel.app
GEMINI_API_KEY=<your key>
SUPABASE_URL=https://pcxscejarxztezfeucgs.supabase.co
SUPABASE_KEY=<service role key>
```

---

## What's Included

✅ **Security**: Rate limiting, XSS protection, CSRF tokens  
✅ **Auth**: Email/password + Google OAuth via Supabase  
✅ **AI Chat**: Gemini-powered financial analysis  
✅ **Charts**: Professional data visualization  
✅ **Deployment Ready**: Vercel + Railway configs included

---

## Files Auto-Excluded

The following are automatically excluded from deployment:
- `backend/` (deployed separately to Railway)
- `*.bat` files (Windows scripts)
- `test_*.py` files
- `.env` files
- `logs/` directory

---

## Post-Deployment

1. Test at your Vercel URL
2. Configure custom domain (optional)
3. Set up monitoring
4. Check security headers at securityheaders.com

---

## Support

- **Deployment Guide**: See `VERCEL_DEPLOYMENT.md`
- **Checklist**: See `DEPLOYMENT_CHECKLIST.md`
- **Environment Template**: See `ENV_TEMPLATE.md`

**Total deployment time: ~40 minutes** ⏱️
