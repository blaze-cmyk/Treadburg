<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';
	
	export let marketData: any;
	
	let cardContainer: HTMLDivElement;
	let priceChartSvg: SVGSVGElement;
	let volumeChartSvg: SVGSVGElement;
	let liquidityGaugeSvg: SVGSVGElement;
	
	let isVisible = false;
	
	onMount(() => {
		// Trigger entrance animation
		setTimeout(() => {
			isVisible = true;
			if (marketData) {
				createPriceChart();
				createVolumeChart();
				createLiquidityGauge();
			}
		}, 100);
	});
	
	function createPriceChart() {
		if (!priceChartSvg || !marketData?.candlestick_data) return;
		
		const margin = { top: 10, right: 10, bottom: 20, left: 50 };
		const width = 400 - margin.left - margin.right;
		const height = 150 - margin.top - margin.bottom;
		
		const svg = d3.select(priceChartSvg)
			.attr('width', width + margin.left + margin.right)
			.attr('height', height + margin.top + margin.bottom);
		
		svg.selectAll('*').remove();
		
		const g = svg.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);
		
		// Parse candlestick data
		const data = marketData.candlestick_data.slice(-24).map((d: any, i: number) => ({
			index: i,
			open: d[1],
			high: d[2],
			low: d[3],
			close: d[4],
			volume: d[5]
		}));
		
		// Scales
		const x = d3.scaleLinear()
			.domain([0, data.length - 1])
			.range([0, width]);
		
		const y = d3.scaleLinear()
			.domain([
				d3.min(data, d => d.low) * 0.999,
				d3.max(data, d => d.high) * 1.001
			])
			.range([height, 0]);
		
		// Grid lines
		g.append('g')
			.attr('class', 'grid')
			.attr('opacity', 0.1)
			.call(d3.axisLeft(y)
				.tickSize(-width)
				.tickFormat(() => '')
			);
		
		// Line path
		const line = d3.line<any>()
			.x(d => x(d.index))
			.y(d => y(d.close))
			.curve(d3.curveMonotoneX);
		
		// Area gradient
		const gradient = g.append('defs')
			.append('linearGradient')
			.attr('id', 'price-gradient')
			.attr('x1', '0%')
			.attr('y1', '0%')
			.attr('x2', '0%')
			.attr('y2', '100%');
		
		gradient.append('stop')
			.attr('offset', '0%')
			.attr('stop-color', marketData.price.change_24h >= 0 ? '#10b981' : '#ef4444')
			.attr('stop-opacity', 0.3);
		
		gradient.append('stop')
			.attr('offset', '100%')
			.attr('stop-color', marketData.price.change_24h >= 0 ? '#10b981' : '#ef4444')
			.attr('stop-opacity', 0);
		
		// Area
		const area = d3.area<any>()
			.x(d => x(d.index))
			.y0(height)
			.y1(d => y(d.close))
			.curve(d3.curveMonotoneX);
		
		g.append('path')
			.datum(data)
			.attr('fill', 'url(#price-gradient)')
			.attr('d', area)
			.attr('opacity', 0)
			.transition()
			.duration(1000)
			.attr('opacity', 1);
		
		// Line
		const path = g.append('path')
			.datum(data)
			.attr('fill', 'none')
			.attr('stroke', marketData.price.change_24h >= 0 ? '#10b981' : '#ef4444')
			.attr('stroke-width', 2)
			.attr('d', line);
		
		// Animate line drawing
		const totalLength = path.node()?.getTotalLength() || 0;
		path
			.attr('stroke-dasharray', `${totalLength} ${totalLength}`)
			.attr('stroke-dashoffset', totalLength)
			.transition()
			.duration(1500)
			.ease(d3.easeLinear)
			.attr('stroke-dashoffset', 0);
		
		// Current price indicator
		const lastPoint = data[data.length - 1];
		g.append('circle')
			.attr('cx', x(lastPoint.index))
			.attr('cy', y(lastPoint.close))
			.attr('r', 0)
			.attr('fill', marketData.price.change_24h >= 0 ? '#10b981' : '#ef4444')
			.attr('stroke', '#fff')
			.attr('stroke-width', 2)
			.transition()
			.delay(1500)
			.duration(500)
			.attr('r', 5);
		
		// Axes
		g.append('g')
			.attr('transform', `translate(0,${height})`)
			.attr('color', '#6b7280')
			.call(d3.axisBottom(x).ticks(5).tickFormat(() => ''));
		
		g.append('g')
			.attr('color', '#6b7280')
			.call(d3.axisLeft(y).ticks(5).tickFormat(d => `$${d3.format('.0f')(d as number)}`));
	}
	
	function createVolumeChart() {
		if (!volumeChartSvg || !marketData) return;
		
		const margin = { top: 5, right: 10, bottom: 20, left: 50 };
		const width = 400 - margin.left - margin.right;
		const height = 60 - margin.top - margin.bottom;
		
		const svg = d3.select(volumeChartSvg)
			.attr('width', width + margin.left + margin.right)
			.attr('height', height + margin.top + margin.bottom);
		
		svg.selectAll('*').remove();
		
		const g = svg.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);
		
		const data = [
			{ label: 'Buy', value: marketData.volume_metrics.buy_volume, color: '#10b981' },
			{ label: 'Sell', value: marketData.volume_metrics.sell_volume, color: '#ef4444' }
		];
		
		const x = d3.scaleBand()
			.domain(data.map(d => d.label))
			.range([0, width])
			.padding(0.3);
		
		const y = d3.scaleLinear()
			.domain([0, d3.max(data, d => d.value) * 1.1])
			.range([height, 0]);
		
		// Bars
		g.selectAll('.bar')
			.data(data)
			.enter()
			.append('rect')
			.attr('class', 'bar')
			.attr('x', d => x(d.label))
			.attr('width', x.bandwidth())
			.attr('y', height)
			.attr('height', 0)
			.attr('fill', d => d.color)
			.attr('rx', 4)
			.transition()
			.duration(1000)
			.delay((d, i) => i * 200)
			.attr('y', d => y(d.value))
			.attr('height', d => height - y(d.value));
		
		// Labels
		g.selectAll('.label')
			.data(data)
			.enter()
			.append('text')
			.attr('class', 'label')
			.attr('x', d => x(d.label) + x.bandwidth() / 2)
			.attr('y', d => y(d.value) - 5)
			.attr('text-anchor', 'middle')
			.attr('fill', '#fff')
			.attr('font-size', '10px')
			.attr('opacity', 0)
			.text(d => d3.format('.2s')(d.value))
			.transition()
			.delay(1200)
			.duration(500)
			.attr('opacity', 1);
		
		// Axis
		g.append('g')
			.attr('transform', `translate(0,${height})`)
			.attr('color', '#6b7280')
			.call(d3.axisBottom(x));
	}
	
	function createLiquidityGauge() {
		if (!liquidityGaugeSvg || !marketData) return;
		
		const width = 400;
		const height = 80;
		const margin = { top: 20, right: 20, bottom: 20, left: 20 };
		
		const svg = d3.select(liquidityGaugeSvg)
			.attr('width', width)
			.attr('height', height);
		
		svg.selectAll('*').remove();
		
		const g = svg.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);
		
		const gaugeWidth = width - margin.left - margin.right;
		const gaugeHeight = 30;
		
		const bidRatio = marketData.liquidity.bid_ratio;
		const askRatio = marketData.liquidity.ask_ratio;
		
		// Background
		g.append('rect')
			.attr('x', 0)
			.attr('y', 0)
			.attr('width', gaugeWidth)
			.attr('height', gaugeHeight)
			.attr('fill', '#1f2937')
			.attr('rx', 8);
		
		// Bid bar
		g.append('rect')
			.attr('x', 0)
			.attr('y', 0)
			.attr('width', 0)
			.attr('height', gaugeHeight)
			.attr('fill', '#10b981')
			.attr('rx', 8)
			.transition()
			.duration(1500)
			.attr('width', gaugeWidth * (bidRatio / 100));
		
		// Ask bar
		g.append('rect')
			.attr('x', gaugeWidth)
			.attr('y', 0)
			.attr('width', 0)
			.attr('height', gaugeHeight)
			.attr('fill', '#ef4444')
			.attr('rx', 8)
			.transition()
			.duration(1500)
			.attr('x', gaugeWidth * (bidRatio / 100))
			.attr('width', gaugeWidth * (askRatio / 100));
		
		// Labels
		g.append('text')
			.attr('x', gaugeWidth * (bidRatio / 200))
			.attr('y', gaugeHeight / 2 + 5)
			.attr('text-anchor', 'middle')
			.attr('fill', '#fff')
			.attr('font-weight', 'bold')
			.attr('font-size', '12px')
			.attr('opacity', 0)
			.text(`Bid ${bidRatio.toFixed(1)}%`)
			.transition()
			.delay(1500)
			.duration(500)
			.attr('opacity', 1);
		
		g.append('text')
			.attr('x', gaugeWidth * (bidRatio / 100) + gaugeWidth * (askRatio / 200))
			.attr('y', gaugeHeight / 2 + 5)
			.attr('text-anchor', 'middle')
			.attr('fill', '#fff')
			.attr('font-weight', 'bold')
			.attr('font-size', '12px')
			.attr('opacity', 0)
			.text(`Ask ${askRatio.toFixed(1)}%`)
			.transition()
			.delay(1500)
			.duration(500)
			.attr('opacity', 1);
	}
	
	$: if (marketData && priceChartSvg && volumeChartSvg && liquidityGaugeSvg) {
		createPriceChart();
		createVolumeChart();
		createLiquidityGauge();
	}
