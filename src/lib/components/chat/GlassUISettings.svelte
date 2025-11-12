<script lang="ts">
	import { glassUISettings, toggleGlassUI, toggleBlur, toggleOverlay, setBackgroundImage, setOpacity, setBlurAmount } from '$lib/stores/glassUI';
	import { slide } from 'svelte/transition';
	
	let showSettings = false;
	
	const backgroundOptions = [
		{ id: 'gradient', name: 'Purple Gradient', preview: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
		{ id: 'crypto', name: 'Crypto Gradient', preview: 'linear-gradient(135deg, #1e3a8a 0%, #7c3aed 50%, #ec4899 100%)' },
		{ id: 'blue', name: 'Blue Gradient', preview: 'linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%)' },
		{ id: 'purple', name: 'Purple Wave', preview: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)' },
		{ id: 'green', name: 'Green Gradient', preview: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' },
		{ id: 'dark', name: 'Dark Mode', preview: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)' },
		{ id: 'landscape', name: 'Landscape', preview: 'url("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80")' },
		{ id: 'abstract', name: 'Abstract', preview: 'url("https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=400&q=80")' }
	];
</script>

<div class="glass-ui-controls">
	<!-- Toggle Button -->
	<button
		class="glass-toggle-btn"
		on:click={() => showSettings = !showSettings}
		title="Glass UI Settings"
	>
		<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<circle cx="12" cy="12" r="3"></circle>
			<path d="M12 1v6m0 6v6m-6-6h6m6 0h6"></path>
			<circle cx="12" cy="12" r="10"></circle>
		</svg>
		<span class="ml-2">Glass UI</span>
	</button>
	
	<!-- Settings Panel -->
	{#if showSettings}
		<div class="glass-settings-panel" transition:slide={{ duration: 300 }}>
			<div class="settings-header">
				<h3>🎨 Glass UI Settings</h3>
				<button class="close-btn" on:click={() => showSettings = false}>×</button>
			</div>
			
			<div class="settings-content">
				<!-- Enable/Disable -->
				<div class="setting-item">
					<label class="setting-label">
						<input
							type="checkbox"
							checked={$glassUISettings.enabled}
							on:change={toggleGlassUI}
							class="toggle-checkbox"
						/>
						<span>Enable Glass UI</span>
					</label>
					<p class="setting-description">Apply glassmorphism effect to chat interface</p>
				</div>
				
				{#if $glassUISettings.enabled}
					<!-- Blur Effect -->
					<div class="setting-item">
						<label class="setting-label">
							<input
								type="checkbox"
								checked={$glassUISettings.blur}
								on:change={toggleBlur}
								class="toggle-checkbox"
							/>
							<span>Background Blur</span>
						</label>
						<p class="setting-description">Apply blur effect to panels</p>
					</div>
					
					<!-- Blur Amount -->
					{#if $glassUISettings.blur}
						<div class="setting-item">
							<label class="setting-label">
								<span>Blur Intensity</span>
							</label>
							<input
								type="range"
								min="4"
								max="24"
								step="2"
								value={$glassUISettings.blurAmount}
								on:input={(e) => setBlurAmount(Number(e.currentTarget.value))}
								class="slider"
							/>
							<span class="slider-value">{$glassUISettings.blurAmount}px</span>
						</div>
					{/if}
					
					<!-- Overlay -->
					<div class="setting-item">
						<label class="setting-label">
							<input
								type="checkbox"
								checked={$glassUISettings.overlay}
								on:change={toggleOverlay}
								class="toggle-checkbox"
							/>
							<span>Dark Overlay</span>
						</label>
						<p class="setting-description">Add dark tint for better readability</p>
					</div>
					
					<!-- Opacity -->
					{#if $glassUISettings.overlay}
						<div class="setting-item">
							<label class="setting-label">
								<span>Overlay Opacity</span>
							</label>
							<input
								type="range"
								min="0"
								max="0.5"
								step="0.05"
								value={$glassUISettings.opacity}
								on:input={(e) => setOpacity(Number(e.currentTarget.value))}
								class="slider"
							/>
							<span class="slider-value">{Math.round($glassUISettings.opacity * 100)}%</span>
						</div>
					{/if}
					
					<!-- Background Selection -->
					<div class="setting-item">
						<label class="setting-label">
							<span>Background Style</span>
						</label>
						<div class="background-grid">
							{#each backgroundOptions as bg}
								<button
									class="background-option"
									class:active={$glassUISettings.backgroundImage === bg.id}
									style="background: {bg.preview}; background-size: cover; background-position: center;"
									on:click={() => setBackgroundImage(bg.id)}
									title={bg.name}
								>
									{#if $glassUISettings.backgroundImage === bg.id}
										<div class="check-mark">✓</div>
									{/if}
								</button>
							{/each}
						</div>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.glass-ui-controls {
		position: fixed;
		bottom: 20px;
		right: 20px;
		z-index: 1000;
	}
	
	.glass-toggle-btn {
		display: flex;
		align-items: center;
		padding: 12px 20px;
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 12px;
		color: white;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}
	
	.glass-toggle-btn:hover {
		background: rgba(255, 255, 255, 0.15);
		transform: translateY(-2px);
		box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
	}
	
	.glass-settings-panel {
		position: absolute;
		bottom: 60px;
		right: 0;
		width: 380px;
		max-height: 600px;
		overflow-y: auto;
		background: rgba(255, 255, 255, 0.95);
		backdrop-filter: blur(20px);
		border: 1px solid rgba(255, 255, 255, 0.3);
		border-radius: 16px;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
	}
	
	:global(.dark) .glass-settings-panel {
		background: rgba(30, 30, 30, 0.95);
		border-color: rgba(255, 255, 255, 0.1);
	}
	
	.settings-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20px;
		border-bottom: 1px solid rgba(0, 0, 0, 0.1);
	}
	
	:global(.dark) .settings-header {
		border-bottom-color: rgba(255, 255, 255, 0.1);
	}
	
	.settings-header h3 {
		margin: 0;
		font-size: 18px;
		font-weight: 600;
		color: #1f2937;
	}
	
	:global(.dark) .settings-header h3 {
		color: #f9fafb;
	}
	
	.close-btn {
		background: none;
		border: none;
		font-size: 28px;
		color: #6b7280;
		cursor: pointer;
		padding: 0;
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 8px;
		transition: all 0.2s;
	}
	
	.close-btn:hover {
		background: rgba(0, 0, 0, 0.05);
		color: #1f2937;
	}
	
	:global(.dark) .close-btn:hover {
		background: rgba(255, 255, 255, 0.1);
		color: #f9fafb;
	}
	
	.settings-content {
		padding: 20px;
	}
	
	.setting-item {
		margin-bottom: 24px;
	}
	
	.setting-label {
		display: flex;
		align-items: center;
		font-weight: 500;
		color: #1f2937;
		margin-bottom: 8px;
		cursor: pointer;
	}
	
	:global(.dark) .setting-label {
		color: #f9fafb;
	}
	
	.setting-description {
		font-size: 13px;
		color: #6b7280;
		margin: 4px 0 0 0;
	}
	
	.toggle-checkbox {
		margin-right: 10px;
		width: 18px;
		height: 18px;
		cursor: pointer;
	}
	
	.slider {
		width: 100%;
		height: 6px;
		border-radius: 3px;
		background: #e5e7eb;
		outline: none;
		margin: 8px 0;
		cursor: pointer;
	}
	
	:global(.dark) .slider {
		background: #374151;
	}
	
	.slider::-webkit-slider-thumb {
		appearance: none;
		width: 18px;
		height: 18px;
		border-radius: 50%;
		background: #3b82f6;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.slider::-webkit-slider-thumb:hover {
		background: #2563eb;
		transform: scale(1.1);
	}
	
	.slider-value {
		font-size: 13px;
		color: #6b7280;
		font-weight: 500;
	}
	
	.background-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 10px;
		margin-top: 12px;
	}
	
	.background-option {
		aspect-ratio: 1;
		border-radius: 8px;
		border: 2px solid transparent;
		cursor: pointer;
		transition: all 0.2s;
		position: relative;
		overflow: hidden;
	}
	
	.background-option:hover {
		transform: scale(1.05);
		border-color: rgba(59, 130, 246, 0.5);
	}
	
	.background-option.active {
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
	}
	
	.check-mark {
		position: absolute;
		top: 4px;
		right: 4px;
		background: #3b82f6;
		color: white;
		width: 20px;
		height: 20px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 12px;
		font-weight: bold;
	}
	
	/* Scrollbar styling */
	.glass-settings-panel::-webkit-scrollbar {
		width: 6px;
	}
	
	.glass-settings-panel::-webkit-scrollbar-track {
		background: transparent;
	}
	
	.glass-settings-panel::-webkit-scrollbar-thumb {
		background: rgba(0, 0, 0, 0.2);
		border-radius: 3px;
	}
	
	:global(.dark) .glass-settings-panel::-webkit-scrollbar-thumb {
		background: rgba(255, 255, 255, 0.2);
	}
</style>
