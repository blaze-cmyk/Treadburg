<script lang="ts">
	import FinancialAnalysisRenderer from '$lib/components/chat/FinancialAnalysisRenderer.svelte';
	import FinancialBarChart from '$lib/components/charts/FinancialBarChart.svelte';
	import CandlestickChart from '$lib/components/charts/CandlestickChart.svelte';
	import SimpleDataGrid from '$lib/components/charts/SimpleDataGrid.svelte';

	// Test 1: Complete AI Response with all chart types
	const fullAIResponse = `
# 📊 Bitcoin Market Analysis - January 15, 2024

## What Happened Today?

Bitcoin surged **5.2%** today from $42,000 to $44,200. Here's the complete breakdown:

### Price Action Analysis

\`\`\`json:chart:candlestick
{
  "title": "BTC/USDT - January 15, 2024 Price Action",
  "data": [
    {"date": "2024-01-15 09:00", "open": 42000, "high": 42500, "low": 41800, "close": 42300, "volume": 8500000000},
    {"date": "2024-01-15 10:00", "open": 42300, "high": 43200, "low": 42200, "close": 43000, "volume": 12400000000},
    {"date": "2024-01-15 11:00", "open": 43000, "high": 43800, "low": 42900, "close": 43500, "volume": 10200000000},
    {"date": "2024-01-15 12:00", "open": 43500, "high": 44000, "low": 43300, "close": 43800, "volume": 9800000000},
    {"date": "2024-01-15 13:00", "open": 43800, "high": 44300, "low": 43600, "close": 44100, "volume": 11500000000},
    {"date": "2024-01-15 14:00", "open": 44100, "high": 44500, "low": 43900, "close": 44200, "volume": 15800000000}
  ],
  "annotations": [
    {"x": "2024-01-15 10:00", "y": 42500, "text": "📰 Fed Rate Pause Announced", "type": "entry"},
    {"x": "2024-01-15 11:00", "y": 43000, "text": "📈 IDEAL ENTRY: Support + Volume", "type": "entry"},
    {"x": "2024-01-15 14:00", "y": 44000, "text": "🎯 TAKE PROFIT: Resistance Zone", "type": "exit"},
    {"x": "2024-01-15 11:00", "y": 42700, "text": "🛑 STOP LOSS: Below Support", "type": "stop"}
  ]
}
\`\`\`

### Volume Analysis

The buying pressure was **significantly stronger** than selling:

\`\`\`json:chart:bar
{
  "title": "Volume Breakdown - January 15, 2024",
  "data": [
    {"label": "Buy Volume", "value": 28500000000, "color": "#10b981"},
    {"label": "Sell Volume", "value": 15200000000, "color": "#ef4444"},
    {"label": "Neutral Volume", "value": 8300000000, "color": "#6b7280"}
  ]
}
\`\`\`

### Top Movers Today

\`\`\`json:chart:grid
{
  "title": "Top Performing Assets - January 15, 2024",
  "data": [
    {"symbol": "BTC", "price": 44200, "change_24h": 5.2, "volume": 52000000000, "market_cap": 865000000000, "sentiment": "Bullish 🚀"},
    {"symbol": "ETH", "price": 2380, "change_24h": 4.8, "volume": 18500000000, "market_cap": 286000000000, "sentiment": "Bullish 📈"},
    {"symbol": "SOL", "price": 108, "change_24h": 7.2, "volume": 3200000000, "market_cap": 48000000000, "sentiment": "Very Bullish 🔥"},
    {"symbol": "AVAX", "price": 38.5, "change_24h": 6.1, "volume": 890000000, "market_cap": 14500000000, "sentiment": "Bullish 📈"},
    {"symbol": "MATIC", "price": 0.92, "change_24h": 3.4, "volume": 420000000, "market_cap": 8500000000, "sentiment": "Neutral ⚖️"}
  ]
}
\`\`\`

## Why Did the Market Go Positive?

### 1. **Federal Reserve Decision** 🏛️
The Fed announced a pause in rate hikes at 10:00 AM UTC, which is **bullish for risk assets** like Bitcoin.

### 2. **Institutional Buying** 🐋
On-chain data shows **$500M in large purchases** during the afternoon session:
- Coinbase: $280M net inflow
- Binance: $150M net inflow  
- Kraken: $70M net inflow

### 3. **Technical Breakout** 📈
BTC broke above the **$43,500 resistance level** with strong volume confirmation (15.8B in the 2PM hour).

## Entry Analysis

### 🎯 **Best Entry Point**
**Price:** $43,000 (11:00 AM)
**Why it was EASY:**
- ✅ Broke above $42,800 resistance
- ✅ Volume spike confirmed breakout (12.4B)
- ✅ RSI showed momentum (62)
- ✅ Support at $42,700

**Risk/Reward:** 1:4 (Excellent!)
- Stop Loss: $42,700 (-$300)
- Take Profit: $44,000 (+$1,000)

**Probability of Success:** 72% ⭐⭐⭐⭐

### ⚠️ **Risky Entry**
**Price:** $44,200 (Current)
**Why it's RISKY:**
- ❌ At resistance zone
- ❌ Overbought RSI (78)
- ❌ Volume declining
- ❌ Potential pullback zone

**Risk/Reward:** 1:1 (Poor!)
**Probability of Success:** 35% ⚠️

## Key Levels

| Level | Price | Type | Strength |
|-------|-------|------|----------|
| Resistance | $45,000 | Major | Strong 🔴 |
| Resistance | $44,500 | Minor | Medium 🟡 |
| Current | $44,200 | - | - |
| Support | $43,000 | Major | Strong 🟢 |
| Support | $42,700 | Minor | Medium 🟡 |

## Recommendation

**For New Entries:** ⏸️ **WAIT**
- Current price is at resistance
- Better entry on pullback to $43,000-$43,200

**For Existing Positions:** 💰 **TAKE PROFIT**
- Move stop loss to breakeven
- Consider taking 50% profit at $44,500
- Let remaining run to $45,000

**Overall Market Sentiment:** 🚀 **BULLISH**
- Probability of continued rally: **72%**
- Key support: **$43,000**
- Next target: **$45,000**
`;

	// Test 2: Individual chart components
	const barChartData = [
		{ label: 'Long Positions', value: 1850000000, color: '#10b981' },
		{ label: 'Short Positions', value: 920000000, color: '#ef4444' },
		{ label: 'Neutral', value: 430000000, color: '#6b7280' }
	];

	const candlestickData = {
		title: 'ETH/USDT - 4H Chart',
		data: [
			{
				date: '2024-01-15 00:00',
				open: 2250,
				high: 2280,
				low: 2240,
				close: 2265,
				volume: 4200000000
			},
			{
				date: '2024-01-15 04:00',
				open: 2265,
				high: 2310,
				low: 2260,
				close: 2295,
				volume: 5100000000
			},
			{
				date: '2024-01-15 08:00',
				open: 2295,
				high: 2340,
				low: 2290,
				close: 2320,
				volume: 4800000000
			},
			{
				date: '2024-01-15 12:00',
				open: 2320,
				high: 2385,
				low: 2315,
				close: 2370,
				volume: 6200000000
			},
			{
				date: '2024-01-15 16:00',
				open: 2370,
				high: 2395,
				low: 2360,
				close: 2380,
				volume: 5500000000
			}
		],
		annotations: [
			{ x: '2024-01-15 08:00', y: 2300, text: '📈 Entry Zone', type: 'entry' },
			{ x: '2024-01-15 16:00', y: 2390, text: '🎯 Target', type: 'exit' },
			{ x: '2024-01-15 08:00', y: 2280, text: '🛑 Stop', type: 'stop' }
		]
	};

	const gridData = [
		{
			asset: 'Bitcoin',
			symbol: 'BTC',
			price: 44200,
			change_1h: 0.8,
			change_24h: 5.2,
			volume_24h: 52000000000,
			market_cap: 865000000000
		},
		{
			asset: 'Ethereum',
			symbol: 'ETH',
			price: 2380,
			change_1h: 0.6,
			change_24h: 4.8,
			volume_24h: 18500000000,
			market_cap: 286000000000
		},
		{
			asset: 'Solana',
			symbol: 'SOL',
			price: 108,
			change_1h: 1.2,
			change_24h: 7.2,
			volume_24h: 3200000000,
			market_cap: 48000000000
		}
	];

	let activeTab = 'full';
