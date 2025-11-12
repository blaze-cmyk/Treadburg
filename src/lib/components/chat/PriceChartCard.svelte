<!--
	Compact TradingView Chart Card for Chat Messages
	Shows automatically when user asks about cryptocurrency prices
-->

<script lang="ts">
	import { onMount } from 'svelte';
	
	export let symbol = 'BINANCE:BTCUSDT';
	export let interval = '15';
	export let coinName = 'Bitcoin';
	
	let container: HTMLDivElement;
	let widgetLoaded = false;
	let error = false;
	
	onMount(() => {
		try {
			// Load TradingView widget script
			const script = document.createElement('script');
			script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
			script.async = true;
			script.innerHTML = JSON.stringify({
				"autosize": false,
				"width": "100%",
				"height": "300",
				"symbol": symbol,
				"interval": interval,
				"timezone": "Etc/UTC",
				"theme": "dark",
				"style": "1",
				"locale": "en",
				"enable_publishing": false,
				"withdateranges": false,
				"hide_side_toolbar": true,
				"allow_symbol_change": false,
				"details": false,
				"hotlist": false,
				"calendar": false,
				"support_host": "https://www.tradingview.com"
			});
			
			container.appendChild(script);
			
			// Mark as loaded after delay
			setTimeout(() => {
				widgetLoaded = true;
			}, 2000);
		} catch (e) {
			console.error('Failed to load TradingView widget:', e);
			error = true;
		}
	});
</script>

<div class="price-chart-card">
	<div class="chart-header">
		<div class="flex items-center gap-2">
			<span class="chart-icon">📊</span>
			<span class="chart-title">{coinName} Price Chart</span>
		</div>
		<span class="chart-badge">Live</span>
	</div>
	
	<div class="chart-container">
		{#if error}
			<div class="chart-error">
				<span>❌</span>
				<p>Failed to load chart</p>
			</div>
		{:else}
			<div class="tradingview-widget" bind:this={container}></div>
			
			{#if !widgetLoaded}
				<div class="chart-loading">
					<div class="spinner"></div>
					<p>Loading chart...</p>
				</div>
			{/if}
		{/if}
	</div>
	
	<div class="chart-footer">
		<span class="footer-text">Powered by TradingView</span>
	</div>
</div>

<style>
	.price-chart-card {
		background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
		border: 1px solid #374151;
		border-radius: 12px;
		overflow: hidden;
		margin: 16px 0;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
	}
	
	.chart-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 16px;
		background: rgba(59, 130, 246, 0.1);
		border-bottom: 1px solid #374151;
	}
	
	.chart-icon {
		font-size: 20px;
	}
	
	.chart-title {
		font-size: 14px;
		font-weight: 600;
		color: #f3f4f6;
	}
	
	.chart-badge {
		background: #10b981;
		color: white;
		padding: 2px 8px;
		border-radius: 4px;
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
		animation: pulse 2s infinite;
	}
	
	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.7; }
	}
	
	.chart-container {
		position: relative;
		height: 300px;
		background: #0a0a0a;
	}
	
	.tradingview-widget {
		width: 100%;
		height: 100%;
	}
	
	.chart-loading {
		position: absolute;
		inset: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background: rgba(0, 0, 0, 0.7);
		backdrop-filter: blur(4px);
		gap: 12px;
	}
	
	.spinner {
		width: 32px;
		height: 32px;
		border: 3px solid #374151;
		border-top-color: #3b82f6;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
	
	.chart-loading p {
		color: #9ca3af;
		font-size: 13px;
	}
	
	.chart-error {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: #ef4444;
		gap: 8px;
	}
	
	.chart-error span {
		font-size: 32px;
	}
	
	.chart-error p {
		font-size: 14px;
	}
	
	.chart-footer {
		padding: 8px 16px;
		background: rgba(0, 0, 0, 0.3);
		border-top: 1px solid #374151;
		text-align: center;
	}
	
	.footer-text {
		color: #6b7280;
		font-size: 11px;
	}
	
	/* Responsive */
	@media (max-width: 640px) {
		.chart-container {
			height: 250px;
		}
	}
</style>
