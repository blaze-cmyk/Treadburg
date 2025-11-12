<script lang="ts">
	import PerplexityChat from '$lib/components/PerplexityChat.svelte';
</script>

<svelte:head>
	<title>Perplexity Trading Bot - TradeBerg</title>
	<meta name="description" content="AI-powered trading analysis with Perplexity" />
</svelte:head>

<main class="perplexity-page">
	<PerplexityChat />
</main>

<style>
	.perplexity-page {
		min-height: 100vh;
		background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #581c87 100%);
		padding: 0;
		margin: 0;
	}

	:global(body) {
		margin: 0;
		padding: 0;
	}
</style>
