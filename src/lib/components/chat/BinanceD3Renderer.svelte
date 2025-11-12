<script lang="ts">
	import { onMount } from 'svelte';
	import BinanceD3Card from '$lib/components/charts/BinanceD3Card.svelte';
	
	export let content: string;
	
	let marketData: any = null;
	let hasData = false;
	
	onMount(() => {
		parseContent();
	});
	
	function parseContent() {
		// Look for binance-d3-data code blocks
		const regex = /```binance-d3-data\n([\s\S]*?)```/g;
		const match = regex.exec(content);
		
		if (match && match[1]) {
			try {
				marketData = JSON.parse(match[1]);
				hasData = true;
			} catch (e) {
				console.error('Failed to parse Binance data:', e);
			}
		}
	}
	
	$: if (content) {
		parseContent();
	}
</script>

{#if hasData && marketData}
	<BinanceD3Card {marketData} />
{/if}
