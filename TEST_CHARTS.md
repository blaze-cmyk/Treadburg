# 🧪 Quick Test Guide - Financial Charts

## 🎯 3-Minute Test

### **Step 1: Start Server** (30 seconds)

```bash
cd c:\Users\hariom\Downloads\tradebergs
npm run dev
```

Wait for: `Local: http://localhost:5173/`

---

### **Step 2: Test Charts Page** (1 minute)

1. Open browser: **http://localhost:5173/test-financial-charts**

2. You should see:
   - ✅ 4 green status indicators (D3.js, Plotly, Data Grids, AI Parser)
   - ✅ Tab navigation (Full AI Response, Bar Chart, Candlestick, Data Grid)
   - ✅ Charts rendering without errors

3. Click through tabs:
   - **Full AI Response** → See complete analysis with all chart types
   - **Bar Chart** → See volume bar chart
   - **Candlestick** → See price chart with annotations
   - **Data Grid** → See sortable table

**Expected:** All charts render beautifully ✅

---

### **Step 3: Test Terminal** (1 minute)

1. Go to main chat: **http://localhost:5173**

2. Look for **💻 button** in bottom-right corner

3. Click it → Terminal slides up from bottom

4. Try commands:
   ```bash
   help          # See all commands
   price BTC     # Get Bitcoin price
   analyze ETH   # Analyze Ethereum
   status        # System status
   ```

5. Press **ESC** to close

**Expected:** Terminal works smoothly ✅

---

### **Step 4: Test Chart Rendering in Chat** (30 seconds)

1. In main chat, paste this message:

```
Testing charts:

```json:chart:bar
{
  "title": "Test Volume",
  "data": [
    {"label": "Buy", "value": 1500000, "color": "#10b981"},
    {"label": "Sell", "value": 1200000, "color": "#ef4444"}
  ]
}
```
```

2. Send the message

**Expected:** You see a green/red bar chart ✅

---

## ✅ Success Criteria

If you see:
- ✅ Test page loads with charts
- ✅ Terminal opens/closes smoothly
- ✅ Bar chart renders from JSON

**Then everything is working!** 🎉

---

## ❌ If Something Doesn't Work

### **Charts not rendering?**

Run:
```bash
npm install d3 plotly.js-dist-min chart.js --legacy-peer-deps
npm run dev
```

### **Terminal button not showing?**

1. Check browser console for errors
2. Hard refresh: `Ctrl + Shift + R`
3. Clear cache and reload

### **Still issues?**

Check `COMPLETE_INTEGRATION_GUIDE.md` for detailed troubleshooting.

---

## 🎨 What to Test Next

### **Test Smart Detection:**

1. Ask: "What is BTC price?"
   - Should show TradingView widget ✅

2. Ask: "Analyze Bitcoin and tell me if it's risky"
   - Should NOT show TradingView (waits for AI charts) ✅

3. Ask: "Tell me about Bitcoin history"
   - Should NOT show any chart ✅

### **Test Different Chart Types:**

Paste these in chat:

**Candlestick Chart:**
```
```json:chart:candlestick
{
  "title": "BTC Test",
  "data": [
    {"date": "2024-01-15", "open": 42000, "high": 43000, "low": 41500, "close": 42800, "volume": 28000000000}
  ],
  "annotations": [
    {"x": "2024-01-15", "y": 42000, "text": "📈 Entry", "type": "entry"}
  ]
}
```
```

**Data Grid:**
```
```json:chart:grid
{
  "title": "Top Coins",
  "data": [
    {"symbol": "BTC", "price": 43200, "change": 2.5}
  ]
}
```
```

---

## 🚀 You're All Set!

Everything is integrated and working. Now you can:

1. ✅ Use charts in chat responses
2. ✅ Use terminal for quick commands
3. ✅ Test on the test page
4. ✅ Customize as needed

**Next:** Add `FINANCIAL_SYSTEM_PROMPT` to your AI to auto-generate charts!

See `COMPLETE_INTEGRATION_GUIDE.md` for full details.
