<!--
	TradeBerg Image Preview Component
	
	Shows captured chart screenshots with remove functionality
	Used in chat input area before sending message
-->

<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	// Component props
	export let file: File;
	export let metadata: any = null;
	export let removable = true;
	export let maxHeight = 100;

	// Component state
	let imageUrl = '';
	let imageElement: HTMLImageElement;
	let isLoading = true;
	let hasError = false;

	// Event dispatcher
	const dispatch = createEventDispatcher<{
		remove: void;
		load: void;
		error: void;
	}>();

	// Create object URL for preview
	$: if (file) {
		// Clean up previous URL
		if (imageUrl) {
			URL.revokeObjectURL(imageUrl);
		}
		
		// Create new URL
		imageUrl = URL.createObjectURL(file);
		isLoading = true;
		hasError = false;
	}

	// Format file size
	function formatFileSize(bytes: number): string {
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	}

	// Handle image load
	function handleImageLoad() {
		isLoading = false;
		dispatch('load');
	}

	// Handle image error
	function handleImageError() {
		isLoading = false;
		hasError = true;
		dispatch('error');
	}

	// Handle remove
	function handleRemove() {
		if (imageUrl) {
			URL.revokeObjectURL(imageUrl);
		}
		dispatch('remove');
	}

	// Cleanup on destroy
	function cleanup() {
		if (imageUrl) {
			URL.revokeObjectURL(imageUrl);
		}
	}
</script>

<svelte:window on:beforeunload={cleanup} />

<!-- Image Preview Container -->
<div 
	class="relative inline-block bg-gray-800 border-2 border-blue-500 rounded-lg shadow-lg overflow-hidden"
	style="max-height: {maxHeight}px;"
>
	<!-- Loading State -->
	{#if isLoading}
		<div 
			class="flex items-center justify-center bg-gray-700 animate-pulse"
			style="width: 150px; height: {maxHeight}px;"
		>
			<svg 
				class="w-8 h-8 text-gray-400" 
				xmlns="http://www.w3.org/2000/svg" 
				fill="none" 
				viewBox="0 0 24 24" 
				stroke="currentColor"
			>
				<path 
					stroke-linecap="round" 
					stroke-linejoin="round" 
					stroke-width="2" 
					d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
				></path>
			</svg>
		</div>
	{/if}

	<!-- Error State -->
	{#if hasError}
		<div 
			class="flex flex-col items-center justify-center bg-red-900/20 border-red-500 text-red-400 p-4"
			style="width: 150px; height: {maxHeight}px;"
		>
			<svg 
				class="w-6 h-6 mb-2" 
				xmlns="http://www.w3.org/2000/svg" 
				fill="none" 
				viewBox="0 0 24 24" 
				stroke="currentColor"
			>
				<path 
					stroke-linecap="round" 
					stroke-linejoin="round" 
					stroke-width="2" 
					d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
				></path>
			</svg>
			<span class="text-xs text-center">Failed to load</span>
		</div>
	{/if}

	<!-- Image -->
	{#if imageUrl && !hasError}
		<img
			bind:this={imageElement}
			src={imageUrl}
			alt="Chart screenshot preview"
			class="block max-w-none"
			style="max-height: {maxHeight}px; width: auto;"
			on:load={handleImageLoad}
			on:error={handleImageError}
		/>
	{/if}

	<!-- Remove Button -->
	{#if removable}
		<button
			class="absolute top-1 right-1 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors duration-200 shadow-lg"
			on:click={handleRemove}
			title="Remove image"
			aria-label="Remove image"
		>
			<svg 
				class="w-4 h-4" 
				xmlns="http://www.w3.org/2000/svg" 
				fill="none" 
				viewBox="0 0 24 24" 
				stroke="currentColor"
			>
				<path 
					stroke-linecap="round" 
					stroke-linejoin="round" 
					stroke-width="2" 
					d="M6 18L18 6M6 6l12 12"
				></path>
			</svg>
		</button>
	{/if}

	<!-- Metadata Overlay -->
	{#if metadata && !isLoading && !hasError}
		<div class="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-xs p-1 flex justify-between items-center">
			<span class="truncate">
				{formatFileSize(file.size)}
			</span>
			<span class="ml-2 opacity-75">
				{metadata.format?.toUpperCase() || 'IMG'}
			</span>
		</div>
	{/if}

	<!-- Capture Success Indicator -->
	<div class="absolute top-1 left-1">
		<div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
	</div>
</div>

<style>
	/* Ensure smooth animations */
	.animate-pulse {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}
	
	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: .5;
		}
	}
</style>
