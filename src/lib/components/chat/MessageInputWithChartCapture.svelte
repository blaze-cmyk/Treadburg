<!--
	TradeBerg Enhanced MessageInput with Chart Capture
	
	This is the modified MessageInput component that includes:
	- Chart capture button integration
	- Image preview functionality
	- All original MessageInput features
	
	Usage: Replace the original MessageInput import with this component
-->

<script lang="ts">
	// Import the original MessageInput component
	import MessageInput from './MessageInput.svelte';
	
	// Import our new components
	import ChartCaptureButton from '../ChartCaptureButton.svelte';
	import ImagePreview from '../ImagePreview.svelte';
	
	import { createEventDispatcher } from 'svelte';
	import { toast } from 'svelte-sonner';
	
	// Re-export all props from MessageInput
	export let onChange: Function = () => {};
	export let createMessagePair: Function;
	export let stopResponse: Function;
	export let autoScroll = false;
	export let generating = false;
	export let atSelectedModel = undefined;
	export let selectedModels = [''];
	export let history;
	export let taskIds = null;
	export let prompt = '';
	export let files = [];
	export let selectedToolIds = [];
	export let selectedFilterIds = [];
	export let imageGenerationEnabled = false;
	export let webSearchEnabled = false;
	export let codeInterpreterEnabled = false;
	
	// Chart capture state
	let capturedImage: File | null = null;
	let capturedImageMetadata: any = null;
	let showImagePreview = false;
	
	const dispatch = createEventDispatcher();
	
	/**
	 * Handle successful chart capture
	 */
	function handleChartCapture(event: CustomEvent<{ file: File; metadata: any }>) {
		const { file, metadata } = event.detail;
		
		// Store captured image
		capturedImage = file;
		capturedImageMetadata = metadata;
		showImagePreview = true;
		
		// Add to files array for sending with message
		files = [
			...files,
			{
				type: 'image',
				url: URL.createObjectURL(file),
				name: file.name,
				size: file.size,
				file: file
			}
		];
		
		console.log('Chart captured:', { file, metadata });
	}
	
	/**
	 * Handle chart capture error
	 */
	function handleChartCaptureError(event: CustomEvent<{ message: string }>) {
		const { message } = event.detail;
		console.error('Chart capture error:', message);
		// Error toast is already shown by the ChartCaptureButton component
	}
	
	/**
	 * Handle image preview removal
	 */
	function handleImageRemove() {
		if (capturedImage) {
			// Remove from files array
			files = files.filter(file => 
				!(file.type === 'image' && file.name === capturedImage?.name)
			);
			
			// Clean up object URL
			const imageFile = files.find(f => f.file === capturedImage);
			if (imageFile?.url) {
				URL.revokeObjectURL(imageFile.url);
			}
			
			// Reset state
			capturedImage = null;
			capturedImageMetadata = null;
			showImagePreview = false;
		}
	}
	
	/**
	 * Enhanced onChange handler that includes chart capture state
	 */
	function handleChange(event: CustomEvent) {
		// Call original onChange with enhanced data
		onChange({
			...event.detail,
			files,
			capturedImage,
			capturedImageMetadata
		});
	}
</script>

<!-- Main Container -->
<div class="relative">
	<!-- Image Preview (if chart captured) -->
	{#if showImagePreview && capturedImage}
		<div class="mb-3 px-4">
			<div class="flex items-center gap-2 mb-2">
				<svg 
					class="w-4 h-4 text-green-400" 
					xmlns="http://www.w3.org/2000/svg" 
					fill="none" 
					viewBox="0 0 24 24" 
					stroke="currentColor"
				>
					<path 
						stroke-linecap="round" 
						stroke-linejoin="round" 
						stroke-width="2" 
						d="M5 13l4 4L19 7"
					></path>
				</svg>
				<span class="text-sm text-gray-300">Chart captured - ready to send</span>
			</div>
			
			<ImagePreview 
				file={capturedImage}
				metadata={capturedImageMetadata}
				on:remove={handleImageRemove}
				maxHeight={120}
			/>
		</div>
	{/if}
	
	<!-- Enhanced MessageInput with Chart Capture Button -->
	<div class="relative">
		<!-- Original MessageInput Component -->
		<MessageInput
			{onChange}
			{createMessagePair}
			{stopResponse}
			{autoScroll}
			{generating}
			{atSelectedModel}
			{selectedModels}
			{history}
			{taskIds}
			bind:prompt
			bind:files
			bind:selectedToolIds
			bind:selectedFilterIds
			bind:imageGenerationEnabled
			bind:webSearchEnabled
			bind:codeInterpreterEnabled
			on:change={handleChange}
		/>
		
		<!-- Chart Capture Button Overlay -->
		<div class="absolute bottom-4 right-16 z-10">
			<ChartCaptureButton
				on:capture={handleChartCapture}
				on:error={handleChartCaptureError}
				disabled={generating}
				size="md"
				variant="ghost"
			/>
		</div>
	</div>
</div>

<style>
	/* Ensure proper layering */
	:global(.chart-capture-overlay) {
		z-index: 50;
	}
	
	/* Smooth transitions for image preview */
	.image-preview-enter {
		opacity: 0;
		transform: translateY(-10px);
	}
	
	.image-preview-enter-active {
		opacity: 1;
		transform: translateY(0);
		transition: opacity 300ms ease, transform 300ms ease;
	}
</style>
