<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, scale } from 'svelte/transition';
	
	export let symbol: string = 'BTC';
	export let show: boolean = true;
	
	let dots = 0;
	let dataPoints = [
		{ label: 'Price', loaded: false },
		{ label: 'Volume', loaded: false },
		{ label: 'Market Cap', loaded: false },
		{ label: 'Analysis', loaded: false }
	];
	
	onMount(() => {
		// Animate dots
		const dotsInterval = setInterval(() => {
			dots = (dots + 1) % 4;
		}, 500);
		
		// Simulate progressive data loading
		dataPoints.forEach((point, index) => {
			setTimeout(() => {
				dataPoints[index].loaded = true;
				dataPoints = [...dataPoints];
			}, (index + 1) * 300);
		});
		
		return () => clearInterval(dotsInterval);
	});
</script>

{#if show}
	<div class="live-loader" in:scale={{ duration: 300 }} out:fade={{ duration: 200 }}>
		<div class="loader-content">
			<!-- Animated Icon -->
			<div class="loader-icon">
				<div class="pulse-ring"></div>
				<div class="pulse-ring delay-1"></div>
				<div class="pulse-ring delay-2"></div>
				<span class="icon">📊</span>
			</div>
			
			<!-- Status Text -->
			<div class="loader-text">
				<h3>Fetching Live {symbol} Data{'.'.repeat(dots)}</h3>
				<p>Connecting to Binance API</p>
			</div>
			
			<!-- Progress Indicators -->
			<div class="data-progress">
				{#each dataPoints as point, i}
					<div class="progress-item" class:loaded={point.loaded}>
						<div class="check-icon">
							{#if point.loaded}
								<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
									<path d="M3 8L6 11L13 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
							{:else}
								<div class="spinner"></div>
							{/if}
						</div>
						<span>{point.label}</span>
					</div>
				{/each}
			</div>
			
			<!-- Loading Bar -->
			<div class="loading-bar">
				<div class="loading-bar-fill"></div>
			</div>
		</div>
	</div>
{/if}

<style>
	.live-loader {
		background: linear-gradient(135deg, rgba(15, 15, 20, 0.95) 0%, rgba(20, 20, 30, 0.95) 100%);
		backdrop-filter: blur(20px);
		border-radius: 16px;
		border: 1px solid rgba(102, 126, 234, 0.3);
		padding: 24px;
		margin: 16px 0;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
		position: relative;
		overflow: hidden;
	}
	
	.live-loader::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 2px;
		background: linear-gradient(90deg, transparent, #667eea, transparent);
		animation: shimmer 2s linear infinite;
	}
	
	@keyframes shimmer {
		0% { left: -100%; }
		100% { left: 100%; }
	}
	
	.loader-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 20px;
	}
	
	/* Animated Icon */
	.loader-icon {
		position: relative;
		width: 80px;
		height: 80px;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.pulse-ring {
		position: absolute;
		width: 100%;
		height: 100%;
		border: 2px solid rgba(102, 126, 234, 0.6);
		border-radius: 50%;
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}
	
	.pulse-ring.delay-1 {
		animation-delay: 0.4s;
	}
	
	.pulse-ring.delay-2 {
		animation-delay: 0.8s;
	}
	
	@keyframes pulse {
		0% {
			transform: scale(0.8);
			opacity: 1;
		}
		100% {
			transform: scale(1.4);
			opacity: 0;
		}
	}
	
	.icon {
		font-size: 32px;
		z-index: 1;
		animation: bounce 1s ease-in-out infinite;
	}
	
	@keyframes bounce {
		0%, 100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-8px);
		}
	}
	
	/* Status Text */
	.loader-text {
		text-align: center;
	}
	
	.loader-text h3 {
		font-size: 18px;
		font-weight: 700;
		color: #fff;
		margin: 0 0 8px 0;
		letter-spacing: -0.5px;
	}
	
	.loader-text p {
		font-size: 13px;
		color: #9ca3af;
		margin: 0;
	}
	
	/* Progress Indicators */
	.data-progress {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 12px;
		width: 100%;
		max-width: 300px;
	}
	
	.progress-item {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 12px;
		background: rgba(255, 255, 255, 0.03);
		border-radius: 8px;
		border: 1px solid rgba(255, 255, 255, 0.06);
		transition: all 0.3s ease;
	}
	
	.progress-item.loaded {
		background: rgba(16, 185, 129, 0.1);
		border-color: rgba(16, 185, 129, 0.3);
	}
	
	.check-icon {
		width: 16px;
		height: 16px;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #9ca3af;
	}
	
	.progress-item.loaded .check-icon {
		color: #10b981;
	}
	
	.spinner {
		width: 12px;
		height: 12px;
		border: 2px solid rgba(156, 163, 175, 0.3);
		border-top-color: #9ca3af;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
	
	.progress-item span {
		font-size: 12px;
		color: #9ca3af;
		font-weight: 500;
	}
	
	.progress-item.loaded span {
		color: #10b981;
	}
	
	/* Loading Bar */
	.loading-bar {
		width: 100%;
		height: 4px;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 2px;
		overflow: hidden;
	}
	
	.loading-bar-fill {
		height: 100%;
		background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
		background-size: 200% 100%;
		animation: loading 2s ease-in-out infinite;
		border-radius: 2px;
	}
	
	@keyframes loading {
		0% {
			width: 0%;
			background-position: 0% 0%;
		}
		50% {
			width: 70%;
			background-position: 100% 0%;
		}
		100% {
			width: 100%;
			background-position: 200% 0%;
		}
	}
	
	/* Responsive */
	@media (max-width: 768px) {
		.live-loader {
			padding: 20px;
		}
		
		.loader-icon {
			width: 60px;
			height: 60px;
		}
		
		.icon {
			font-size: 24px;
		}
		
		.data-progress {
			grid-template-columns: 1fr;
		}
	}
</style>
