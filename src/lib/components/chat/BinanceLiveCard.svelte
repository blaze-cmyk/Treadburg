<script lang="ts">
	import { onMount } from 'svelte';
	
	export let symbol: string = 'BTC';
	export let price: number = 0;
	export let change24h: number = 0;
	export let high24h: number = 0;
	export let low24h: number = 0;
	export let volume24h: number = 0;
	export let buyPressure: number = 50;
	export let bidRatio: number = 50;
	export let askRatio: number = 50;
	export let timestamp: string = '';
	
	let isVisible = false;
	
	onMount(() => {
		// Trigger animation after mount
		setTimeout(() => {
			isVisible = true;
		}, 50);
	});
	
	$: isPositive = change24h >= 0;
	$: formattedPrice = price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	$: formattedVolume = (volume24h / 1e9).toFixed(2);
</script>

<div class="binance-live-card" class:visible={isVisible}>
	<!-- Shimmer overlay -->
	<div class="shimmer-overlay"></div>
	
	<!-- Header -->
	<div class="card-header">
		<h3>🔴 LIVE BINANCE DATA</h3>
	</div>
	
	<!-- Price Display -->
	<div class="price-display">
		<div class="crypto-symbol">{symbol}/USDT</div>
		<div class="current-price">${formattedPrice}</div>
		<div class="price-change" class:positive={isPositive} class:negative={!isPositive}>
			{isPositive ? '+' : ''}{change24h.toFixed(2)}% (24h)
		</div>
	</div>
	
	<!-- Market Metrics -->
	<div class="market-metrics">
		<div class="metric">
			<span class="metric-label">24h High</span>
			<span class="metric-value">${high24h.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
		</div>
		<div class="metric">
			<span class="metric-label">24h Low</span>
			<span class="metric-value">${low24h.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
		</div>
		<div class="metric">
			<span class="metric-label">24h Volume</span>
			<span class="metric-value">${formattedVolume}B</span>
		</div>
		<div class="metric">
			<span class="metric-label">Buy Pressure</span>
			<span class="metric-value">{buyPressure.toFixed(1)}%</span>
		</div>
	</div>
	
	<!-- Liquidity Bar -->
	<div class="liquidity-bar">
		<div class="bid-side" style="width: {bidRatio}%">
			<span>Bid {bidRatio.toFixed(1)}%</span>
		</div>
		<div class="ask-side" style="width: {askRatio}%">
			<span>Ask {askRatio.toFixed(1)}%</span>
		</div>
	</div>
	
	<!-- Footer -->
	<div class="data-footer">
		<span class="live-indicator">
			<span class="pulse-dot"></span>
			LIVE
		</span>
		<span class="timestamp">{timestamp}</span>
	</div>
</div>

<style>
	@import '../../../styles/binance-card.css';
	
	.binance-live-card {
		opacity: 0;
		transform: scale(0.8) translateY(20px);
		transition: all 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
	}
	
	.binance-live-card.visible {
		opacity: 1;
		transform: scale(1) translateY(0);
	}
	
	.card-header h3 {
		margin: 0 0 16px 0;
		font-size: 16px;
		font-weight: 700;
		color: #f39c12;
		text-transform: uppercase;
		letter-spacing: 2px;
		text-align: center;
	}
	
	.pulse-dot {
		display: inline-block;
		width: 8px;
		height: 8px;
		background: #e74c3c;
		border-radius: 50%;
		margin-right: 6px;
		animation: pulse-dot 1.5s ease-in-out infinite;
	}
	
	@keyframes pulse-dot {
		0%, 100% {
			opacity: 1;
			transform: scale(1);
		}
		50% {
			opacity: 0.5;
			transform: scale(1.2);
		}
	}
</style>
