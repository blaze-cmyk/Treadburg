<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		// Redirect to the TradeBerg enhanced chat
		goto('/tradeberg-chat');
	});
</script>

<svelte:head>
	<title>TradeBerg - Redirecting...</title>
</svelte:head>

<div class="redirect-container">
	<h1>🚀 Redirecting to TradeBerg Enhanced Chat...</h1>
	<p>If you're not redirected, <a href="/tradeberg-chat">click here</a>.</p>
</div>

<style>
	.redirect-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 50vh;
		text-align: center;
		padding: 2rem;
	}
	
	h1 {
		color: #00ff88;
		margin-bottom: 1rem;
	}
	
	a {
		color: #00ff88;
		text-decoration: none;
	}
	
	a:hover {
		text-decoration: underline;
	}
</style>