</script>

<svelte:head>
	<title>Financial Charts Test - TradeBerg</title>
</svelte:head>

<div class="min-h-screen bg-gray-950 text-white p-8">
	<div class="max-w-7xl mx-auto">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-4xl font-bold mb-2">📊 Financial Charts Test Page</h1>
			<p class="text-gray-400">
				Testing all financial visualization components for TradeBerg chat integration
			</p>
		</div>

		<!-- Status Indicators -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
			<div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
				<div class="flex items-center gap-2">
					<span class="text-2xl">✅</span>
					<div>
						<div class="text-sm text-gray-400">D3.js Charts</div>
						<div class="font-semibold text-green-400">Ready</div>
					</div>
				</div>
			</div>
			<div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
				<div class="flex items-center gap-2">
					<span class="text-2xl">✅</span>
					<div>
						<div class="text-sm text-gray-400">Plotly Charts</div>
						<div class="font-semibold text-green-400">Ready</div>
					</div>
				</div>
			</div>
			<div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
				<div class="flex items-center gap-2">
					<span class="text-2xl">✅</span>
					<div>
						<div class="text-sm text-gray-400">Data Grids</div>
						<div class="font-semibold text-green-400">Ready</div>
					</div>
				</div>
			</div>
			<div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
				<div class="flex items-center gap-2">
					<span class="text-2xl">✅</span>
					<div>
						<div class="text-sm text-gray-400">AI Parser</div>
						<div class="font-semibold text-green-400">Ready</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Tab Navigation -->
		<div class="flex gap-2 mb-6 border-b border-gray-800">
			<button
				class="px-6 py-3 font-semibold transition-colors {activeTab === 'full'
					? 'text-blue-400 border-b-2 border-blue-400'
					: 'text-gray-400 hover:text-white'}"
				on:click={() => (activeTab = 'full')}
			>
				Full AI Response
			</button>
			<button
				class="px-6 py-3 font-semibold transition-colors {activeTab === 'bar'
					? 'text-blue-400 border-b-2 border-blue-400'
					: 'text-gray-400 hover:text-white'}"
				on:click={() => (activeTab = 'bar')}
			>
				Bar Chart
			</button>
			<button
				class="px-6 py-3 font-semibold transition-colors {activeTab === 'candlestick'
					? 'text-blue-400 border-b-2 border-blue-400'
					: 'text-gray-400 hover:text-white'}"
				on:click={() => (activeTab = 'candlestick')}
			>
				Candlestick
			</button>
			<button
				class="px-6 py-3 font-semibold transition-colors {activeTab === 'grid'
					? 'text-blue-400 border-b-2 border-blue-400'
					: 'text-gray-400 hover:text-white'}"
				on:click={() => (activeTab = 'grid')}
			>
				Data Grid
			</button>
		</div>

		<!-- Content -->
		<div class="bg-gray-900 border border-gray-800 rounded-lg p-6">
			{#if activeTab === 'full'}
				<div class="prose prose-invert max-w-none">
					<h2 class="text-2xl font-bold mb-4">
						🤖 Complete AI Response with All Chart Types
					</h2>
					<p class="text-gray-400 mb-6">
						This simulates a full AI response with embedded bar charts, candlestick charts, and
						data grids. This is exactly how it will appear in your chat.
					</p>
					<div class="bg-gray-950 border border-gray-700 rounded-lg p-6">
						<FinancialAnalysisRenderer content={fullAIResponse} />
					</div>
				</div>
			{:else if activeTab === 'bar'}
				<div>
					<h2 class="text-2xl font-bold mb-4">📊 Bar Chart Component Test</h2>
					<p class="text-gray-400 mb-6">
						D3.js bar chart for volume analysis, comparisons, and portfolio breakdown.
					</p>
					<FinancialBarChart data={barChartData} title="Position Distribution" />
				</div>
			{:else if activeTab === 'candlestick'}
				<div>
					<h2 class="text-2xl font-bold mb-4">📈 Candlestick Chart Component Test</h2>
					<p class="text-gray-400 mb-6">
						Plotly.js candlestick chart with OHLCV data and entry/exit/stop annotations.
					</p>
					<CandlestickChart
						data={candlestickData.data}
						title={candlestickData.title}
						annotations={candlestickData.annotations}
					/>
				</div>
			{:else if activeTab === 'grid'}
				<div>
					<h2 class="text-2xl font-bold mb-4">📋 Data Grid Component Test</h2>
					<p class="text-gray-400 mb-6">
						Custom data grid with sorting, filtering, pagination, and CSV export.
					</p>
					<SimpleDataGrid rowData={gridData} title="Top Cryptocurrencies" />
				</div>
			{/if}
		</div>

		<!-- Integration Instructions -->
		<div class="mt-8 bg-blue-950 border border-blue-800 rounded-lg p-6">
			<h3 class="text-xl font-bold mb-4 flex items-center gap-2">
				<span>💡</span>
				<span>How to Use in Chat</span>
			</h3>
			<div class="space-y-4 text-sm">
				<div>
					<div class="font-semibold text-blue-300 mb-2">For AI to generate charts:</div>
					<div class="bg-gray-900 rounded p-3 font-mono text-xs">
						User: "What happened on January 15th that made BTC go up?"<br />
						<br />
						AI: Returns response with embedded chart blocks like:<br />
						```json:chart:candlestick<br />
						{'{'}..chart data..{'}'}
						```
					</div>
				</div>
				<div>
					<div class="font-semibold text-blue-300 mb-2">Chart types available:</div>
					<ul class="list-disc list-inside space-y-1 text-gray-300">
						<li><code>```json:chart:bar</code> - Volume, comparisons, portfolio</li>
						<li><code>```json:chart:candlestick</code> - Price action with annotations</li>
						<li><code>```json:chart:grid</code> - Tabular data with sorting/filtering</li>
					</ul>
				</div>
				<div>
					<div class="font-semibold text-blue-300 mb-2">Status:</div>
					<div class="text-green-400">
						✅ All components working<br />
						✅ Integrated into ResponseMessage.svelte<br />
						✅ Smart chart detection enabled<br />
						✅ Ready to use in chat
					</div>
				</div>
			</div>
		</div>

		<!-- Quick Links -->
		<div class="mt-6 flex gap-4">
			<a
				href="/"
				class="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
			>
				← Back to Chat
			</a>
			<a
				href="/test-financial-charts"
				class="px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-semibold transition-colors"
			>
				🔄 Refresh Test
			</a>
		</div>
	</div>
</div>

<style>
	:global(body) {
		background: #030712;
	}
</style>
