<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';

	export let data: Array<{ label: string; value: number; color?: string }> = [];
	export let title: string = 'Financial Data';
	export let height: number = 400;
	export let showValues: boolean = true;

	let container: HTMLDivElement;

	onMount(() => {
		if (!data || data.length === 0) return;
		renderChart();
	});

	$: if (data && container) {
		renderChart();
	}

	function renderChart() {
		// Clear previous chart
		d3.select(container).selectAll('*').remove();

		const margin = { top: 40, right: 30, bottom: 60, left: 60 };
		const width = container.clientWidth - margin.left - margin.right;
		const chartHeight = height - margin.top - margin.bottom;

		// Create SVG
		const svg = d3
			.select(container)
			.append('svg')
			.attr('width', width + margin.left + margin.right)
			.attr('height', height)
			.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);

		// Create scales
		const x = d3
			.scaleBand()
			.range([0, width])
			.domain(data.map((d) => d.label))
			.padding(0.2);

		const y = d3
			.scaleLinear()
			.domain([0, d3.max(data, (d) => d.value) || 0])
			.nice()
			.range([chartHeight, 0]);

		// Add X axis
		svg
			.append('g')
			.attr('transform', `translate(0,${chartHeight})`)
			.call(d3.axisBottom(x))
			.selectAll('text')
			.attr('transform', 'rotate(-45)')
			.style('text-anchor', 'end')
			.style('fill', 'currentColor');

		// Add Y axis
		svg.append('g').call(d3.axisLeft(y)).style('color', 'currentColor');

		// Add bars
		svg
			.selectAll('rect')
			.data(data)
			.enter()
			.append('rect')
			.attr('x', (d) => x(d.label) || 0)
			.attr('y', (d) => y(d.value))
			.attr('width', x.bandwidth())
			.attr('height', (d) => chartHeight - y(d.value))
			.attr('fill', (d) => d.color || '#667eea')
			.attr('rx', 4)
			.on('mouseover', function (event, d) {
				d3.select(this).attr('opacity', 0.8);
			})
			.on('mouseout', function (event, d) {
				d3.select(this).attr('opacity', 1);
			});

		// Add values on top of bars
		if (showValues) {
			svg
				.selectAll('.value-label')
				.data(data)
				.enter()
				.append('text')
				.attr('class', 'value-label')
				.attr('x', (d) => (x(d.label) || 0) + x.bandwidth() / 2)
				.attr('y', (d) => y(d.value) - 5)
				.attr('text-anchor', 'middle')
				.style('fill', 'currentColor')
				.style('font-size', '12px')
				.text((d) => d.value.toFixed(2));
		}

		// Add title
		svg
			.append('text')
			.attr('x', width / 2)
			.attr('y', -10)
			.attr('text-anchor', 'middle')
			.style('font-size', '16px')
	}
</script>

<div class="financial-bar-chart glass-chart" bind:this={container}>
	<div class="chart-header">
		{#if title}
			<h3 class="chart-title">
				<span class="icon">📊</span>
				{title}
			</h3>
		{/if}
		<div class="chart-badge">Live</div>
	</div>
</div>

<style>
	.financial-bar-chart {
		width: 100%;
		padding: 24px;
		background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
		border-radius: 16px;
		margin: 16px 0;
		border: 1px solid rgba(255, 255, 255, 0.1);
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
		position: relative;
		overflow: hidden;
	}
	
	.financial-bar-chart::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 2px;
		background: linear-gradient(90deg, #10b981, #3b82f6, #8b5cf6);
		background-size: 200% 100%;
		animation: shimmer 3s linear infinite;
	}
	
	@keyframes shimmer {
		0% { background-position: -200% 0; }
		100% { background-position: 200% 0; }
	}
	
	.chart-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20px;
	}

	.chart-title {
		font-size: 18px;
		font-weight: 600;
		color: #fff;
		margin: 0;
		display: flex;
		align-items: center;
		gap: 10px;
	}
	
	.chart-title .icon {
		font-size: 22px;
	}
	
	.chart-badge {
		padding: 4px 12px;
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
		font-size: 11px;
		font-weight: 600;
		border-radius: 12px;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
		animation: pulse 2s ease-in-out infinite;
	}
	
	@keyframes pulse {
		0%, 100% {
			box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
		}
		50% {
			box-shadow: 0 2px 16px rgba(16, 185, 129, 0.6);
		}
	}
</style>
