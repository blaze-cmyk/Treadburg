# 🚀 TradeBerg

**AI-Powered Trading & Financial Analysis Platform**

TradeBerg is an institutional-grade AI trading assistant that combines real-time market data, AI-powered analysis, and professional financial reporting. Built with Next.js 15 and FastAPI, it integrates multiple AI providers with live market data to provide comprehensive trading insights.

---

## ✨ Key Features

- 🤖 **AI-Powered Analysis** - Gemini 2.5 Flash + Perplexity API for market insights
- 📊 **Real-Time Market Data** - Live cryptocurrency prices via Binance API
- 📈 **Interactive Charts** - TradingView integration with technical indicators
- 💼 **SEC Filing Analysis** - Automated 10-K/10-Q analysis for fundamental research
- 💬 **Streaming Chat** - Real-time AI responses with citations
- 🖼️ **Multi-Modal Support** - Text and image analysis capabilities
- 📉 **Trading Zones** - Support/resistance detection and analysis
- 🎯 **Smart Intent Detection** - Automatic routing between chat and trading modes

---

## 🏗️ Tech Stack

### Frontend
- **Framework**: Next.js 15.5.3 with Turbopack
- **UI**: React 19, TailwindCSS 4, Framer Motion
- **Charts**: Lightweight Charts, Recharts, AG Grid
- **Auth**: NextAuth.js with JWT
- **Database**: Prisma (PostgreSQL)

### Backend
- **Framework**: FastAPI + Uvicorn
- **AI**: Gemini, Perplexity, OpenAI (optional)
- **Data**: Binance API, SEC EDGAR, CCXT
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ORM**: SQLAlchemy + Peewee

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 20.x+
- **Python** 3.11+
- **API Keys**: Gemini, Perplexity (required)

### Option 1: One-Command Startup (Windows)

```bash
cd C:\Users\hariom\Downloads\tradebergs
start-all.bat
```

Then open: **http://localhost:3000**

### Option 2: Manual Startup

#### 1. Start Backend (Terminal 1)

```bash
cd backend

# Create and activate virtual environment
python -m venv .runvenv
.runvenv\Scripts\activate  # Windows
# source .runvenv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Start server
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

**Backend will run on**: http://localhost:8080

#### 2. Start Frontend (Terminal 2)

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
# Create .env.local with:
# NEXT_PUBLIC_API_URL=http://localhost:8080/api

# Start development server
npm run dev
```

**Frontend will run on**: http://localhost:3000

---

## ⚙️ Configuration

### Backend Environment Variables

Create `backend/.env`:

```env
# AI APIs (Required)
GEMINI_API_KEY=your_gemini_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here

# AI APIs (Optional)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Market Data APIs (Optional)
NANSEN_API_KEY=your_nansen_key_here
COINALYZE_API_KEY=your_coinalyze_key_here

# Database (Production)
DATABASE_URL=postgresql://user:pass@host:5432/db

# Supabase (Optional)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# Server Configuration
HOST=0.0.0.0
PORT=8080
DEBUG=False
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend Environment Variables

Create `frontend/.env.local`:

```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8080/api

# NextAuth
NEXTAUTH_SECRET=your_secret_here
NEXTAUTH_URL=http://localhost:3000

