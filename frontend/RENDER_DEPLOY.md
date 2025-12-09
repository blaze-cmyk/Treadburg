# 🚀 TradeBerg Frontend - Render Deployment Guide

## Quick Start

### Render Web Service Configuration

| Setting | Value |
|---------|-------|
| **Name** | `tradeberg-frontend` (or your preferred name) |
| **Region** | Choose closest to your users |
| **Branch** | `main` |
| **Root Directory** | `frontend` |
| **Runtime** | Node |
| **Build Command** | `npm install && npm run build` |
| **Start Command** | `npm run start` |
| **Instance Type** | Starter (or higher for production) |

---

## Environment Variables

Set these in **Render Dashboard → Your Service → Environment**:

### Required Variables

```
NODE_VERSION=20
NEXT_PUBLIC_API_URL=https://treadburg.onrender.com/api
NEXT_PUBLIC_SUPABASE_URL=https://pcxscejarxztezfeucgs.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-supabase-anon-key>
NEXTAUTH_SECRET=<generate-a-secure-secret>
NEXTAUTH_URL=https://your-frontend-name.onrender.com
DATABASE_URL=<your-supabase-connection-string>
```

### Optional Variables

```
NEXT_PUBLIC_APP_URL=https://your-frontend-name.onrender.com
```

---

## Step-by-Step Deployment

### 1. Push Code to GitHub
Ensure your latest changes are pushed to your GitHub repository.

### 2. Create New Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Select the repository containing TradeBerg

### 3. Configure Service Settings
- Set **Root Directory** to `frontend`
- Set **Build Command** to `npm install && npm run build`
- Set **Start Command** to `npm run start`

### 4. Add Environment Variables
Copy all required environment variables from the list above.

> ⚠️ **Important:** Replace placeholder values with your actual credentials

### 5. Deploy
Click **Create Web Service** and wait for the build to complete.

---

## Troubleshooting

### Build Fails
- Ensure `NODE_VERSION=20` is set
- Check that all required environment variables are set
- Review build logs for specific errors

### 502 Bad Gateway
- Wait 2-3 minutes for the service to start
- Check the Logs tab in Render dashboard
- Verify `npm run start` is the start command

### API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` points to your backend
- Check if backend service is running
- Ensure CORS is configured on backend

### Authentication Not Working
- Verify `NEXTAUTH_URL` matches your Render URL exactly
- Check Supabase redirect URLs in Supabase dashboard
- Ensure `NEXTAUTH_SECRET` is set

---

## Post-Deployment Checklist

- [ ] Verify the site loads correctly
- [ ] Test login/signup flow
- [ ] Verify chat functionality works
- [ ] Check billing pages load
- [ ] Test on mobile devices

---

## Architecture

```
[Browser] → [Render: tradeberg-frontend] → [Render: treadburg (backend)]
                     ↓
              [Supabase Auth & DB]
```

The frontend proxies API calls through Next.js API routes to your backend, avoiding CORS issues.
