<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { getOpenInterest, getFundingRates, type OpenInterestData, type FundingRateData } from '$lib/apis/coinalyze';
	import { toast } from 'svelte-sonner';

	// State
	let selectedSymbol = 'BTCUSDC';
	let marketData: any = {};
	let openInterestData: OpenInterestData[] = [];
	let fundingRateData: FundingRateData[] = [];
	let isLoading = false;
	let refreshInterval: any;
	let orderSize = '';
	let orderPrice = '';
	let orderSide: 'buy' | 'sell' = 'buy';

	// Popular trading pairs
	const popularPairs = [
		'BTCUSDC', 'ETHUSDC', 'SOLUSDC', 'ADAUSDC', 'DOTUSDC',
		'LINKUSDC', 'AVAXUSDC', 'MATICUSDC', 'ATOMUSDC', 'NEARUSDC'
	];

	// Mock price data (in real app, this would come from WebSocket)
	let mockPrices: Record<string, any> = {
		BTCUSDC: { price: 103421, change: -0.32, volume: 6953950244.61 },
		ETHUSDC: { price: 3245.67, change: 2.15, volume: 2847392847.23 },
		SOLUSDC: { price: 234.89, change: -1.45, volume: 1293847562.45 }
	};

	// Format numbers
	function formatPrice(price: number): string {
		if (price >= 1000) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
		if (price >= 1) return price.toFixed(4);
		return price.toFixed(6);
	}

	function formatVolume(volume: number): string {
		if (volume >= 1e9) return `$${(volume / 1e9).toFixed(2)}B`;
		if (volume >= 1e6) return `$${(volume / 1e6).toFixed(2)}M`;
		if (volume >= 1e3) return `$${(volume / 1e3).toFixed(2)}K`;
		return `$${volume.toFixed(2)}`;
	}

	function formatPercent(percent: number): string {
		const sign = percent >= 0 ? '+' : '';
		return `${sign}${percent.toFixed(2)}%`;
	}

	function formatFundingRate(rate: number): string {
		return `${(rate * 100).toFixed(4)}%`;
	}

	// Load market data
	async function loadMarketData() {
		if (isLoading) return;
		
		isLoading = true;
		try {
			const symbols = [selectedSymbol];
			
			// Try to get real data, fall back to mock data
			const [openInterest, fundingRates] = await Promise.all([
				getOpenInterest(symbols).catch((err) => {
					console.warn('Open interest API failed:', err);
					return [];
				}),
				getFundingRates(symbols).catch((err) => {
					console.warn('Funding rate API failed:', err);
					return [];
				})
			]);

			openInterestData = openInterest;
			fundingRateData = fundingRates;

			// Update market data with real data if available, otherwise use mock
			marketData = {
				...mockPrices[selectedSymbol] || { price: 103421, change: -0.32, volume: 6953950244.61 },
				openInterest: openInterest[0]?.value || Math.random() * 1000000000,
				fundingRate: fundingRates[0]?.value || (Math.random() - 0.5) * 0.001
			};

			console.log('Market data updated:', marketData);

		} catch (error) {
			console.error('Error loading market data:', error);
			// Use mock data as fallback
			marketData = {
				...mockPrices[selectedSymbol] || { price: 103421, change: -0.32, volume: 6953950244.61 },
				openInterest: Math.random() * 1000000000,
				fundingRate: (Math.random() - 0.5) * 0.001
			};
		} finally {
			isLoading = false;
		}
	}

	// Auto-refresh data
	function startAutoRefresh() {
		refreshInterval = setInterval(() => {
			loadMarketData();
		}, 10000); // Refresh every 10 seconds
	}

	function stopAutoRefresh() {
		if (refreshInterval) {
			clearInterval(refreshInterval);
			refreshInterval = null;
		}
	}

	// Initialize TradingView chart
	function initChart() {
		if (typeof window !== 'undefined' && window.TradingView) {
			new window.TradingView.widget({
				autosize: true,
				symbol: `BINANCE:${selectedSymbol}`,
				interval: "15",
				timezone: "Etc/UTC",
				theme: "dark",
				style: "1",
				locale: "en",
				toolbar_bg: "#1f2937",
				enable_publishing: false,
				hide_top_toolbar: false,
				hide_legend: true,
				save_image: false,
				container_id: "tradingview_chart",
				studies: [
					"Volume@tv-basicstudies"
				]
			});
		}
	}

	// Lifecycle
	onMount(() => {
		// Initialize order price
		orderPrice = formatPrice(mockPrices[selectedSymbol]?.price || 0);
		
		loadMarketData();
		startAutoRefresh();
		
		// Load TradingView script
		const script = document.createElement('script');
		script.src = 'https://s3.tradingview.com/tv.js';
		script.onload = initChart;
		document.head.appendChild(script);
	});

	onDestroy(() => {
		stopAutoRefresh();
	});

	// Handle symbol change
	function selectSymbol(symbol: string) {
		selectedSymbol = symbol;
		orderPrice = formatPrice(mockPrices[symbol]?.price || 0);
		loadMarketData();
	}

	// Handle order side change
	function setOrderSide(side: 'buy' | 'sell') {
		orderSide = side;
	}

	// Handle order submission
	function submitOrder() {
		if (!orderSize || !orderPrice) {
			toast.error('Please enter size and price');
			return;
		}

		const order = {
			symbol: selectedSymbol,
			side: orderSide,
			size: parseFloat(orderSize),
			price: parseFloat(orderPrice),
			type: 'limit'
		};

		console.log('Submitting order:', order);
		toast.success(`${orderSide.toUpperCase()} order submitted for ${orderSize} ${selectedSymbol} at ${orderPrice}`);
		
		// Clear form
		orderSize = '';
	}

	// Handle percentage buttons
	function setPercentage(percent: number) {
		// Mock available balance
		const availableBalance = 1000; // USDC
		const price = parseFloat(orderPrice) || mockPrices[selectedSymbol]?.price || 0;
		
		if (price > 0) {
			const sizeInBase = (availableBalance * percent / 100) / price;
			orderSize = sizeInBase.toFixed(6);
		}
	}
