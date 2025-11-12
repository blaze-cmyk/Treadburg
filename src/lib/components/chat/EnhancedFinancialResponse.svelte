<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, slide, scale } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	
	export let content: string = '';
	
	let mounted = false;
	
	onMount(() => {
		mounted = true;
	});
	
	// Parse content to extract components
	function parseContent(text: string) {
		const parts = [];
		let currentText = '';
		let inCodeBlock = false;
		let codeBlock = '';
		
		const lines = text.split('\n');
		
		for (let i = 0; i < lines.length; i++) {
			const line = lines[i];
			
			if (line.startsWith('```json:chart:')) {
				if (currentText.trim()) {
					parts.push({ type: 'text', content: currentText.trim() });
					currentText = '';
				}
				inCodeBlock = true;
				codeBlock = line + '\n';
			} else if (line === '```' && inCodeBlock) {
				codeBlock += line;
				parts.push({ type: 'chart', content: codeBlock });
				codeBlock = '';
				inCodeBlock = false;
			} else if (inCodeBlock) {
				codeBlock += line + '\n';
			} else {
				currentText += line + '\n';
			}
		}
		
		if (currentText.trim()) {
			parts.push({ type: 'text', content: currentText.trim() });
		}
		
		return parts;
	}
	
	$: parts = parseContent(content);
</script>

<div class="enhanced-financial-response" class:mounted>
	{#each parts as part, i}
		{#if part.type === 'text'}
			<div 
				class="text-section glass-card"
				in:fade={{ delay: i * 100, duration: 400 }}
			>
				<div class="gradient-border"></div>
				<div class="content">
					{@html part.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
				</div>
			</div>
		{:else if part.type === 'chart'}
			<div 
				class="chart-section glass-card"
				in:scale={{ delay: i * 150, duration: 500, easing: quintOut }}
			>
				<div class="gradient-border pulse"></div>
				<div class="chart-content">
					<slot name="chart" {part} />
					<!-- This will be handled by FinancialAnalysisRenderer -->
					<div class="chart-placeholder">
						{part.content}
					</div>
				</div>
			</div>
		{/if}
	{/each}
</div>

<style>
	.enhanced-financial-response {
		display: flex;
		flex-direction: column;
		gap: 20px;
		padding: 8px;
		opacity: 0;
		transform: translateY(10px);
		transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
	}
	
	.enhanced-financial-response.mounted {
		opacity: 1;
		transform: translateY(0);
	}
	
	.glass-card {
		position: relative;
		background: rgba(255, 255, 255, 0.03);
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
		border-radius: 16px;
		padding: 24px;
		border: 1px solid rgba(255, 255, 255, 0.08);
		box-shadow: 
			0 8px 32px 0 rgba(0, 0, 0, 0.37),
			inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
		overflow: hidden;
		transition: all 0.3s ease;
	}
	
	.glass-card:hover {
		background: rgba(255, 255, 255, 0.05);
		border-color: rgba(255, 255, 255, 0.12);
		transform: translateY(-2px);
		box-shadow: 
			0 12px 40px 0 rgba(0, 0, 0, 0.45),
			inset 0 1px 0 0 rgba(255, 255, 255, 0.08);
	}
	
	.gradient-border {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: linear-gradient(
			90deg,
			#667eea 0%,
			#764ba2 25%,
			#f093fb 50%,
			#4facfe 75%,
			#00f2fe 100%
		);
		background-size: 200% 100%;
		animation: gradientShift 3s ease infinite;
	}
	
	.gradient-border.pulse {
		animation: gradientShift 3s ease infinite, pulse 2s ease-in-out infinite;
	}
	
	@keyframes gradientShift {
		0%, 100% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
	}
	
	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.6;
		}
	}
	
	.text-section {
		background: rgba(255, 255, 255, 0.02);
	}
	
	.text-section .content {
		color: #e5e5e5;
		font-size: 15px;
		line-height: 1.7;
		letter-spacing: 0.3px;
	}
	
	.text-section .content :global(strong) {
		color: #fff;
		font-weight: 600;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}
	
	.chart-section {
		background: rgba(0, 0, 0, 0.2);
		padding: 0;
		overflow: visible;
	}
	
	.chart-content {
		padding: 24px;
	}
	
	.chart-placeholder {
		display: none;
	}
	
	/* Responsive */
	@media (max-width: 768px) {
		.enhanced-financial-response {
			gap: 16px;
			padding: 4px;
		}
		
		.glass-card {
			padding: 16px;
			border-radius: 12px;
		}
		
		.text-section .content {
			font-size: 14px;
		}
	}
	
	/* Dark mode enhancements */
	:global(.dark) .glass-card {
		background: rgba(255, 255, 255, 0.04);
		border-color: rgba(255, 255, 255, 0.1);
	}
	
	:global(.dark) .glass-card:hover {
		background: rgba(255, 255, 255, 0.06);
		border-color: rgba(255, 255, 255, 0.15);
	}
	
	/* Glow effect on hover */
	.glass-card::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		border-radius: 16px;
		padding: 2px;
		background: linear-gradient(135deg, #667eea, #764ba2, #f093fb, #4facfe);
		-webkit-mask: 
			linear-gradient(#fff 0 0) content-box, 
			linear-gradient(#fff 0 0);
		-webkit-mask-composite: xor;
		mask-composite: exclude;
		opacity: 0;
		transition: opacity 0.3s ease;
	}
	
	.glass-card:hover::before {
		opacity: 0.3;
	}
</style>
