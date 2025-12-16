# 🚀 TradeBerg Trading Platform

A unified full-stack trading platform with AI-powered chat, real-time market data, and comprehensive trading tools.

## 📁 Project Structure

```
trade/
├── client/          # Next.js frontend application
├── server/          # FastAPI backend application
├── package.json     # Root package.json with unified scripts
├── .env.example     # Environment variables template
└── README.md        # This file
```

## 🛠️ Tech Stack

### Frontend (Client)
- **Framework**: Next.js 15 with React 19
- **Styling**: TailwindCSS 4
- **UI Components**: Radix UI, shadcn/ui
- **Authentication**: NextAuth.js with Supabase
- **State Management**: React Context + SWR
- **Charts**: Lightweight Charts, Recharts
- **Animations**: Framer Motion, GSAP

### Backend (Server)
- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT with Supabase Auth
- **Payment**: Stripe
- **AI/ML**: Google Gemini, OpenAI, Anthropic
- **Market Data**: Binance, Alpaca
- **Vector DB**: ChromaDB
- **Rate Limiting**: SlowAPI

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm 9+
- Python 3.11+
- Git

### 1. Clone and Navigate
```bash
cd trade
```

### 2. Install Dependencies
```bash
# Install root dependencies (concurrently for running both servers)
npm install

# Install client dependencies
npm run install:client

# Install server dependencies
npm run install:server
```

### 3. Environment Setup
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and fill in your API keys and configuration
```

### 4. Run Development Servers
```bash
# Run both client and server simultaneously
npm run dev

# Or run them separately:
npm run dev:client    # Frontend on http://localhost:3000
npm run dev:server    # Backend on http://localhost:8080
```

## 📝 Available Scripts

### Development
- `npm run dev` - Run both client and server in development mode
- `npm run dev:client` - Run only the frontend
- `npm run dev:server` - Run only the backend

### Production
- `npm run build` - Build the client for production
- `npm start` - Start both client and server in production mode
- `npm run start:client` - Start only the frontend
- `npm run start:server` - Start only the backend

### Installation
- `npm run install:all` - Install all dependencies
- `npm run install:client` - Install client dependencies
- `npm run install:server` - Install server dependencies

### Testing & Linting
- `npm run lint` - Run ESLint on the client
- `npm run test` - Run all tests
- `npm run test:client` - Run client tests
- `npm run test:server` - Run server tests (pytest)

## 🔧 Configuration

### Client Configuration
The client configuration is in `client/next.config.js`. Key settings:
- CORS and security headers
- API URL configuration
- Image optimization
- Environment variables

### Server Configuration
The server configuration is in `server/config.py`. Key settings:
- CORS origins
- Database connections
- API keys
- Rate limiting

## 🔐 Environment Variables

See `.env.example` for all required environment variables. Key variables:

**Application URLs**
- `NEXT_PUBLIC_APP_URL` - Frontend URL
- `NEXT_PUBLIC_API_URL` - Backend API URL

**Supabase**
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

**Authentication**
- `NEXTAUTH_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

**Stripe**
- `STRIPE_SECRET_KEY`
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`

**AI APIs**
- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `PERPLEXITY_API_KEY`

## 📦 Database Setup

### Supabase Setup
1. Create a Supabase project at https://supabase.com
2. Run migrations from `server/supabase/migrations/`
3. Update `.env` with your Supabase credentials

### Local Database (Optional)
```bash
cd server
python init_database.py
```

## 🎨 Features

- **AI-Powered Chat**: Intelligent trading assistant with context-aware responses
- **Real-Time Charts**: Interactive TradingView-style charts
- **Market Data**: Live crypto and stock market data
- **User Authentication**: Secure OAuth with Google and email/password
- **Subscription Management**: Stripe-powered billing and subscriptions
- **Document Ingestion**: AI-powered document analysis and chat
- **Trading Integration**: Connect with Alpaca and other brokers
- **Dark/Light Mode**: Beautiful theme switching with animations

## 🧪 Testing

### Client Tests
```bash
cd client
npm test
```

### Server Tests
```bash
cd server
pytest
```

## 📚 Documentation

- **Client**: See `client/README.md`
- **Server**: See `server/README.md`
- **API Docs**: Visit http://localhost:8080/docs when server is running

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

Proprietary - All rights reserved

## 🆘 Support

For issues and questions, please check:
- Client documentation in `client/`
- Server documentation in `server/`
- Environment setup in `.env.example`

---

**Built with ❤️ by the TradeBerg Team**
