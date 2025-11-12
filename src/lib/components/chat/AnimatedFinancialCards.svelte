<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { quintOut, elasticOut } from 'svelte/easing';
	
	export let data: any = null;
	
	let mounted = false;
	let animatedValues: any = {};
	
	onMount(() => {
		mounted = true;
		if (data) {
			animateValues();
		}
	});
	
	$: if (data && mounted) {
		animateValues();
	}
	
	function animateValues() {
		// Animate numbers counting up
		const metrics = data.metrics || [];
		metrics.forEach((metric: any, index: number) => {
			setTimeout(() => {
				animateNumber(metric.label, 0, parseFloat(metric.value.replace(/[^0-9.-]/g, '')), 1000);
			}, index * 100);
		});
	}
	
	function animateNumber(key: string, start: number, end: number, duration: number) {
		const startTime = Date.now();
		const animate = () => {
			const now = Date.now();
			const progress = Math.min((now - startTime) / duration, 1);
			const eased = quintOut(progress);
			const current = start + (end - start) * eased;
			
			animatedValues[key] = current;
			
			if (progress < 1) {
				requestAnimationFrame(animate);
			}
		};
		animate();
	}
	
	function formatValue(value: number, originalFormat: string): string {
		if (originalFormat.includes('$')) {
			return '$' + value.toFixed(2);
		} else if (originalFormat.includes('B')) {
			return value.toFixed(1) + 'B';
		} else if (originalFormat.includes('%')) {
			return value.toFixed(1) + '%';
		}
		return value.toFixed(2);
	}
	
	function getChangeColor(change: string): string {
		if (change.startsWith('+')) return '#10b981';
		if (change.startsWith('-')) return '#ef4444';
		return '#6b7280';
	}
</script>

