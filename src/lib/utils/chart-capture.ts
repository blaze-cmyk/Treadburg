/**
 * TradeBerg Chart Capture Utility
 * 
 * Provides browser-side screenshot capture of TradingView charts using html2canvas-pro.
 * Features:
 * - High-quality chart screenshots (2x scale)
 * - Automatic compression for large images
 * - Comprehensive error handling
 * - TradingView iframe detection
 * - Mobile-responsive capture
 */

import html2canvas from 'html2canvas-pro';

/**
 * Chart capture configuration
 */
export interface ChartCaptureConfig {
	/** Background color for the screenshot */
	backgroundColor?: string;
	/** Scale factor for image quality (1-3) */
	scale?: number;
	/** Maximum file size in bytes (default: 2MB) */
	maxFileSize?: number;
	/** JPEG quality for compression (0.1-1.0) */
	compressionQuality?: number;
	/** Timeout in milliseconds */
	timeout?: number;
}

/**
 * Chart capture result
 */
export interface ChartCaptureResult {
	/** Success status */
	success: boolean;
	/** Generated file object (if successful) */
	file?: File;
	/** Error message (if failed) */
	error?: string;
	/** Capture metadata */
	metadata?: {
		width: number;
		height: number;
		fileSize: number;
		format: string;
		timestamp: string;
		compressed: boolean;
	};
}

/**
 * Default configuration for chart capture
 */
const DEFAULT_CONFIG: Required<ChartCaptureConfig> = {
	backgroundColor: '#1a1a1a', // TradeBerg dark theme
	scale: 2, // High quality
	maxFileSize: 2 * 1024 * 1024, // 2MB
	compressionQuality: 0.85, // Good quality/size balance
	timeout: 5000 // 5 seconds
};

/**
 * Check if an element is visible in the viewport
 * 
 * @param element Element to check
 * @returns True if element is visible
 */
function isElementVisible(element: HTMLElement): boolean {
	const rect = element.getBoundingClientRect();
	return (
		rect.top >= 0 &&
		rect.left >= 0 &&
		rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
		rect.right <= (window.innerWidth || document.documentElement.clientWidth)
	);
}

/**
 * Find TradingView chart element using multiple selectors
 */
function findTradingViewChart(): HTMLElement | null {
	// Priority order: most specific to least specific
	const selectors = [
		'iframe[src*="tradingview.com"]',    // TradingView iframe (highest priority)
		'iframe[src*="charting_library"]',   // TradingView charting library
		'.tradingview-widget-container iframe', // Widget container iframe
		'#tradingview_widget iframe',        // Standard widget iframe
		'[data-widget-type="chart"] iframe', // Chart widget iframe
		'.tv-embed-widget-wrapper iframe',   // Embed wrapper iframe
		'#tradeberg-chart iframe',           // TradeBerg chart iframe
		'iframe[title*="chart"]',            // Any chart iframe
		'iframe[title*="trading"]'           // Any trading iframe
	];

	for (const selector of selectors) {
		const element = document.querySelector(selector) as HTMLElement;
		if (element && isElementVisible(element)) {
			console.log(`Chart iframe found using selector: ${selector}`);
			// Return the iframe element directly for precise capture
			return element;
		}
	}

	// Fallback: look for chart containers if no iframe found
	const fallbackSelectors = [
		'#tradingview_widget',
		'.tradingview-widget-container', 
		'#tradeberg-chart',
		'.chart-container'
	];

	for (const selector of fallbackSelectors) {
		const element = document.querySelector(selector) as HTMLElement;
		if (element && isElementVisible(element)) {
			console.log(`Chart container found using selector: ${selector}`);
			return element;
		}
	}

	console.warn('No TradingView chart element found');
	return null;
}

/**
 * Check if chart is ready for capture
 * 
 * @param element Chart element to check
 * @returns True if chart appears to be loaded
 */
