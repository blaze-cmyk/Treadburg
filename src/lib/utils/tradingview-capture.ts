/**
 * TradingView-Style Chart Capture
 * 
 * Implements the same screenshot functionality as TradingView's native camera button
 * without requiring screen sharing permissions
 */

/**
 * Capture chart using TradingView's native screenshot API
 * This method doesn't require permissions like the built-in camera button
 */
export async function captureTradingViewChart(): Promise<{
	success: boolean;
	file?: File;
	error?: string;
}> {
	try {
		// Method 1: Try to use TradingView's built-in screenshot functionality
		const result = await tryTradingViewNativeCapture();
		if (result.success) {
			return result;
		}

		// Method 2: Try canvas-based capture of chart content
		const canvasResult = await tryCanvasCapture();
		if (canvasResult.success) {
			return canvasResult;
		}

		// Method 3: Fallback to element capture
		return await tryElementCapture();

	} catch (error) {
		console.error('TradingView capture failed:', error);
		return {
			success: false,
			error: error instanceof Error ? error.message : 'Capture failed'
		};
	}
}

/**
 * Try to use TradingView's native screenshot functionality
 */
async function tryTradingViewNativeCapture(): Promise<{
	success: boolean;
	file?: File;
	error?: string;
}> {
	try {
		// Look for TradingView's screenshot button and trigger it programmatically
		const screenshotButton = document.querySelector('[data-name="screenshot"], .tv-header__screenshot, .js-header__screenshot') as HTMLButtonElement;
		
		if (screenshotButton) {
			// Create a promise to capture the screenshot result
			return new Promise((resolve) => {
				// Listen for TradingView's screenshot events
				const handleScreenshot = (event: any) => {
					if (event.detail && event.detail.imageData) {
						// Convert TradingView's image data to File
						const canvas = document.createElement('canvas');
						const ctx = canvas.getContext('2d')!;
						const img = new Image();
						
						img.onload = () => {
							canvas.width = img.width;
							canvas.height = img.height;
							ctx.drawImage(img, 0, 0);
							
							canvas.toBlob((blob) => {
								if (blob) {
									const file = new File([blob], `chart-${Date.now()}.png`, { type: 'image/png' });
									resolve({ success: true, file });
								} else {
									resolve({ success: false, error: 'Failed to create image file' });
								}
							}, 'image/png');
						};
						
						img.src = event.detail.imageData;
					}
				};

				// Add event listener for TradingView screenshot
				document.addEventListener('tv-screenshot-ready', handleScreenshot, { once: true });
				
				// Trigger the screenshot
				screenshotButton.click();
				
				// Timeout after 3 seconds
				setTimeout(() => {
					document.removeEventListener('tv-screenshot-ready', handleScreenshot);
					resolve({ success: false, error: 'Screenshot timeout' });
				}, 3000);
			});
		}

		return { success: false, error: 'Screenshot button not found' };
	} catch (error) {
		return { success: false, error: 'Native capture failed' };
	}
}

/**
 * Try canvas-based capture of chart content
 */
