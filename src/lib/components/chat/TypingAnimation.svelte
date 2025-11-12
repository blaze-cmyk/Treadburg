<script lang="ts">
	import { onMount } from 'svelte';
	
	export let text: string = '';
	export let speed: number = 20; // milliseconds per character
	export let showCursor: boolean = true;
	
	let displayedText = '';
	let isTyping = true;
	let currentIndex = 0;
	
	onMount(() => {
		if (!text) return;
		
		const typeNextChar = () => {
			if (currentIndex < text.length) {
				displayedText = text.substring(0, currentIndex + 1);
				currentIndex++;
				setTimeout(typeNextChar, speed);
			} else {
				isTyping = false;
			}
		};
		
		typeNextChar();
	});
</script>

<div class="typing-container">
	<span class="typed-text">{displayedText}</span>
	{#if isTyping && showCursor}
		<span class="typing-cursor">|</span>
	{/if}
</div>

<style>
	.typing-container {
		display: inline;
		position: relative;
	}
	
	.typed-text {
		white-space: pre-wrap;
		word-wrap: break-word;
	}
	
	.typing-cursor {
		display: inline-block;
		width: 2px;
		height: 1.2em;
		background-color: currentColor;
		margin-left: 2px;
		animation: blink 1s step-end infinite;
	}
	
	@keyframes blink {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0;
		}
	}
</style>