function isChartReady(element: HTMLElement): boolean {
	// Basic checks for chart readiness
	if (!element || element.offsetWidth < 300 || element.offsetHeight < 200) {
		return false;
	}

	// Check if iframe is loaded (for TradingView widgets)
	const iframe = element.querySelector('iframe') || (element.tagName === 'IFRAME' ? element : null);
	if (iframe) {
		try {
			// Try to access iframe content (will fail for cross-origin)
			const iframeDoc = (iframe as HTMLIFrameElement).contentDocument;
			if (iframeDoc && iframeDoc.readyState !== 'complete') {
				return false;
			}
		} catch (e) {
			// Cross-origin iframe - assume it's loaded if it has dimensions
			return iframe.offsetWidth > 300 && iframe.offsetHeight > 200;
		}
	}

	return true;
}

/**
 * Compress image if it exceeds size limit
 * 
 * @param canvas Canvas element to compress
 * @param maxSize Maximum file size in bytes
 * @param quality Initial quality (0.1-1.0)
 * @returns Promise resolving to compressed blob
 */
async function compressImage(
	canvas: HTMLCanvasElement, 
	maxSize: number, 
	quality: number = 0.85
): Promise<{ blob: Blob; compressed: boolean }> {
	// Try PNG first (lossless)
	const pngBlob = await new Promise<Blob>((resolve) => {
		canvas.toBlob((blob) => resolve(blob!), 'image/png');
	});

	if (pngBlob.size <= maxSize) {
		return { blob: pngBlob, compressed: false };
	}

	// PNG too large, try JPEG with decreasing quality
	let currentQuality = quality;
	let attempts = 0;
	const maxAttempts = 5;

	while (attempts < maxAttempts && currentQuality > 0.1) {
		const jpegBlob = await new Promise<Blob>((resolve) => {
			canvas.toBlob((blob) => resolve(blob!), 'image/jpeg', currentQuality);
		});

		if (jpegBlob.size <= maxSize) {
			return { blob: jpegBlob, compressed: true };
		}

		currentQuality -= 0.15;
		attempts++;
	}

	// If still too large, return the most compressed version
	const finalBlob = await new Promise<Blob>((resolve) => {
		canvas.toBlob((blob) => resolve(blob!), 'image/jpeg', 0.1);
	});

	return { blob: finalBlob, compressed: true };
}

/**
 * Generate filename for captured chart
 * 
 * @param format Image format ('png' or 'jpeg')
 * @returns Filename with timestamp
 */
function generateFilename(format: string): string {
	const timestamp = new Date().toISOString()
		.replace(/[:.]/g, '-')
		.replace('T', '_')
		.split('.')[0];
	
	return `tradeberg-chart-${timestamp}.${format}`;
}

/**
 * Capture TradingView chart screenshot using browser native API
 * 
 * @param config Optional configuration overrides
 * @returns Promise resolving to capture result
 */