async function tryCanvasCapture(): Promise<{
	success: boolean;
	file?: File;
	error?: string;
}> {
	try {
		// Find TradingView chart canvas elements
		const chartCanvases = document.querySelectorAll('canvas[data-name="candles"], canvas[data-name="pane"], .tv-lightweight-charts canvas, canvas') as NodeListOf<HTMLCanvasElement>;
		
		if (chartCanvases.length === 0) {
			return { success: false, error: 'No chart canvas found' };
		}

		// Find the main chart canvas (usually the largest one)
		let mainCanvas: HTMLCanvasElement | null = null;
		let maxArea = 0;

		chartCanvases.forEach(canvas => {
			const area = canvas.width * canvas.height;
			if (area > maxArea) {
				maxArea = area;
				mainCanvas = canvas;
			}
		});

		if (!mainCanvas) {
			return { success: false, error: 'No suitable canvas found' };
		}

		// Create a new canvas to combine all chart elements
		const combinedCanvas = document.createElement('canvas');
		const ctx = combinedCanvas.getContext('2d')!;

		// Set canvas size to match the chart container
		const chartContainer = mainCanvas.closest('.tv-lightweight-charts, .chart-container, [class*="chart"]') as HTMLElement;
		const rect = chartContainer ? chartContainer.getBoundingClientRect() : mainCanvas.getBoundingClientRect();

		combinedCanvas.width = rect.width;
		combinedCanvas.height = rect.height;

		// Fill with dark background (TradingView style)
		ctx.fillStyle = '#1e1e1e';
		ctx.fillRect(0, 0, combinedCanvas.width, combinedCanvas.height);

		// Draw all relevant canvases
		chartCanvases.forEach(canvas => {
			if (canvas.width > 0 && canvas.height > 0) {
				try {
					const canvasRect = canvas.getBoundingClientRect();
					const x = canvasRect.left - rect.left;
					const y = canvasRect.top - rect.top;
					ctx.drawImage(canvas, x, y);
				} catch (e) {
					// Skip canvases that can't be drawn (CORS issues)
				}
			}
		});

		// Convert to blob
		const blob = await new Promise<Blob>((resolve) => {
			combinedCanvas.toBlob((blob) => {
				resolve(blob!);
			}, 'image/png');
		});

		const file = new File([blob], `tradingview-chart-${Date.now()}.png`, { type: 'image/png' });
		return { success: true, file };

	} catch (error) {
		return { success: false, error: 'Canvas capture failed' };
	}
}

/**
 * Try element-based capture as fallback
 */
async function tryElementCapture(): Promise<{
	success: boolean;
	file?: File;
	error?: string;
}> {
	try {
		// Import html2canvas dynamically
		const html2canvas = (await import('html2canvas-pro')).default;

		// Find the chart container
		const chartElement = document.querySelector('.tv-lightweight-charts, .chart-container, [class*="chart-widget"], [id*="tradingview"]') as HTMLElement;
		
		if (!chartElement) {
			return { success: false, error: 'Chart element not found' };
		}

		// Capture with html2canvas
		const canvas = await html2canvas(chartElement, {
			backgroundColor: '#1e1e1e',
			scale: 1,
			useCORS: true,
			allowTaint: false,
			foreignObjectRendering: true,
			logging: false
		});

		// Convert to blob
		const blob = await new Promise<Blob>((resolve) => {
			canvas.toBlob((blob) => {
				resolve(blob!);
			}, 'image/png');
		});

		const file = new File([blob], `chart-fallback-${Date.now()}.png`, { type: 'image/png' });
		return { success: true, file };

	} catch (error) {
		return { success: false, error: 'Element capture failed' };
	}
}

/**
 * Find and click TradingView's native screenshot button
 */
export function clickTradingViewScreenshot(): boolean {
	try {
		// Multiple selectors for TradingView's screenshot button
		const selectors = [
			'[data-name="screenshot"]',
			'.tv-header__screenshot',
			'.js-header__screenshot',
			'[title*="screenshot" i]',
			'[aria-label*="screenshot" i]',
			'button[class*="screenshot"]',
			'.tv-toolbar__button[data-tooltip*="screenshot" i]'
		];

		for (const selector of selectors) {
			const button = document.querySelector(selector) as HTMLButtonElement;
			if (button && button.offsetParent !== null) { // Check if visible
				button.click();
				return true;
			}
		}

		return false;
	} catch (error) {
		console.error('Failed to click TradingView screenshot button:', error);
		return false;
	}
}

/**
 * Check if TradingView's native screenshot is available
 */
export function isTradingViewScreenshotAvailable(): boolean {
	const selectors = [
		'[data-name="screenshot"]',
		'.tv-header__screenshot',
		'.js-header__screenshot'
	];

	return selectors.some(selector => {
		const button = document.querySelector(selector);
		return button && button.offsetParent !== null;
	});
}
