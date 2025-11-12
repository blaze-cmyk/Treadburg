<script lang="ts">
	import { onMount } from 'svelte';
	import Plotly from 'plotly.js-dist-min';

	export let data: Array<{
		date: string;
		open: number;
		high: number;
		low: number;
		close: number;
		volume?: number;
	}> = [];
	export let title: string = 'Price Action';
	export let annotations: Array<{
		x: string;
		y: number;
		text: string;
		type: 'entry' | 'exit' | 'stop';
	}> = [];

	let container: HTMLDivElement;

	onMount(() => {
		if (data && data.length > 0) {
			renderChart();
		}
	});

	$: if (data && container) {
		renderChart();
	}

	function renderChart() {
		const trace = {
			x: data.map((d) => d.date),
			close: data.map((d) => d.close),
			high: data.map((d) => d.high),
			low: data.map((d) => d.low),
			open: data.map((d) => d.open),
			type: 'candlestick',
			name: 'Price',
			increasing: { line: { color: '#10b981' } },
			decreasing: { line: { color: '#ef4444' } }
		};

		const volumeTrace = data[0]?.volume
			? {
					x: data.map((d) => d.date),
					y: data.map((d) => d.volume || 0),
					type: 'bar',
					name: 'Volume',
					yaxis: 'y2',
					marker: {
						color: data.map((d) => (d.close > d.open ? '#10b98180' : '#ef444480'))
					}
			  }
			: null;

		const plotAnnotations = annotations.map((ann) => ({
			x: ann.x,
			y: ann.y,
			text: ann.text,
			showarrow: true,
			arrowhead: 2,
			arrowcolor:
				ann.type === 'entry' ? '#10b981' : ann.type === 'exit' ? '#3b82f6' : '#ef4444',
			ax: 0,
			ay: ann.type === 'entry' ? 40 : -40,
			font: { color: 'white', size: 12 },
			bgcolor:
				ann.type === 'entry' ? '#10b981' : ann.type === 'exit' ? '#3b82f6' : '#ef4444',
			borderpad: 4
		}));

		const layout = {
			title: {
				text: title,
				font: { color: 'currentColor' }
			},
			xaxis: {
				rangeslider: { visible: false },
				color: 'currentColor'
			},
			yaxis: {
				title: 'Price',
				color: 'currentColor'
			},
			yaxis2: data[0]?.volume
				? {
						title: 'Volume',
						overlaying: 'y',
						side: 'right',
						color: 'currentColor'
				  }
				: undefined,
			annotations: plotAnnotations,
			paper_bgcolor: 'transparent',
			plot_bgcolor: 'transparent',
			font: { color: 'currentColor' },
			margin: { t: 50, b: 50, l: 60, r: 60 }
		};

		const config = {
			responsive: true,
			displayModeBar: true,
			displaylogo: false
		};

		const traces = volumeTrace ? [trace, volumeTrace] : [trace];

		Plotly.newPlot(container, traces, layout, config);
	}
</script>

<div bind:this={container} class="w-full h-[500px]"></div>
