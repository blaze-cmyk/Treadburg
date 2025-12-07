# 🚀 TradeBerg Quick Start Guide

## Start in 3 Simple Steps

### Step 1: Open Terminal
Navigate to the TradeBerg folder:
```bash
cd C:\Users\hariom\Downloads\tradebergs
```

### Step 2: Run the Startup Script
```bash
start-all.bat
```

### Step 3: Open Your Browser
Go to: **http://localhost:3000**

---

## ✅ That's It!

Your TradeBerg application is now running with:
- ✅ Backend API on port 8080
- ✅ Frontend on port 3000
- ✅ AI-powered chat with Perplexity
- ✅ Real-time streaming responses
- ✅ Trading history and zone analysis

---

## 🎯 What You Can Do Now

### Try These Commands in the Chat:
1. **"What's the price of @AAPL?"** - Get stock prices
2. **"Analyze @BTC technical indicators"** - Technical analysis
3. **"Show me trading history"** - View your trades
4. **"Explain RSI indicator"** - Learn trading concepts

---

## 🛠️ If Something Goes Wrong

### Backend Issues
```bash
cd backend
venv\Scripts\activate.bat
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8080
```

### Frontend Issues
```bash
cd frontend
npm install
npm run dev
```

---

## 📚 Full Documentation
See `INTEGRATION_COMPLETE.md` for detailed information.

**Happy Trading! 📈**