<div class="animated-financial-cards" class:mounted>
	{#if data}
		<!-- Header Section -->
		<div class="card-header" in:fly={{ y: -20, duration: 600, easing: quintOut }}>
			<div class="symbol-info">
				<div class="symbol-icon">
					<span class="icon-pulse">₿</span>
				</div>
				<div class="symbol-details">
					<h2 class="symbol-name">{data.symbol || 'BTC/USDT'}</h2>
					<p class="symbol-exchange">Binance • Live</p>
				</div>
			</div>
			<div class="live-badge">
				<span class="pulse-dot"></span>
				LIVE
			</div>
		</div>
		
		<!-- Price Card (Large) -->
		{#if data.price}
			<div 
				class="price-card-large"
				in:scale={{ duration: 800, delay: 100, easing: elasticOut }}
			>
				<div class="price-label">Current Price</div>
				<div class="price-value">
					{#if animatedValues['price']}
						{formatValue(animatedValues['price'], data.price)}
					{:else}
						{data.price}
					{/if}
				</div>
				{#if data.change}
					<div class="price-change" style="color: {getChangeColor(data.change)}">
						<span class="change-arrow">
							{data.change.startsWith('+') ? '↗' : '↘'}
						</span>
						{data.change}
					</div>
				{/if}
			</div>
		{/if}
		
		<!-- Metrics Grid -->
		{#if data.metrics && data.metrics.length > 0}
			<div class="metrics-grid">
				{#each data.metrics as metric, i}
					<div 
						class="metric-card"
						in:fly={{ y: 20, duration: 500, delay: 200 + (i * 80), easing: quintOut }}
					>
						<div class="metric-header">
							<span class="metric-label">{metric.label}</span>
							{#if metric.change}
								<span 
									class="metric-change"
									style="color: {getChangeColor(metric.change)}"
								>
									{metric.change}
								</span>
							{/if}
						</div>
						<div class="metric-value">
							{#if animatedValues[metric.label]}
								{formatValue(animatedValues[metric.label], metric.value)}
							{:else}
								{metric.value}
							{/if}
						</div>
						{#if metric.status}
							<div class="metric-status">
								<span class="status-indicator" style="background: {getChangeColor(metric.change || '+')}"></span>
								{metric.status}
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
		
		<!-- Timestamp -->
		<div class="timestamp" in:fade={{ delay: 800, duration: 400 }}>
			<svg width="12" height="12" viewBox="0 0 12 12" fill="none">
				<circle cx="6" cy="6" r="5" stroke="currentColor" stroke-width="1"/>
				<path d="M6 3V6L8 8" stroke="currentColor" stroke-width="1" stroke-linecap="round"/>
			</svg>
			Updated: {data.timestamp || 'Just now'}
		</div>
	{/if}
</div>

<style>
	.animated-financial-cards {
		width: 100%;
		padding: 20px;
		background: linear-gradient(135deg, rgba(15, 15, 20, 0.98) 0%, rgba(20, 20, 30, 0.98) 100%);
		border-radius: 20px;
		border: 1px solid rgba(255, 255, 255, 0.08);
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
		position: relative;
		overflow: hidden;
		opacity: 0;
		transform: translateY(20px);
		transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
	}
	
	.animated-financial-cards.mounted {
		opacity: 1;
		transform: translateY(0);
	}
	
	.animated-financial-cards::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 2px;
		background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #4facfe);
		background-size: 200% 100%;
		animation: shimmer 3s linear infinite;
	}
	
	@keyframes shimmer {
		0% { background-position: -200% 0; }
		100% { background-position: 200% 0; }
	}
	
	/* Header */
	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24px;
		padding-bottom: 16px;
		border-bottom: 1px solid rgba(255, 255, 255, 0.06);
	}
	
	.symbol-info {
		display: flex;
		align-items: center;
		gap: 12px;
	}
	
	.symbol-icon {
		width: 48px;
		height: 48px;
		background: linear-gradient(135deg, #667eea, #764ba2);
		border-radius: 12px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 24px;
		box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
		animation: iconPulse 2s ease-in-out infinite;
	}
	
	@keyframes iconPulse {
		0%, 100% {
			transform: scale(1);
			box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
		}
		50% {
			transform: scale(1.05);
			box-shadow: 0 6px 24px rgba(102, 126, 234, 0.5);
		}
	}
	
	.icon-pulse {
		animation: pulse 2s ease-in-out infinite;
	}
	
	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.7; }
	}
	
	.symbol-details {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
	
	.symbol-name {
		font-size: 20px;
		font-weight: 700;
		color: #fff;
		margin: 0;
		letter-spacing: -0.5px;
	}
	
	.symbol-exchange {
		font-size: 13px;
		color: #9ca3af;
		margin: 0;
	}
	
	.live-badge {
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 6px 12px;
		background: rgba(16, 185, 129, 0.15);
		border: 1px solid rgba(16, 185, 129, 0.3);
		border-radius: 20px;
		font-size: 11px;
		font-weight: 700;
		color: #10b981;
		letter-spacing: 0.5px;
	}
	
	.pulse-dot {
		width: 6px;
		height: 6px;
		background: #10b981;
		border-radius: 50%;
		animation: pulseDot 1.5s ease-in-out infinite;
	}
	
	@keyframes pulseDot {
		0%, 100% {
			opacity: 1;
			transform: scale(1);
		}
		50% {
			opacity: 0.5;
			transform: scale(1.3);
		}
	}
	
	/* Large Price Card */
	.price-card-large {
		background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
		border: 1px solid rgba(102, 126, 234, 0.2);
		border-radius: 16px;
		padding: 24px;
		margin-bottom: 20px;
		text-align: center;
		position: relative;
		overflow: hidden;
	}
	
	.price-card-large::before {
		content: '';
		position: absolute;
		top: -50%;
		left: -50%;
		width: 200%;
		height: 200%;
		background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
		animation: rotate 10s linear infinite;
	}
	
	@keyframes rotate {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
	
	.price-label {
		font-size: 12px;
		color: #9ca3af;
		text-transform: uppercase;
		letter-spacing: 1px;
		margin-bottom: 8px;
		position: relative;
		z-index: 1;
	}
	
	.price-value {
		font-size: 48px;
		font-weight: 800;
		color: #fff;
		margin-bottom: 8px;
		font-family: 'Courier New', monospace;
		letter-spacing: -2px;
		position: relative;
		z-index: 1;
		text-shadow: 0 2px 20px rgba(102, 126, 234, 0.3);
	}
	
	.price-change {
		font-size: 18px;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 6px;
		position: relative;
		z-index: 1;
	}
	
	.change-arrow {
		font-size: 24px;
		animation: bounce 1s ease-in-out infinite;
	}
	
	@keyframes bounce {
		0%, 100% { transform: translateY(0); }
		50% { transform: translateY(-4px); }
	}
	
	/* Metrics Grid */
	.metrics-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
		gap: 12px;
		margin-bottom: 16px;
	}
	
	.metric-card {
		background: rgba(255, 255, 255, 0.03);
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.08);
		border-radius: 12px;
		padding: 16px;
		transition: all 0.3s ease;
		cursor: pointer;
	}
	
	.metric-card:hover {
		background: rgba(255, 255, 255, 0.05);
		border-color: rgba(102, 126, 234, 0.3);
		transform: translateY(-2px);
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
	}
	
	.metric-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
	}
	
	.metric-label {
		font-size: 11px;
		color: #9ca3af;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}
	
	.metric-change {
		font-size: 11px;
		font-weight: 700;
	}
	
	.metric-value {
		font-size: 24px;
		font-weight: 700;
		color: #fff;
		font-family: 'Courier New', monospace;
		margin-bottom: 6px;
	}
	
	.metric-status {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 11px;
		color: #9ca3af;
	}
	
	.status-indicator {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		animation: pulseDot 1.5s ease-in-out infinite;
	}
	
	/* Timestamp */
	.timestamp {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 11px;
		color: #6b7280;
		justify-content: center;
		padding-top: 12px;
		border-top: 1px solid rgba(255, 255, 255, 0.06);
	}
	
	/* Responsive */
	@media (max-width: 768px) {
		.animated-financial-cards {
			padding: 16px;
		}
		
		.price-value {
			font-size: 36px;
		}
		
		.metrics-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}
</style>
