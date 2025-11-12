<script lang="ts">
	import { marked } from 'marked';
	import FinancialBarChart from '$lib/components/charts/FinancialBarChart.svelte';
	import CandlestickChart from '$lib/components/charts/CandlestickChart.svelte';
	import SimpleDataGrid from '$lib/components/charts/SimpleDataGrid.svelte';
	import AnimatedFinancialCards from './AnimatedFinancialCards.svelte';

	export let content: string = '';

	interface ParsedContent {
		text: string;
		charts: Array<{
			type: 'bar' | 'candlestick' | 'grid' | 'animated';
			data: any;
			title: string;
			annotations?: any[];
		}>;
	}

	let parsedContent: ParsedContent = { text: '', charts: [] };

	$: {
		parsedContent = parseFinancialContent(content);
	}

	function parseFinancialContent(content: string): ParsedContent {
		const result: ParsedContent = { text: content, charts: [] };

		// Parse JSON data blocks for charts (including animated cards)
		const jsonBlockRegex = /```json:(chart:|animated:)?(\w+)\n([\s\S]*?)```/g;
		let match;

		while ((match = jsonBlockRegex.exec(content)) !== null) {
			const prefix = match[1] || 'chart:';
			const chartType = match[2];
			const jsonData = match[3];

			try {
				const data = JSON.parse(jsonData);
				result.charts.push({
					type: chartType as any,
					data: data.data || data,
					title: data.title || 'Financial Chart',
					annotations: data.annotations
				});

				// Remove the JSON block from text
				result.text = result.text.replace(match[0], '');
			} catch (e) {
				console.error('Failed to parse chart data:', e);
			}
		}

		// Parse inline chart commands
		const chartCommandRegex = /\[CHART:(\w+):([^\]]+)\]/g;
		result.text = result.text.replace(chartCommandRegex, (match, type, title) => {
			return `<div class="chart-placeholder">${type} Chart: ${title}</div>`;
		});

		return result;
	}

	function renderMarkdown(text: string): string {
		return marked(text);
	}
</script>

<div class="financial-analysis-container space-y-6">
	<!-- Render text content -->
	{#if parsedContent.text.trim()}
		<div class="prose dark:prose-invert max-w-none">
			{@html renderMarkdown(parsedContent.text)}
		</div>
	{/if}

	<!-- Render charts -->
	{#each parsedContent.charts as chart, i}
		{#if chart.type === 'cards'}
			<!-- Animated cards don't need container wrapper -->
			<AnimatedFinancialCards data={chart.data} />
		{:else}
			<div class="chart-container">
				{#if chart.type === 'bar'}
					<FinancialBarChart data={chart.data} title={chart.title} />
				{:else if chart.type === 'candlestick'}
					<CandlestickChart
						data={chart.data}
						title={chart.title}
						annotations={chart.annotations || []}
					/>
				{:else if chart.type === 'grid'}
					<SimpleDataGrid rowData={chart.data} title={chart.title} />
				{/if}
			</div>
		{/if}
	{/each}
</div>

<style>
	.financial-analysis-container {
		padding: 1rem;
	}

	.chart-container {
		background: rgba(255, 255, 255, 0.03);
		backdrop-filter: blur(10px);
		border-radius: 12px;
		padding: 20px;
		border: 1px solid rgba(255, 255, 255, 0.1);
		margin: 1rem 0;
	}

	:global(.dark) .chart-container {
		background: rgba(0, 0, 0, 0.2);
	}

	.chart-placeholder {
		padding: 2rem;
		background: rgba(99, 102, 241, 0.1);
		border: 2px dashed rgba(99, 102, 241, 0.3);
		border-radius: 8px;
		text-align: center;
		color: #6366f1;
		font-weight: 600;
	}

	:global(.prose) {
		color: inherit;
	}

	:global(.prose h1),
	:global(.prose h2),
	:global(.prose h3) {
		color: inherit;
		font-weight: 700;
	}

	:global(.prose code) {
		background: rgba(99, 102, 241, 0.1);
		padding: 0.2em 0.4em;
		border-radius: 4px;
		font-size: 0.9em;
	}

	:global(.prose pre) {
		background: rgba(0, 0, 0, 0.3);
		border-radius: 8px;
		padding: 1rem;
	}

	:global(.prose table) {
		width: 100%;
		border-collapse: collapse;
		margin: 1rem 0;
	}

	:global(.prose th),
	:global(.prose td) {
		border: 1px solid rgba(255, 255, 255, 0.1);
		padding: 0.75rem;
		text-align: left;
	}

	:global(.prose th) {
		background: rgba(99, 102, 241, 0.1);
		font-weight: 600;
	}

	:global(.prose tr:nth-child(even)) {
		background: rgba(255, 255, 255, 0.02);
	}
</style>
