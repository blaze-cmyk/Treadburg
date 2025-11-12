<!--
	TradeBerg Chart Capture Button Component
	
	Features:
	- Manual chart screenshot capture
	- Loading states and animations
	- Error handling with user feedback
	- Keyboard shortcut support (Ctrl+Shift+S)
	- Mobile responsive design
	- Integration with existing file upload system
-->

<script lang="ts">
	import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import { toast } from 'svelte-sonner';
	// @ts-ignore
	import html2canvas from 'html2canvas-pro';

	// Component props
	export let disabled = false;
	export let showTooltip = true;
	export let size: 'sm' | 'md' | 'lg' = 'md';
	export let variant: 'default' | 'ghost' | 'outline' = 'ghost';

	// Component state
	let isCapturing = false;
	let showSuccess = false;

	// Event dispatcher
	const dispatch = createEventDispatcher<{
		capture: { file: File; metadata: any };
		error: { message: string };
		start: void;
		complete: void;
	}>();

	// Size classes
	const sizeClasses = {
		sm: 'p-1.5 text-sm',
		md: 'p-2 text-base',
		lg: 'p-3 text-lg'
	};

	// Variant classes
	const variantClasses = {
		default: 'bg-gray-800 hover:bg-gray-700 border border-gray-600',
		ghost: 'hover:bg-gray-700/50 border border-transparent hover:border-gray-600',
		outline: 'border border-gray-600 hover:bg-gray-700/30'
	};

	// Reactive computed properties
	$: buttonClasses = [
		'relative rounded-lg transition-all duration-200 flex items-center justify-center',
		'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900',
		sizeClasses[size],
		variantClasses[variant],
		disabled || isCapturing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
		showSuccess ? 'ring-2 ring-green-500' : ''
	].join(' ');

	$: isDisabled = disabled || isCapturing;

	/**
	 * Find TradingView chart element
	 */
	function findChartElement(): HTMLElement | null {
		// Try to find TradingView chart container
		const selectors = [
			'iframe[src*="tradingview"]',
			'iframe[id*="tradingview"]',
			'.tradingview-widget-container',
			'[class*="chart-container"]',
			'[class*="tv-chart"]',
			'#tradingview_chart',
			'.chart-wrapper',
			'canvas[data-qa-widget-chart-canvas]'
		];

		for (const selector of selectors) {
			const element = document.querySelector(selector);
			if (element) {
				console.log('Found chart element:', selector);
				return element as HTMLElement;
			}
		}

		// Fallback to body
		console.log('No chart element found, using document body');
		return document.body;
	}

	/**
	 * Convert canvas to file
	 */
	async function canvasToFile(canvas: HTMLCanvasElement): Promise<File> {
		return new Promise((resolve, reject) => {
			canvas.toBlob(
				(blob) => {
					if (!blob) {
						reject(new Error('Failed to create blob from canvas'));
						return;
					}
					
					const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
					const file = new File([blob], `chart-${timestamp}.png`, {
						type: 'image/png',
						lastModified: Date.now()
					});
					
					resolve(file);
				},
				'image/png',
				0.95
			);
		});
	}

	/**
	 * Capture chart screenshot
	 */
	async function handleCapture() {
		if (isDisabled) return;

		isCapturing = true;
		dispatch('start');

		try {
			toast.info('Capturing chart...', { duration: 2000 });

			// Find chart element
			const chartElement = findChartElement();
			if (!chartElement) {
				throw new Error('Could not find chart element');
			}

			// Capture with html2canvas
			const canvas = await html2canvas(chartElement, {
				backgroundColor: '#1a1a1a',
				scale: 2,
				logging: false,
				useCORS: true,
				allowTaint: true
			});

			// Convert to file
			const file = await canvasToFile(canvas);

			// Show success animation
			showSuccess = true;
			setTimeout(() => {
				showSuccess = false;
			}, 300);

			// Dispatch capture event
			dispatch('capture', {
				file: file,
				metadata: {
					width: canvas.width,
					height: canvas.height,
					format: 'png',
					size: file.size,
					timestamp: Date.now()
				}
			});

			toast.success('Chart captured! Click send to analyze.');
		} catch (error) {
			const errorMessage = error instanceof Error ? error.message : 'Failed to capture chart';
			console.error('Chart capture error:', error);
			dispatch('error', { message: errorMessage });
			toast.error(errorMessage);
		} finally {
			isCapturing = false;
			dispatch('complete');
		}
	}

	/**
	 * Handle keyboard shortcut
	 */
	function handleKeyDown(event: KeyboardEvent) {
		if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'S') {
			event.preventDefault();
			handleCapture();
		}
	}

	/**
	 * Setup keyboard listener on mount
	 */
	onMount(() => {
		// Add keyboard listener
		window.addEventListener('keydown', handleKeyDown);
	});

	/**
	 * Cleanup on destroy
	 */
	onDestroy(() => {
		window.removeEventListener('keydown', handleKeyDown);
	});
</script>

<!-- Chart Capture Button -->
<div class="relative">
	<button
		class={buttonClasses}
		on:click={handleCapture}
		disabled={isDisabled}
		title={showTooltip ? 'Capture current chart (Ctrl+Shift+S)' : undefined}
		aria-label="Capture chart screenshot"
	>
		<!-- Button Content -->
		<div class="relative flex items-center justify-center">
			{#if isCapturing}
				<!-- Loading Spinner -->
				<svg 
					class="animate-spin h-5 w-5 text-blue-400" 
					xmlns="http://www.w3.org/2000/svg" 
					fill="none" 
					viewBox="0 0 24 24"
				>
					<circle 
						class="opacity-25" 
						cx="12" 
						cy="12" 
						r="10" 
						stroke="currentColor" 
						stroke-width="4"
					></circle>
					<path 
						class="opacity-75" 
						fill="currentColor" 
						d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
					></path>
				</svg>
			{:else if showSuccess}
				<!-- Success Checkmark -->
				<svg 
					class="h-5 w-5 text-green-400" 
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
			{:else}
				<!-- Camera Icon -->
				<svg 
					class="h-5 w-5 {isDisabled ? 'text-gray-500' : 'text-gray-300'}" 
					xmlns="http://www.w3.org/2000/svg" 
					fill="none" 
					viewBox="0 0 24 24" 
					stroke="currentColor"
				>
					<path 
						stroke-linecap="round" 
						stroke-linejoin="round" 
						stroke-width="2" 
						d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
					></path>
					<path 
						stroke-linecap="round" 
						stroke-linejoin="round" 
						stroke-width="2" 
						d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
					></path>
				</svg>
			{/if}
		</div>

		<!-- Success Ring Animation -->
		{#if showSuccess}
			<div class="absolute inset-0 rounded-lg border-2 border-green-400 animate-ping"></div>
		{/if}
	</button>

	<!-- Tooltip (if enabled and not on mobile) -->
	{#if showTooltip && !isDisabled}
		<div 
			class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-800 rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50 hidden md:block"
		>
			Capture chart (Ctrl+Shift+S)
			<div class="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
		</div>
	{/if}
</div>


<style>
	/* Custom animations */
	@keyframes ping {
		75%, 100% {
			transform: scale(2);
			opacity: 0;
		}
	}
	
	.animate-ping {
		animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
	}
</style>
