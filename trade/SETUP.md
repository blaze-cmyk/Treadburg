# 🚀 TradeBerg Setup Guide

Complete setup instructions for the TradeBerg unified monorepo.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Node.js 18+** and **npm 9+** - [Download](https://nodejs.org/)
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/)

## 🎯 Quick Setup (Recommended)

### Step 1: Install All Dependencies

Run the installation script:

```bash
install-all.bat
```

This will:
- Install root npm dependencies
- Install client (frontend) dependencies
- Create Python virtual environment
- Install server (backend) dependencies

### Step 2: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   - Supabase URL and keys
   - Stripe keys
   - Google OAuth credentials
   - AI API keys (Gemini, OpenAI, etc.)

### Step 3: Start Development Servers

Run both frontend and backend:

```bash
start-dev.bat
```

Or start them separately:

```bash
start-client.bat    # Frontend only (port 3000)
start-server.bat    # Backend only (port 8080)
```

## 🔧 Manual Setup

If you prefer to set up manually:

### 1. Install Root Dependencies
```bash
npm install
```

### 2. Install Client Dependencies
```bash
cd client
npm install
cd ..
```

### 3. Setup Python Environment
```bash
cd server
python -m venv .runvenv
.runvenv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 4. Configure Environment
```bash
copy .env.example .env
# Edit .env with your credentials
```

### 5. Start Development
```bash
# Terminal 1 - Frontend
cd client
npm run dev

# Terminal 2 - Backend
cd server
.runvenv\Scripts\activate
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8080
```

## 🗄️ Database Setup

### Supabase Setup (Recommended)

1. Create a project at [supabase.com](https://supabase.com)
2. Get your project URL and keys
3. Update `.env` with Supabase credentials
4. Run migrations:
   ```bash
   cd server/supabase/migrations
   # Apply migrations through Supabase dashboard or CLI
   ```

### Local Database (Optional)

```bash
cd server
.runvenv\Scripts\activate
python init_database.py
```

## 🔐 Required API Keys

### Essential (Required for core functionality)

1. **Supabase**
   - Sign up at [supabase.com](https://supabase.com)
   - Create a new project
   - Get: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`

2. **NextAuth Secret**
   - Generate: `openssl rand -base64 32`
   - Set as: `NEXTAUTH_SECRET`

3. **Stripe** (for payments)
   - Sign up at [stripe.com](https://stripe.com)
   - Get: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`

### Optional (For enhanced features)

4. **Google OAuth** (for Google login)
   - Create project at [console.cloud.google.com](https://console.cloud.google.com)
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Get: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`

5. **AI APIs** (for chat features)
   - **Gemini**: [ai.google.dev](https://ai.google.dev)
   - **OpenAI**: [platform.openai.com](https://platform.openai.com)
   - **Perplexity**: [perplexity.ai](https://www.perplexity.ai)

## 🧪 Testing

### Run All Tests
```bash
npm test
```

### Client Tests Only
```bash
cd client
npm test
```

### Server Tests Only
```bash
cd server
.runvenv\Scripts\activate
pytest
```

## 📱 Access Your Application

After starting the servers:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs

## 🐛 Troubleshooting

### Port Already in Use

**Frontend (3000)**:
```bash
# Find and kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Backend (8080)**:
```bash
# Find and kill process on port 8080
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### Python Dependencies Issues

```bash
cd server
.runvenv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Node Modules Issues

```bash
cd client
rmdir /s /q node_modules
del package-lock.json
npm install
```

### Database Connection Issues

1. Check Supabase credentials in `.env`
2. Verify Supabase project is active
3. Check network connectivity
4. Review server logs for specific errors

## 📚 Next Steps

1. **Configure OAuth**: Set up Google OAuth for authentication
2. **Setup Stripe**: Configure payment processing
3. **Add AI Keys**: Enable AI chat features
4. **Customize**: Modify branding and features as needed

## 🆘 Getting Help

- Check `README.md` for general information
- Review `client/README.md` for frontend details
- Review `server/README.md` for backend details
- Check API docs at http://localhost:8080/docs

---

**Ready to trade! 🚀**