</script>

<div class="binance-d3-card" class:visible={isVisible} bind:this={cardContainer}>
	<!-- Header -->
	<div class="card-header">
		<div class="header-left">
			<div class="live-badge">
				<span class="pulse-dot"></span>
				<span>LIVE</span>
			</div>
			<h2>Binance Market Data</h2>
		</div>
		<div class="timestamp">{new Date(marketData?.timestamp).toLocaleTimeString()}</div>
	</div>
	
	<!-- Price Display -->
	<div class="price-section">
		<div class="symbol">{marketData?.symbol}/USDT</div>
		<div class="price-main">
			<span class="price">${marketData?.price.current.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
			<span class="change" class:positive={marketData?.price.change_24h >= 0} class:negative={marketData?.price.change_24h < 0}>
				{marketData?.price.change_24h >= 0 ? '+' : ''}{marketData?.price.change_24h.toFixed(2)}%
			</span>
		</div>
	</div>
	
	<!-- Price Chart -->
	<div class="chart-section">
		<div class="chart-title">24h Price Movement</div>
		<svg bind:this={priceChartSvg}></svg>
	</div>
	
	<!-- Metrics Grid -->
	<div class="metrics-grid">
		<div class="metric">
			<div class="metric-label">24h High</div>
			<div class="metric-value">${marketData?.price.high_24h.toLocaleString()}</div>
		</div>
		<div class="metric">
			<div class="metric-label">24h Low</div>
			<div class="metric-value">${marketData?.price.low_24h.toLocaleString()}</div>
		</div>
		<div class="metric">
			<div class="metric-label">24h Volume</div>
			<div class="metric-value">${(marketData?.price.quote_volume_24h / 1e9).toFixed(2)}B</div>
		</div>
		<div class="metric">
			<div class="metric-label">Buy Pressure</div>
			<div class="metric-value">{marketData?.volume_metrics.buy_pressure.toFixed(1)}%</div>
		</div>
	</div>
	
	<!-- Volume Chart -->
	<div class="chart-section">
		<div class="chart-title">Buy vs Sell Volume</div>
		<svg bind:this={volumeChartSvg}></svg>
	</div>
	
	<!-- Liquidity Gauge -->
	<div class="chart-section">
		<div class="chart-title">Liquidity Distribution</div>
		<svg bind:this={liquidityGaugeSvg}></svg>
	</div>
</div>

<style>
	.binance-d3-card {
		background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
		border: 2px solid #f59e0b;
		border-radius: 20px;
		padding: 24px;
		margin: 20px 0;
		box-shadow: 
			0 20px 60px rgba(245, 158, 11, 0.3),
			0 0 0 1px rgba(245, 158, 11, 0.1),
			inset 0 1px 0 rgba(255, 255, 255, 0.1);
		position: relative;
		overflow: hidden;
		opacity: 0;
		transform: scale(0.9) translateY(20px);
		transition: all 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
	}
	
	.binance-d3-card.visible {
		opacity: 1;
		transform: scale(1) translateY(0);
	}
	
	/* Animated background gradient */
	.binance-d3-card::before {
		content: '';
		position: absolute;
		top: -50%;
		left: -50%;
		width: 200%;
		height: 200%;
		background: radial-gradient(circle, rgba(245, 158, 11, 0.1) 0%, transparent 70%);
		animation: rotate 20s linear infinite;
	}
	
	@keyframes rotate {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
	
	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24px;
		padding-bottom: 16px;
		border-bottom: 1px solid rgba(245, 158, 11, 0.2);
		position: relative;
		z-index: 1;
	}
	
	.header-left {
		display: flex;
		align-items: center;
		gap: 12px;
	}
	
	.live-badge {
		display: flex;
		align-items: center;
		gap: 6px;
		background: rgba(239, 68, 68, 0.2);
		border: 1px solid #ef4444;
		padding: 4px 12px;
		border-radius: 20px;
		font-size: 11px;
		font-weight: 700;
		color: #ef4444;
		text-transform: uppercase;
		letter-spacing: 1px;
	}
	
	.pulse-dot {
		width: 6px;
		height: 6px;
		background: #ef4444;
		border-radius: 50%;
		animation: pulse 2s ease-in-out infinite;
	}
	
	@keyframes pulse {
		0%, 100% {
			opacity: 1;
			transform: scale(1);
		}
		50% {
			opacity: 0.5;
			transform: scale(1.3);
		}
	}
	
	.card-header h2 {
		margin: 0;
		font-size: 18px;
		font-weight: 700;
		color: #f59e0b;
		text-transform: uppercase;
		letter-spacing: 1px;
	}
	
	.timestamp {
		font-size: 12px;
		color: #94a3b8;
		font-family: 'Courier New', monospace;
	}
	
	.price-section {
		text-align: center;
		padding: 20px 0;
		position: relative;
		z-index: 1;
	}
	
	.symbol {
		font-size: 16px;
		font-weight: 600;
		color: #f59e0b;
		text-transform: uppercase;
		letter-spacing: 2px;
		margin-bottom: 12px;
	}
	
	.price-main {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 16px;
	}
	
	.price {
		font-size: 48px;
		font-weight: 700;
		color: #fff;
		font-family: 'Courier New', monospace;
		text-shadow: 0 0 30px rgba(245, 158, 11, 0.5);
	}
	
	.change {
		font-size: 24px;
		font-weight: 700;
		padding: 8px 16px;
		border-radius: 12px;
		font-family: 'Courier New', monospace;
	}
	
	.change.positive {
		background: rgba(16, 185, 129, 0.2);
		color: #10b981;
		border: 1px solid #10b981;
	}
	
	.change.negative {
		background: rgba(239, 68, 68, 0.2);
		color: #ef4444;
		border: 1px solid #ef4444;
	}
	
	.chart-section {
		margin: 24px 0;
		position: relative;
		z-index: 1;
	}
	
	.chart-title {
		font-size: 14px;
		font-weight: 600;
		color: #94a3b8;
		text-transform: uppercase;
		letter-spacing: 1px;
		margin-bottom: 12px;
	}
	
	.metrics-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 16px;
		margin: 24px 0;
		position: relative;
		z-index: 1;
	}
	
	.metric {
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(245, 158, 11, 0.2);
		border-radius: 12px;
		padding: 16px;
		text-align: center;
		transition: all 0.3s ease;
		backdrop-filter: blur(10px);
	}
	
	.metric:hover {
		transform: translateY(-4px);
		box-shadow: 0 8px 24px rgba(245, 158, 11, 0.3);
		border-color: #f59e0b;
	}
	
	.metric-label {
		font-size: 11px;
		color: #94a3b8;
		text-transform: uppercase;
		letter-spacing: 1px;
		margin-bottom: 8px;
	}
	
	.metric-value {
		font-size: 20px;
		font-weight: 700;
		color: #fff;
		font-family: 'Courier New', monospace;
	}
	
	/* Responsive */
	@media (max-width: 768px) {
		.binance-d3-card {
			padding: 16px;
		}
		
		.price {
			font-size: 36px;
		}
		
		.change {
			font-size: 18px;
		}
		
		.metrics-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}
	
	/* D3 chart styling */
	:global(.binance-d3-card svg) {
		overflow: visible;
	}
	
	:global(.binance-d3-card .grid line) {
		stroke: #475569;
	}
	
	:global(.binance-d3-card .domain) {
		stroke: #475569;
	}
	
	:global(.binance-d3-card text) {
		fill: #94a3b8;
		font-size: 11px;
	}
</style>