</script>

<svelte:head>
	<title>Trading - TradeBerg</title>
</svelte:head>

<div class="min-h-screen bg-black text-white font-mono">
	<!-- Top Navigation -->
	<div class="border-b border-gray-800 bg-gray-900/50 backdrop-blur">
		<div class="flex items-center justify-between px-6 py-3">
			<div class="flex items-center space-x-6">
				<div class="flex items-center space-x-2">
					<div class="w-2 h-2 bg-green-500 rounded-full"></div>
					<span class="text-sm font-medium">TradeBerg</span>
				</div>
				
				<nav class="flex items-center space-x-6 text-sm">
					<a href="#" class="text-white border-b-2 border-blue-500 pb-1">Trade</a>
					<a href="#" class="text-gray-400 hover:text-white transition-colors">Vaults</a>
					<a href="#" class="text-gray-400 hover:text-white transition-colors">Portfolio</a>
					<a href="#" class="text-gray-400 hover:text-white transition-colors">Staking</a>
					<a href="#" class="text-gray-400 hover:text-white transition-colors">Referrals</a>
					<a href="#" class="text-gray-400 hover:text-white transition-colors">Leaderboard</a>
				</nav>
			</div>

			<div class="flex items-center space-x-4">
				<a href="/" class="px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded text-sm transition-colors">
					← Back to Chat
				</a>
				<button class="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm font-medium transition-colors">
					Connect
				</button>
			</div>
		</div>
	</div>

	<div class="flex h-[calc(100vh-60px)]">
		<!-- Left Sidebar - Market List -->
		<div class="w-80 border-r border-gray-800 bg-gray-900/30">
			<div class="p-4 border-b border-gray-800">
				<h3 class="text-sm font-medium text-gray-300 mb-3">Markets</h3>
				<div class="relative">
					<input
						type="text"
						placeholder="Search markets..."
						class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
					/>
				</div>
			</div>

			<div class="overflow-y-auto">
				{#each popularPairs as symbol}
					<button
						on:click={() => selectSymbol(symbol)}
						class="w-full px-4 py-3 text-left hover:bg-gray-800/50 transition-colors border-b border-gray-800/50 {selectedSymbol === symbol ? 'bg-gray-800' : ''}"
					>
						<div class="flex items-center justify-between">
							<div>
								<div class="text-sm font-medium text-white">{symbol}</div>
								<div class="text-xs text-gray-500">Perp</div>
							</div>
							<div class="text-right">
								<div class="text-sm font-medium text-white">
									{formatPrice(mockPrices[symbol]?.price || 0)}
								</div>
								<div class="text-xs {(mockPrices[symbol]?.change || 0) >= 0 ? 'text-green-500' : 'text-red-500'}">
									{formatPercent(mockPrices[symbol]?.change || 0)}
								</div>
							</div>
						</div>
					</button>
				{/each}
			</div>
		</div>

		<!-- Main Content -->
		<div class="flex-1 flex flex-col">
			<!-- Market Header -->
			<div class="border-b border-gray-800 bg-gray-900/30 p-4">
				<div class="flex items-center justify-between">
					<div class="flex items-center space-x-6">
						<div class="flex items-center space-x-2">
							<div class="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center text-sm font-bold">
								₿
							</div>
							<div>
								<div class="text-lg font-bold text-white">{selectedSymbol}</div>
								<div class="text-xs text-gray-500">Perpetual</div>
							</div>
						</div>

						<div class="grid grid-cols-6 gap-6 text-sm">
							<div>
								<div class="text-gray-400 text-xs mb-1">Mark</div>
								<div class="font-medium text-white">{formatPrice(marketData.price || 0)}</div>
							</div>
							<div>
								<div class="text-gray-400 text-xs mb-1">Oracle</div>
								<div class="font-medium text-white">{formatPrice((marketData.price || 0) * 1.0001)}</div>
							</div>
							<div>
								<div class="text-gray-400 text-xs mb-1">24h Change</div>
								<div class="font-medium {(marketData.change || 0) >= 0 ? 'text-green-500' : 'text-red-500'}">
									{formatPercent(marketData.change || 0)}
								</div>
							</div>
							<div>
								<div class="text-gray-400 text-xs mb-1">24h Volume</div>
								<div class="font-medium text-white">{formatVolume(marketData.volume || 0)}</div>
							</div>
							<div>
								<div class="text-gray-400 text-xs mb-1">Open Interest</div>
								<div class="font-medium text-white">{formatVolume(marketData.openInterest || 0)}</div>
							</div>
							<div>
								<div class="text-gray-400 text-xs mb-1">Funding / Countdown</div>
								<div class="font-medium text-green-500">
									{formatFundingRate(marketData.fundingRate || 0)} / 00:47:1
								</div>
							</div>
						</div>
					</div>

					<div class="flex items-center space-x-2">
						<button
							on:click={loadMarketData}
							disabled={isLoading}
							class="p-2 hover:bg-gray-800 rounded transition-colors {isLoading ? 'animate-spin' : ''}"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
							</svg>
						</button>
					</div>
				</div>
			</div>

			<div class="flex flex-1">
				<!-- Chart Area -->
				<div class="flex-1 bg-gray-900/20 p-4">
					<div class="h-full bg-gray-800/30 rounded border border-gray-700 relative overflow-hidden">
						<!-- TradingView Widget -->
						<div id="tradingview_chart" class="w-full h-full">
							<!-- Fallback content -->
							<div class="flex items-center justify-center h-full text-center text-gray-500">
								<div>
									<div class="text-4xl mb-2">📈</div>
									<div class="text-lg font-medium">{selectedSymbol} Chart</div>
									<div class="text-sm">Loading TradingView chart...</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Right Panel - Trading -->
				<div class="w-80 border-l border-gray-800 bg-gray-900/30">
					<!-- Order Form -->
					<div class="p-4 border-b border-gray-800">
						<div class="flex space-x-1 mb-4">
							<button 
								on:click={() => setOrderSide('buy')}
								class="flex-1 py-2 px-3 rounded text-sm font-medium transition-colors {orderSide === 'buy' ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300'}"
							>
								Buy / Long
							</button>
							<button 
								on:click={() => setOrderSide('sell')}
								class="flex-1 py-2 px-3 rounded text-sm font-medium transition-colors {orderSide === 'sell' ? 'bg-red-600 text-white' : 'bg-gray-700 text-gray-300'}"
							>
								Sell / Short
							</button>
						</div>

						<div class="space-y-3">
							<div>
								<label class="block text-xs text-gray-400 mb-1">Market</label>
								<div class="text-sm text-white font-medium">{selectedSymbol}</div>
							</div>

							<div>
								<label class="block text-xs text-gray-400 mb-1">Cross</label>
								<div class="flex items-center justify-between">
									<span class="text-sm text-white">20x</span>
									<button class="text-xs text-blue-400 hover:text-blue-300">One-Way</button>
								</div>
							</div>

							<div>
								<label class="block text-xs text-gray-400 mb-1">Limit</label>
								<select class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-white">
									<option>Pro</option>
									<option>Limit</option>
									<option>Market</option>
								</select>
							</div>

							<div>
								<label class="block text-xs text-gray-400 mb-1">Available to Trade</label>
								<div class="text-sm text-white">0.00</div>
							</div>

							<div>
								<label class="block text-xs text-gray-400 mb-1">Current Position</label>
								<div class="text-sm text-white">0.00000 BTC</div>
							</div>

							<div>
								<label class="block text-xs text-gray-400 mb-1">Price (USDC)</label>
								<input
									type="text"
									bind:value={orderPrice}
									placeholder="0.00"
									class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-white focus:outline-none focus:border-blue-500"
								/>
								<div class="text-xs text-gray-500 mt-1">Mid</div>
							</div>

							<div>
								<label class="block text-xs text-gray-400 mb-1">Size</label>
								<div class="flex">
									<select class="px-3 py-2 bg-gray-800 border border-gray-700 rounded-l text-sm text-white focus:outline-none">
										<option>BTC</option>
										<option>USDC</option>
									</select>
									<input
										type="text"
										bind:value={orderSize}
										placeholder="0"
										class="flex-1 px-3 py-2 bg-gray-800 border-t border-b border-gray-700 text-sm text-white focus:outline-none focus:border-blue-500"
									/>
									<button class="px-3 py-2 bg-gray-700 border border-gray-700 rounded-r text-xs text-gray-300 hover:bg-gray-600 transition-colors">
										%
									</button>
								</div>
							</div>

							<div class="flex space-x-2 text-xs">
								<button on:click={() => setPercentage(25)} class="flex-1 py-1 bg-gray-700 hover:bg-gray-600 rounded text-gray-300 transition-colors">25%</button>
								<button on:click={() => setPercentage(50)} class="flex-1 py-1 bg-gray-700 hover:bg-gray-600 rounded text-gray-300 transition-colors">50%</button>
								<button on:click={() => setPercentage(75)} class="flex-1 py-1 bg-gray-700 hover:bg-gray-600 rounded text-gray-300 transition-colors">75%</button>
								<button on:click={() => setPercentage(100)} class="flex-1 py-1 bg-gray-700 hover:bg-gray-600 rounded text-gray-300 transition-colors">100%</button>
							</div>

							<div class="space-y-2 text-xs text-gray-400">
								<div class="flex justify-between">
									<span>Reduce Only</span>
									<input type="checkbox" class="rounded" />
								</div>
								<div class="flex justify-between">
									<span>Take Profit / Stop Loss</span>
									<input type="checkbox" class="rounded" />
								</div>
							</div>

							<button 
								on:click={submitOrder}
								class="w-full py-3 rounded font-medium transition-colors {orderSide === 'buy' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'} text-white"
							>
								{orderSide === 'buy' ? 'Buy / Long' : 'Sell / Short'}
							</button>
						</div>
					</div>

					<!-- Positions -->
					<div class="p-4">
						<h4 class="text-sm font-medium text-gray-300 mb-3">Positions</h4>
						<div class="text-center text-gray-500 py-8">
							<div class="text-2xl mb-2">📊</div>
							<div class="text-sm">No open positions</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	/* Custom scrollbar */
	:global(.overflow-y-auto::-webkit-scrollbar) {
		width: 4px;
	}
	
	:global(.overflow-y-auto::-webkit-scrollbar-track) {
		background: transparent;
	}
	
	:global(.overflow-y-auto::-webkit-scrollbar-thumb) {
		background: #374151;
		border-radius: 2px;
	}
	
	:global(.overflow-y-auto::-webkit-scrollbar-thumb:hover) {
		background: #4B5563;
	}
</style>
