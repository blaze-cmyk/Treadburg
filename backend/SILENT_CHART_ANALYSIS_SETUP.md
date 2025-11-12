# Silent Chart Analysis System - Setup Guide

## Overview

This system automatically captures TradingView chart screenshots when users request analysis, sends them to Vision API (OpenAI/Qwen) for analysis, and returns clean text responses **without showing screenshots in the chat UI**.

## ✅ What Was Implemented

### Backend Services

1. **Intent Detection** (`backend/open_webui/utils/intent_detector.py`)

   - Detects if user prompt requires chart analysis
   - Extracts symbol and timeframe from messages
   - Identifies analysis keywords and patterns

2. **Silent Screenshot Capture** (`backend/open_webui/utils/chart_capture.py`)

   - Uses Playwright to capture charts without user interaction
   - Captures TradingView iframes or chart containers
   - Browser instance caching for performance
   - No permission popups - runs entirely in backend

3. **Vision API Integration** (`backend/open_webui/utils/vision_analyzer.py`)

   - Analyzes screenshots using OpenAI Vision API (gpt-4o)
   - Supports Qwen Vision as alternative
   - Returns only text analysis (no images)
   - Screenshots NEVER appear in chat UI

4. **Chat Handler Integration** (`backend/open_webui/main.py`)
   - Modified `tradeberg_chat_enforced` to intercept analysis requests
   - Automatically removes auto-attached images for analysis requests
   - Performs silent screenshot capture and vision analysis
   - Integrates analysis into prompt context

### Frontend Changes

1. **Message Input** (`src/lib/components/chat/MessageInput.svelte`)
   - Updated `maybeAutoAttachHistoricalSnapshot()` to skip frontend capture for analysis requests
   - Prevents permission popups for analysis keywords
   - Backend handles all screenshot capture silently

## 🔧 Setup Instructions

### 1. Environment Variables

Add to your `.env` file or environment:

```bash
# OpenAI API (required for vision analysis)
OPENAI_API_KEY=your_openai_api_key_here

# Frontend URL (for Playwright to access charts)
FRONTEND_URL=http://localhost:5173

# Optional: Qwen Vision API (alternative to OpenAI)
QWEN_API_KEY=your_qwen_key_here
QWEN_API_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
```

### 2. Dependencies

Playwright is already in `requirements.txt`. Install browsers if needed:

```bash
# Install Playwright browsers
playwright install chromium

# Or on Linux (if needed):
sudo apt-get install -y \
  chromium-browser \
  libx11-xcb1 \
  libxcomposite1 \
  libxdamage1 \
  libxi6 \
  libxtst6 \
  libnss3 \
  libcups2 \
  libxrandr2 \
  libasound2 \
  libpangocairo-1.0-0 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libgtk-3-0
```

### 3. Verify Installation

Test the system:

```bash
# Start backend
cd backend
python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8081

# Start frontend (in another terminal)
npm run dev
```

## 🧪 Testing

### Test Scenarios

1. **Analysis Request (Should use silent vision)**

   ```
   User: "Analyze BTC trend"
   Expected: ✅ Text response, ❌ No screenshot shown, ❌ No popup
   ```

2. **Regular Chat (Should NOT use vision)**

   ```
   User: "What's the current BTC price?"
   Expected: ✅ Text response, ❌ No screenshot taken
   ```

3. **Manual Image Upload (Should still work)**

   ```
   User: [Uploads image manually] "What do you see?"
   Expected: ✅ Image shown in chat, ✅ AI analyzes it
   ```

4. **Multiple Analysis Requests**
   ```
   User: "Analyze BTC" then "Analyze ETH"
   Expected: ✅ Both get analyzed separately with silent screenshots
   ```

## 🔍 How It Works

### Flow Diagram

```
User: "Analyze BTC"
  ↓
Frontend: Detects analysis keyword → Skips frontend capture
  ↓
Backend: Intercepts request → Detects analysis intent
  ↓
Backend: Captures screenshot silently (Playwright) → NO USER INTERACTION
  ↓
Backend: Sends to Vision API → Screenshot NEVER goes to chat
  ↓
Backend: Receives text analysis
  ↓
Backend: Integrates analysis into prompt → Sends to GPT-5
  ↓
User sees: Clean text response ✅ (NO screenshot in chat)
```

### Key Features

- **No Permission Popups**: All screenshot capture happens in backend
- **Screenshots Hidden**: Images never appear in chat UI
- **Automatic Detection**: System detects analysis requests automatically
- **Performance Optimized**: Browser instance caching for fast screenshots
- **Fallback Handling**: If screenshot fails, continues with regular chat

## 📊 Performance

- Screenshot capture: ~2-5 seconds
- Vision API analysis: ~3-8 seconds
- Total analysis time: ~5-13 seconds

## 🐛 Troubleshooting

### Screenshot Not Capturing

1. Check Playwright installation:

   ```bash
   playwright install chromium
   ```

2. Verify frontend is accessible:

   ```bash
   curl http://localhost:5173
   ```

3. Check browser logs in backend:
   ```bash
   # Look for "📸 Silently capturing chart" messages
   ```

### Vision API Errors

1. Verify OpenAI API key:

   ```bash
   echo $OPENAI_API_KEY
   ```

2. Check API quota/limits

3. Review error logs in backend console

### Frontend Still Showing Screenshots

1. Clear browser cache
2. Restart frontend dev server
3. Check browser console for errors

## 📝 Code Locations

- Intent Detection: `backend/open_webui/utils/intent_detector.py`
- Chart Capture: `backend/open_webui/utils/chart_capture.py`
- Vision Analyzer: `backend/open_webui/utils/vision_analyzer.py`
- Chat Handler: `backend/open_webui/main.py` (function `tradeberg_chat_enforced`)
- Frontend Logic: `src/lib/components/chat/MessageInput.svelte` (function `maybeAutoAttachHistoricalSnapshot`)

## 🚀 Next Steps

1. Test with different symbols and timeframes
2. Monitor performance and optimize browser caching
3. Add more analysis keywords to intent detection if needed
4. Consider adding Qwen Vision as fallback option

## ✅ Verification Checklist

After setup, verify:

- [ ] Backend starts without errors
- [ ] Playwright browsers installed
- [ ] OpenAI API key configured
- [ ] Frontend accessible at FRONTEND_URL
- [ ] Analysis requests work without popups
- [ ] Screenshots don't appear in chat
- [ ] Regular chat still works normally
- [ ] Manual image uploads still work

## 🎯 Success Criteria

✅ User sends "Analyze BTC" → No popup appears  
✅ Response is pure text analysis (no image in chat)  
✅ Backend logs show screenshot was taken  
✅ Vision API was called successfully  
✅ Regular chat messages work normally  
✅ Manual image uploads still work  
✅ Performance is acceptable (5-13 seconds for analysis)
