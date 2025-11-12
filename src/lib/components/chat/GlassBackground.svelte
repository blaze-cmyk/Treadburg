<script lang="ts">
	import { glassUISettings } from '$lib/stores/glassUI';
	import { onMount } from 'svelte';
	
	// Predefined background options
	const backgrounds = {
		gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
		landscape: 'url("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=80")',
		abstract: 'url("https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=1920&q=80")',
		crypto: 'linear-gradient(135deg, #1e3a8a 0%, #7c3aed 50%, #ec4899 100%)',
		dark: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
		blue: 'linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%)',
		purple: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
		green: 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
	};
	
	$: backgroundStyle = backgrounds[$glassUISettings.backgroundImage] || backgrounds.gradient;
	
	// Apply glass effects directly to elements
	onMount(() => {
		const applyGlassEffect = () => {
			if ($glassUISettings.enabled && $glassUISettings.blur) {
				const blurValue = `${$glassUISettings.blurAmount}px`;
				
				// Apply to messages container
				const messagesContainer = document.getElementById('messages-container');
				if (messagesContainer) {
					messagesContainer.style.background = 'rgba(255, 255, 255, 0.05)';
					messagesContainer.style.backdropFilter = `blur(${blurValue})`;
					messagesContainer.style.webkitBackdropFilter = `blur(${blurValue})`;
					messagesContainer.style.borderRadius = '12px';
				}
				
				// Apply to all message elements
				const messages = document.querySelectorAll('[id*="message-"]');
				messages.forEach((msg: Element) => {
					if (msg instanceof HTMLElement) {
						msg.style.background = 'rgba(255, 255, 255, 0.12)';
						msg.style.backdropFilter = `blur(${blurValue})`;
						msg.style.webkitBackdropFilter = `blur(${blurValue})`;
						msg.style.border = '1px solid rgba(255, 255, 255, 0.2)';
						msg.style.borderRadius = '16px';
					}
				});
				
				// Apply to textarea
				const textareas = document.querySelectorAll('textarea');
				textareas.forEach((textarea: Element) => {
					if (textarea instanceof HTMLElement) {
						textarea.style.background = 'rgba(255, 255, 255, 0.15)';
						textarea.style.backdropFilter = `blur(${blurValue})`;
						textarea.style.webkitBackdropFilter = `blur(${blurValue})`;
						textarea.style.border = '1px solid rgba(255, 255, 255, 0.25)';
					}
				});
			} else {
				// Remove glass effects when disabled
				const messagesContainer = document.getElementById('messages-container');
				if (messagesContainer) {
					messagesContainer.style.background = '';
					messagesContainer.style.backdropFilter = '';
					messagesContainer.style.webkitBackdropFilter = '';
					messagesContainer.style.borderRadius = '';
				}
			}
		};
		
		// Apply immediately
		setTimeout(applyGlassEffect, 100);
		
		// Re-apply when settings change
		const unsubscribe = glassUISettings.subscribe(() => {
			setTimeout(applyGlassEffect, 50);
		});
		
		// Re-apply when messages change
		const observer = new MutationObserver(() => {
			setTimeout(applyGlassEffect, 50);
		});
		const messagesContainer = document.getElementById('messages-container');
		if (messagesContainer) {
			observer.observe(messagesContainer, { childList: true, subtree: true });
		}
		
		return () => {
			unsubscribe();
			observer.disconnect();
		};
	});
</script>

{#if $glassUISettings.enabled}
	<div class="glass-background" style="background: {backgroundStyle};">
		{#if $glassUISettings.overlay}
			<div class="glass-overlay" style="opacity: {$glassUISettings.opacity};"></div>
		{/if}
	</div>
{/if}

<style>
	.glass-background {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 0;
		background-size: cover !important;
		background-position: center !important;
		background-repeat: no-repeat !important;
		animation: backgroundShift 30s ease-in-out infinite;
		pointer-events: none;
	}
	
	@keyframes backgroundShift {
		0%, 100% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
	}
	
	.glass-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: linear-gradient(135deg, rgba(0, 0, 0, 0.5) 0%, rgba(0, 0, 0, 0.3) 100%);
		pointer-events: none;
	}
</style>