export async function captureChart(config: ChartCaptureConfig = {}): Promise<ChartCaptureResult> {
	const finalConfig = { ...DEFAULT_CONFIG, ...config };
	
	try {
		// Step 1: Find chart element
		const chartElement = findTradingViewChart();
		if (!chartElement) {
			return {
				success: false,
				error: 'Chart not found. Please open a TradingView chart first.'
			};
		}

		// Step 2: Check if chart is ready
		if (!isChartReady(chartElement)) {
			return {
				success: false,
				error: 'Chart is still loading. Please wait a moment and try again.'
			};
		}

		// Step 3: Use browser native screen capture API (same as "Capture" button)
		let mediaStream: MediaStream;
		
		try {
			// Request screen capture with preferCurrentTab to avoid popup
			mediaStream = await navigator.mediaDevices.getDisplayMedia({
				video: {
					mediaSource: 'screen',
					width: { ideal: chartElement.offsetWidth * 2 },
					height: { ideal: chartElement.offsetHeight * 2 }
				},
				audio: false,
				// @ts-ignore - preferCurrentTab is supported in Chromium browsers
				preferCurrentTab: true,
				// @ts-ignore - selfBrowserSurface for current tab
				selfBrowserSurface: 'include'
			});
		} catch (error) {
			// Fallback to regular screen capture if preferCurrentTab fails
			mediaStream = await navigator.mediaDevices.getDisplayMedia({
				video: {
					mediaSource: 'screen',
					width: { ideal: 1920 },
					height: { ideal: 1080 }
				},
				audio: false
			});
		}

		// Step 4: Create video element and capture frame
		const video = document.createElement('video');
		video.srcObject = mediaStream;
		video.autoplay = true;
		video.muted = true;

		// Wait for video to be ready
		await new Promise<void>((resolve) => {
			video.onloadedmetadata = () => {
				video.play();
				resolve();
			};
		});

		// Step 5: Create canvas and capture current frame
		const canvas = document.createElement('canvas');
		const ctx = canvas.getContext('2d')!;
		
		// Get chart element position for cropping
		const rect = chartElement.getBoundingClientRect();
		const scaleX = video.videoWidth / window.innerWidth;
		const scaleY = video.videoHeight / window.innerHeight;
		
		// Calculate crop area (chart only)
		const cropX = Math.max(0, Math.floor(rect.left * scaleX));
		const cropY = Math.max(0, Math.floor(rect.top * scaleY));
		const cropWidth = Math.min(video.videoWidth - cropX, Math.floor(rect.width * scaleX));
		const cropHeight = Math.min(video.videoHeight - cropY, Math.floor(rect.height * scaleY));
		
		// Set canvas size to cropped area
		canvas.width = cropWidth;
		canvas.height = cropHeight;
		
		// Draw cropped video frame to canvas
		ctx.drawImage(video, cropX, cropY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);
		
		// Stop media stream
		mediaStream.getTracks().forEach(track => track.stop());

		// Step 6: Convert canvas to blob
		const blob = await new Promise<Blob>((resolve) => {
			canvas.toBlob((blob) => {
				resolve(blob!);
			}, 'image/png', 1.0);
		});

		// Step 7: Compress if needed
		const { blob: finalBlob, compressed } = await compressImage(canvas, finalConfig.maxFileSize, finalConfig.compressionQuality);
		
		// Step 8: Create file object
		const format = compressed ? 'jpeg' : 'png';
		const filename = generateFilename(format);
		const file = new File([finalBlob], filename, { 
			type: `image/${format}`,
			lastModified: Date.now()
		});

		return {
			success: true,
			file,
			metadata: {
				width: canvas.width,
				height: canvas.height,
				format,
				compressed,
				size: finalBlob.size,
				timestamp: Date.now()
			}
		};

	} catch (error) {
		console.error('Chart capture failed:', error);
		
		// Provide user-friendly error messages
		if (error instanceof Error) {
			if (error.name === 'NotAllowedError') {
				return {
					success: false,
					error: 'Screen capture permission denied. Please allow screen sharing to capture charts.'
				};
			}
			
			if (error.name === 'NotSupportedError') {
				return {
					success: false,
					error: 'Screen capture not supported in this browser. Please use Chrome or Edge.'
				};
			}
			
			if (error.message.includes('timeout')) {
				return {
					success: false,
					error: 'Screenshot capture timed out. Please try again.'
				};
			}
		}

		return {
			success: false,
			error: 'Failed to capture chart. Please try again or use manual screenshot.'
		};
	}
}

/**
 * Check if chart capture is supported in current browser
 * 
 * @returns True if capture is likely to work
 */
export function isChartCaptureSupported(): boolean {
	// Check for required APIs
	if (typeof HTMLCanvasElement === 'undefined') return false;
	if (typeof Blob === 'undefined') return false;
	if (typeof File === 'undefined') return false;
	
	// Check if html2canvas is available
	try {
		return typeof html2canvas === 'function';
	} catch {
		return false;
	}
}

/**
 * Get chart element info for debugging
 * 
 * @returns Chart element information
 */
export function getChartInfo(): {
	found: boolean;
	element?: string;
	dimensions?: { width: number; height: number };
	ready?: boolean;
} {
	const element = findTradingViewChart();
	
	if (!element) {
		return { found: false };
	}

	return {
		found: true,
		element: element.tagName.toLowerCase() + (element.id ? `#${element.id}` : '') + (element.className ? `.${element.className.split(' ').join('.')}` : ''),
		dimensions: {
			width: element.offsetWidth,
			height: element.offsetHeight
		},
		ready: isChartReady(element)
	};
}
