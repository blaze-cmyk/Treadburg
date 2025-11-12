<!--
	TradingView Chart Widget for TradeBerg
	
	Simple TradingView widget that can be captured by the chart capture button
-->

<script lang="ts">
	import { onMount } from 'svelte';
	
	export let symbol = 'BINANCE:BTCUSDT';
	export let interval = '15';
	export let theme = 'dark';
	export let width = '100%';
	export let height = '600';
	
	let container: HTMLDivElement;
	let widgetLoaded = false;
	
	onMount(() => {
		// Load TradingView widget script
		const script = document.createElement('script');
		script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
		script.async = true;
		script.innerHTML = JSON.stringify({
			"autosize": false,
			"width": width,
			"height": height,
			"symbol": symbol,
			"interval": interval,
			"timezone": "Etc/UTC",
			"theme": theme,
			"style": "1",
			"locale": "en",
			"enable_publishing": false,
			"withdateranges": true,
			"range": "YTD",
			"hide_side_toolbar": false,
			"allow_symbol_change": true,
			"details": true,
			"hotlist": true,
			"calendar": false,
			"support_host": "https://www.tradingview.com"
		});
		
		container.appendChild(script);
		
		// Mark as loaded after a delay
		setTimeout(() => {
			widgetLoaded = true;
		}, 2000);
	});
</script>

<!-- TradingView Widget Container -->
<div class="tradingview-widget-container" id="tradeberg-chart">
	<div class="tradingview-widget-container__widget" bind:this={container}></div>
	
	{#if !widgetLoaded}
		<div class="absolute inset-0 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm">
			<div class="text-center">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
				<p class="text-gray-300 text-sm">Loading TradingView Chart...</p>
			</div>
		</div>
	{/if}
</div>

<style>
	.tradingview-widget-container {
		position: relative;
		background: #1a1a1a;
		border-radius: 8px;
		overflow: hidden;
	}
	
	.tradingview-widget-container__widget {
		height: 100%;
	}
</style>
