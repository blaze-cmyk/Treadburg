<!--
	Test Page for Chart Capture Feature
	
	This page includes a TradingView chart and the chat interface
	to test the chart capture functionality
-->

<script lang="ts">
	import TradingViewWidget from '$lib/components/TradingViewWidget.svelte';
	import ChartCaptureButton from '$lib/components/ChartCaptureButton.svelte';
	
	let capturedImage: File | null = null;
	let capturedImageUrl: string | null = null;
	
	function handleChartCapture(event: CustomEvent<{ file: File; metadata: any }>) {
		const { file } = event.detail;
		capturedImage = file;
		
		// Create preview URL
		if (capturedImageUrl) {
			URL.revokeObjectURL(capturedImageUrl);
		}
		capturedImageUrl = URL.createObjectURL(file);
		
		console.log('Chart captured successfully:', file);
	}
	
	function handleCaptureError(event: CustomEvent<{ message: string }>) {
		console.error('Capture failed:', event.detail.message);
	}
	
	function clearCapture() {
		if (capturedImageUrl) {
			URL.revokeObjectURL(capturedImageUrl);
		}
		capturedImage = null;
		capturedImageUrl = null;
	}
</script>

<svelte:head>
	<title>TradeBerg - Chart Capture Test</title>
</svelte:head>

<div class="min-h-screen bg-gray-900 text-white">
	<!-- Header -->
	<header class="bg-gray-800 border-b border-gray-700 p-4">
		<div class="max-w-6xl mx-auto flex items-center justify-between">
			<h1 class="text-xl font-bold">TradeBerg - Chart Capture Test</h1>
			<div class="flex items-center gap-4">
				<ChartCaptureButton
					on:capture={handleChartCapture}
					on:error={handleCaptureError}
					size="lg"
					variant="default"
				/>
				{#if capturedImage}
					<button
						on:click={clearCapture}
						class="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm transition-colors"
					>
						Clear Capture
					</button>
				{/if}
			</div>
		</div>
	</header>

	<div class="max-w-6xl mx-auto p-4">
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- TradingView Chart -->
			<div class="lg:col-span-2">
				<div class="bg-gray-800 rounded-lg p-4">
					<h2 class="text-lg font-semibold mb-4">TradingView Chart</h2>
					<TradingViewWidget 
						symbol="BINANCE:BTCUSDT"
						interval="15"
						theme="dark"
						height="500"
					/>
				</div>
			</div>

			<!-- Capture Preview -->
			<div class="lg:col-span-1">
				<div class="bg-gray-800 rounded-lg p-4">
					<h2 class="text-lg font-semibold mb-4">Captured Chart</h2>
					
					{#if capturedImageUrl}
						<div class="space-y-4">
							<img 
								src={capturedImageUrl} 
								alt="Captured chart" 
								class="w-full rounded border-2 border-green-500"
							/>
							<div class="text-sm text-gray-300">
								<p><strong>File:</strong> {capturedImage?.name}</p>
								<p><strong>Size:</strong> {Math.round((capturedImage?.size || 0) / 1024)} KB</p>
								<p><strong>Type:</strong> {capturedImage?.type}</p>
							</div>
						</div>
					{:else}
						<div class="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
							<div class="text-gray-400">
								<svg class="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
								</svg>
								<p>No chart captured yet</p>
								<p class="text-sm mt-2">Click the camera button or press Ctrl+Shift+S</p>
							</div>
						</div>
					{/if}
				</div>

				<!-- Instructions -->
				<div class="bg-gray-800 rounded-lg p-4 mt-4">
					<h3 class="font-semibold mb-2">How to Test:</h3>
					<ul class="text-sm text-gray-300 space-y-1">
						<li>1. Wait for chart to load</li>
						<li>2. Click camera button 📸</li>
						<li>3. Or press Ctrl+Shift+S</li>
						<li>4. Check captured image</li>
					</ul>
				</div>
			</div>
		</div>
	</div>
</div>
