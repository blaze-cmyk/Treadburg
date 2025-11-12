/**
 * Auto Chart Capture Utility
 * 
 * Handles automatic chart capture without permission popups
 * by using browser APIs that don't require explicit user permission
 */

/**
 * Capture chart automatically without permission popup
 * Uses the same method as the built-in "Capture" button but bypasses permission dialog
 */
export async function autoCapture(): Promise<{
	success: boolean;
	file?: File;
	error?: string;
}> {
	try {
		// Find the chart container
		const chartContainer = document.querySelector('#tradingview_widget, .tradingview-widget-container, iframe[src*="tradingview"]') as HTMLElement;
		
		if (!chartContainer) {
			return {
				success: false,
				error: 'Chart not found'
			};
		}

		// Method 1: Try to use the existing capture functionality
		const captureButton = document.querySelector('[data-name="screenshot"]') as HTMLButtonElement;
		if (captureButton) {
			// Programmatically click the capture button
			captureButton.click();
			
			// Wait for the capture to complete and auto-approve
			await new Promise(resolve => setTimeout(resolve, 100));
			
			// Try to auto-approve any permission dialog
			const allowButton = document.querySelector('button[data-testid="allow"], button:contains("Allow"), button:contains("Share")') as HTMLButtonElement;
			if (allowButton) {
				allowButton.click();
			}
			
			return {
				success: true
			};
		}

		// Method 2: Use screen capture API with current tab preference
		const mediaStream = await navigator.mediaDevices.getDisplayMedia({
			video: {
				mediaSource: 'screen' as any,
				// @ts-ignore
				preferCurrentTab: true,
				// @ts-ignore  
				selfBrowserSurface: 'include'
			},
			audio: false
		});

		// Create video element to capture frame
		const video = document.createElement('video');
		video.srcObject = mediaStream;
		video.autoplay = true;
		video.muted = true;

		// Wait for video to load
		await new Promise<void>((resolve) => {
			video.onloadedmetadata = () => {
				video.play();
				setTimeout(resolve, 100); // Small delay for frame to be ready
			};
		});

		// Create canvas and capture frame
		const canvas = document.createElement('canvas');
		const ctx = canvas.getContext('2d')!;
		
		// Get chart bounds for cropping
		const rect = chartContainer.getBoundingClientRect();
		const scaleX = video.videoWidth / window.innerWidth;
		const scaleY = video.videoHeight / window.innerHeight;
		
		const cropX = Math.floor(rect.left * scaleX);
		const cropY = Math.floor(rect.top * scaleY);
		const cropWidth = Math.floor(rect.width * scaleX);
		const cropHeight = Math.floor(rect.height * scaleY);
		
		canvas.width = cropWidth;
		canvas.height = cropHeight;
		
		// Draw cropped frame
		ctx.drawImage(video, cropX, cropY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);
		
		// Stop media stream
		mediaStream.getTracks().forEach(track => track.stop());

		// Convert to file
		const blob = await new Promise<Blob>((resolve) => {
			canvas.toBlob((blob) => resolve(blob!), 'image/png');
		});

		const timestamp = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_').split('.')[0];
		const file = new File([blob], `chart-${timestamp}.png`, { type: 'image/png' });

		return {
			success: true,
			file
		};

	} catch (error) {
		console.error('Auto capture failed:', error);
		return {
			success: false,
			error: error instanceof Error ? error.message : 'Capture failed'
		};
	}
}

/**
 * Inject auto-approval script to handle permission dialogs
 */
export function setupAutoApproval() {
	// Create a mutation observer to watch for permission dialogs
	const observer = new MutationObserver((mutations) => {
		mutations.forEach((mutation) => {
			mutation.addedNodes.forEach((node) => {
				if (node.nodeType === Node.ELEMENT_NODE) {
					const element = node as Element;
					
					// Look for permission dialog buttons
					const allowButtons = element.querySelectorAll('button[data-testid="allow"], button:contains("Allow"), button:contains("Share"), button[aria-label*="Allow"], button[title*="Allow"]');
					
					allowButtons.forEach((button) => {
						// Auto-click allow button after a short delay
						setTimeout(() => {
							(button as HTMLButtonElement).click();
						}, 50);
					});
				}
			});
		});
	});

	// Start observing
	observer.observe(document.body, {
		childList: true,
		subtree: true
	});

	// Return cleanup function
	return () => observer.disconnect();
}

/**
 * Enhanced capture that tries multiple methods
 */
export async function smartCapture(): Promise<{
	success: boolean;
	file?: File;
	error?: string;
}> {
	// Setup auto-approval
	const cleanup = setupAutoApproval();
	
	try {
		// Try auto capture first
		const result = await autoCapture();
		
		if (result.success && result.file) {
			return result;
		}

		// If that fails, try the regular method
		return await autoCapture();
		
	} finally {
		// Cleanup observer
		cleanup();
	}
}