# Database (if using Prisma)
DATABASE_URL=postgresql://user:pass@host:5432/db
```

---

## 📁 Project Structure

```
tradebergs/
├── backend/                 # FastAPI backend
│   ├── app.py              # Main application
│   ├── config.py           # Configuration
│   ├── database.py         # Database setup
│   ├── routes/             # API endpoints
│   │   ├── chat.py         # Chat API (streaming)
│   │   ├── trading.py      # Trading history/zones
│   │   ├── integrations.py # External integrations
│   │   └── sec.py          # SEC filing endpoints
│   ├── services/           # Business logic
│   │   ├── gemini_service.py
│   │   ├── perplexity_service.py
│   │   ├── chat_service.py
│   │   ├── binance_service.py
│   │   ├── market_data_service.py
│   │   └── sec_client.py
│   ├── core/               # Core functionality
│   │   ├── constants.py    # TradeBerg doctrine
│   │   ├── intent_router.py
│   │   ├── output_engine.py
│   │   └── agents/
│   └── models/             # Database models
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   │   ├── (auth)/    # Auth pages
│   │   │   ├── (main)/    # Main app
│   │   │   │   ├── c/[chatId]/  # Chat interface
│   │   │   │   ├── trade/       # Trading view
│   │   │   │   └── charts/      # Chart views
│   │   │   └── api/       # API routes (proxy)
│   │   ├── components/    # React components
│   │   │   ├── chat/      # Chat UI
│   │   │   ├── chart/     # Chart components
│   │   │   └── ui/        # Reusable UI
│   │   └── lib/           # Utilities
│   │       ├── api/       # API client
│   │       └── auth.ts    # Auth utilities
│   └── package.json
│
└── README.md              # This file
```

---

## 🎯 Usage Examples

### Chat Commands

```
"What's the price of BTC?"
→ Real-time Bitcoin price with 24h statistics

"Analyze Tesla's latest 10-K"
→ SEC filing analysis with financial metrics

"Show me @AAPL technical indicators"
→ Technical analysis with RSI, MACD, etc.

"Explain support and resistance zones"
→ Educational content about trading concepts
```

### Trading Mode

Navigate to `/trade` for the full trading interface with:
- TradingView chart integration
- AI-powered side panel
- Real-time market data
- Technical indicator analysis

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

For detailed testing instructions, see [TESTING_GUIDE.md](./TESTING_GUIDE.md)

---

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

### Key Endpoints

- `POST /api/chat/create` - Create new chat session
- `POST /api/chat/{chatId}/stream` - Stream AI responses
- `GET /api/chat/{chatId}/messages` - Get chat history
- `GET /api/integrations/binance/price/{symbol}` - Get crypto price
- `GET /api/sec/filings/{ticker}` - Get SEC filings
- `GET /api/trading/zones` - Get support/resistance zones

---

## 🛠️ Troubleshooting

### Backend Issues

**Port 8080 already in use:**
```bash
# Windows
kill-port-8080.bat

# Or manually find and kill the process
netstat -ano | findstr :8080
taskkill /PID <process_id> /F
```

**Missing dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

**Database errors:**
```bash
cd backend
python init_database.py
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Kill the process using port 3000
npx kill-port 3000
```

**Module not found errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Build errors:**
```bash
cd frontend
npm run build
```

---

## 🚢 Production Deployment

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8080
```

### Frontend

```bash
cd frontend
npm run build
npm start
```

Make sure to:
1. Set `ENVIRONMENT=production` in backend `.env`
2. Configure proper `DATABASE_URL` for PostgreSQL
3. Set secure `NEXTAUTH_SECRET`
4. Update `CORS_ORIGINS` to your production domain
5. Use environment-specific API keys

---

## 📖 Additional Documentation

- **[Backend README](./backend/README.md)** - Backend-specific documentation
- **[Frontend README](./frontend/README.md)** - Frontend-specific documentation
- **[Quick Start Guide](./QUICK_START.md)** - Simplified startup instructions
- **[Testing Guide](./TESTING_GUIDE.md)** - Comprehensive testing documentation
- **[Quick Test](./QUICK_TEST.md)** - Quick verification tests

---

## 🤝 Contributing

This is a private project. For questions or issues, contact the development team.

---

## 📄 License

Proprietary - All rights reserved

---

## 🔗 Resources

- **Next.js**: https://nextjs.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Gemini API**: https://ai.google.dev/
- **Perplexity API**: https://docs.perplexity.ai/
- **Binance API**: https://binance-docs.github.io/apidocs/

---

**Built with ❤️ for institutional-grade trading analysis**
