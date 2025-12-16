# 🚨 URGENT FIX - Render Root Directory Configuration

## The Problem
Render can't find the `client` folder because the **Root Directory** is incorrectly configured.

Error: `ENOENT: no such file or directory, open '/opt/render/project/src/trade/client/package.json'`

## The Solution

### Update Your Render Service Settings

**Go to your Render dashboard → Frontend Service → Settings**

Change the **Root Directory** setting:

**Current (WRONG):**
```
Root Directory: (empty) or client
```

**Correct (RIGHT):**
```
Root Directory: trade
```

### Complete Configuration

**Frontend Service:**
```
Name: tradeberg-frontend
Region: Oregon (US West)
Branch: main
Root Directory: trade          ← CRITICAL: Must be "trade"
Runtime: Node
Build Command: npm install; npm run build
Start Command: cd client && npm start
```

**Backend Service:**
```
Name: tradeberg-backend
Region: Oregon (US West)
Branch: main
Root Directory: trade/server   ← CRITICAL: Must be "trade/server"
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
```

## Step-by-Step Fix

1. **Go to Render Dashboard**
   - Navigate to https://dashboard.render.com

2. **Select Your Frontend Service**
   - Click on "tradeberg-frontend" (or whatever you named it)

3. **Go to Settings**
   - Click "Settings" in the left sidebar

4. **Update Root Directory**
   - Find "Root Directory" field
   - Change it to: `trade`
   - Click "Save Changes"

5. **Trigger Manual Deploy**
   - Go to "Manual Deploy" tab
   - Click "Clear build cache & deploy"

6. **Monitor Build Logs**
   - Watch the logs - should now find client folder
   - Build should complete in 2-5 minutes

## Why This Works

Your GitHub repository structure is:
```
repository-root/
  └── trade/
      ├── client/
      │   └── package.json
      ├── server/
      └── package.json
```

When you set `Root Directory: trade`, Render starts from the `trade` folder, so:
- `npm run build` executes from `/trade/`
- Which runs `npm install --prefix client` (finds `/trade/client/`)
- Then runs `npm run --prefix client build` (builds from `/trade/client/`)

## Verification

After the fix, your build logs should show:
```
==> Running build command 'npm install; npm run build'...
up to date, audited 30 packages in 553ms
> tradeberg-monorepo@1.0.0 build
> npm install --prefix client && npm run --prefix client build

added 500 packages in 45s  ← Should see client packages installing
> chatgpt-clone@0.1.0 build
> next build                ← Should see Next.js building

✓ Compiled successfully    ← Success!
```

## If It Still Fails

Check these:
1. **Verify your GitHub repo has the `trade` folder at the root**
2. **Ensure `trade/client/package.json` exists**
3. **Check that you pushed the latest changes to GitHub**
4. **Try "Clear build cache & deploy" again**

---

**This should fix your deployment immediately!** 🚀
