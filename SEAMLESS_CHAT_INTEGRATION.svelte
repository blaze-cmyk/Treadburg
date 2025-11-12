<!--
  Complete Example: Seamless Chart Analysis Integration
  
  This shows how to integrate the silent chart analysis system into your chat page.
  Copy the relevant parts into your actual chat component.
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import ChartAnalysisHandler from '$lib/components/ChartAnalysisHandler.svelte';
	import { chartState } from '$lib/stores/chart-state';
	import { formatAnalysisRequest } from '$lib/utils/trading-intent';
	import type { ChartAnalysisResponse } from '$lib/apis/tradeberg';

	// Message type
	interface Message {
		id: string;
		role: 'user' | 'assistant';
		content: string;
		isLoading?: boolean;
		error?: boolean;
		metadata?: {
			method?: string;
			provider?: string;
			cost?: number;
			from_cache?: boolean;
			tokens_used?: number;
		};
		timestamp: number;
	}

	// State
	let messages: Message[] = [];
	let userInput = '';
	let isLoading = false;
	let analysisHandler: ChartAnalysisHandler;

	// Chart settings
	let visionProvider: 'openai' | 'claude' = 'openai';
	let useCache = true;

	/**
	 * Main message handler - seamlessly detects and handles chart analysis
	 */
	async function sendMessage() {
		if (!userInput.trim() || isLoading) return;

		const message = userInput.trim();
		userInput = '';

		// Add user message to chat
		addMessage({
			id: generateId(),
			role: 'user',
			content: message,
			timestamp: Date.now()
		});

		// Try chart analysis first (completely silent)
		const handled = await analysisHandler.handleMessage(message);

		if (!handled) {
			// Not a chart analysis request - use normal chat flow
			await handleNormalChat(message);
		}
	}

	/**
	 * Handle normal (non-chart) chat messages
	 */
	async function handleNormalChat(message: string) {
		isLoading = true;

		// Add loading message
		const loadingId = generateId();
		addMessage({
			id: loadingId,
			role: 'assistant',
			content: 'Thinking...',
			isLoading: true,
			timestamp: Date.now()
		});

		try {
			// Your normal chat API call here
			const response = await fetch('/api/chat', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ message })
			});

			const data = await response.json();

			// Update loading message with response
			updateMessage(loadingId, {
				content: data.response,
				isLoading: false
			});
		} catch (error) {
			console.error('Chat error:', error);

			updateMessage(loadingId, {
				content: 'Sorry, I encountered an error. Please try again.',
				isLoading: false,
				error: true
			});
		} finally {
			isLoading = false;
		}
	}

	/**
	 * Chart analysis started - show loading indicator
	 */
	function handleAnalysisStart(intent: any) {
		const loadingMessage = formatAnalysisRequest(intent);

		addMessage({
			id: 'analysis-loading',
			role: 'assistant',
			content: `🔍 ${loadingMessage}`,
			isLoading: true,
			timestamp: Date.now()
		});
	}

	/**
	 * Chart analysis complete - show results
	 */
	function handleAnalysisComplete(result: ChartAnalysisResponse) {
		// Replace loading message with actual analysis
		updateMessage('analysis-loading', {
			content: result.analysis,
			isLoading: false,
			metadata: {
				method: result.method,
				provider: result.provider,
				cost: result.cost,
				from_cache: result.from_cache,
				tokens_used: result.tokens_used
			}
		});

		console.log(
			`💰 Analysis cost: $${result.cost?.toFixed(4) || 0} (${result.from_cache ? 'cached' : 'fresh'})`
		);
	}

	/**
	 * Chart analysis failed - show error
	 */
	function handleAnalysisError(error: string) {
		updateMessage('analysis-loading', {
			content: `TRADEBERG: ${error}`,
			isLoading: false,
			error: true
		});
	}

	/**
	 * Add message to chat
	 */
	function addMessage(message: Message) {
		messages = [...messages, message];
		scrollToBottom();
	}

	/**
	 * Update existing message
	 */
	function updateMessage(id: string, updates: Partial<Message>) {
		messages = messages.map((msg) => (msg.id === id ? { ...msg, ...updates } : msg));
		scrollToBottom();
	}

	/**
	 * Generate unique message ID
	 */
	function generateId(): string {
		return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
	}

	/**
	 * Scroll chat to bottom
	 */
	function scrollToBottom() {
		setTimeout(() => {
			const chatContainer = document.querySelector('.chat-messages');
			if (chatContainer) {
				chatContainer.scrollTop = chatContainer.scrollHeight;
			}
		}, 100);
	}

	/**
	 * Handle keyboard shortcuts
	 */
	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}

	/**
	 * Quick action buttons
	 */
	function quickAnalysis(prompt: string) {
		userInput = prompt;
		sendMessage();
	}
</script>

<div class="chat-container">
	<!-- Chart Analysis Handler (invisible component) -->
	<ChartAnalysisHandler
		bind:this={analysisHandler}
		{visionProvider}
		{useCache}
		onAnalysisStart={handleAnalysisStart}
		onAnalysisComplete={handleAnalysisComplete}
		onAnalysisError={handleAnalysisError}
	/>

	<!-- Settings Bar -->
	<div class="settings-bar">
		<div class="setting">
			<label>
				<input type="checkbox" bind:checked={useCache} />
				Use Cache (5min)
			</label>
		</div>

		<div class="setting">
			<label>
				Vision Provider:
				<select bind:value={visionProvider}>
					<option value="openai">OpenAI GPT-4o ($0.05)</option>
					<option value="claude">Claude 3.5 Sonnet ($0.03)</option>
				</select>
			</label>
		</div>

		<div class="chart-status">
			{#if $chartState.isOpen}
				<span class="status-indicator active"></span>
				Chart: {$chartState.symbol} {$chartState.timeframe}
			{:else}
				<span class="status-indicator"></span>
				Chart: Closed
			{/if}
		</div>
	</div>

	<!-- Messages Display -->
	<div class="chat-messages">
		{#each messages as message (message.id)}
			<div class="message {message.role}" class:loading={message.isLoading} class:error={message.error}>
				<div class="message-content">
					{message.content}

					<!-- Metadata (optional) -->
					{#if message.metadata && !message.isLoading}
						<div class="message-metadata">
							<span class="badge">{message.metadata.method}</span>
							{#if message.metadata.provider}
								<span class="badge">{message.metadata.provider}</span>
							{/if}
							{#if message.metadata.from_cache}
								<span class="badge cache">cached</span>
							{/if}
							{#if message.metadata.cost}
								<span class="badge cost">${message.metadata.cost.toFixed(4)}</span>
							{/if}
						</div>
					{/if}
				</div>

				<!-- Loading spinner -->
				{#if message.isLoading}
					<div class="spinner"></div>
				{/if}
			</div>
		{/each}
	</div>

	<!-- Quick Actions -->
	<div class="quick-actions">
		<button on:click={() => quickAnalysis('analyze BTCUSDT 15m')} disabled={isLoading}>
			📊 BTC 15m
		</button>
		<button on:click={() => quickAnalysis('check ETH levels')} disabled={isLoading}>
			⚡ ETH Levels
		</button>
		<button on:click={() => quickAnalysis('what\'s SOL doing on 1h')} disabled={isLoading}>
			🌟 SOL 1h
		</button>
	</div>

	<!-- Input Area -->
	<div class="input-area">
		<textarea
			bind:value={userInput}
			on:keydown={handleKeydown}
			placeholder="Ask about any chart... (e.g., 'analyze BTCUSDT 15m')"
			disabled={isLoading}
			rows="2"
		/>

		<button on:click={sendMessage} disabled={isLoading || !userInput.trim()}>
			{#if isLoading}
				Analyzing...
			{:else}
				Send
			{/if}
		</button>
	</div>

	<!-- Info Banner -->
	<div class="info-banner">
		💡 Just ask! Type "analyze BTCUSDT" or "check ETH levels" - screenshots happen automatically
		in the background
	</div>
</div>

<style>
	.chat-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		max-width: 1200px;
		margin: 0 auto;
		padding: 1rem;
		gap: 1rem;
	}

	.settings-bar {
		display: flex;
		align-items: center;
		gap: 1.5rem;
		padding: 0.75rem 1rem;
		background: #f8f9fa;
		border-radius: 8px;
		font-size: 0.875rem;
	}

	.setting label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.chart-status {
		margin-left: auto;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-weight: 500;
	}

	.status-indicator {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: #6c757d;
	}

	.status-indicator.active {
		background: #28a745;
		animation: pulse 2s infinite;
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}

	.chat-messages {
		flex: 1;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding: 1rem;
		background: white;
		border-radius: 8px;
		border: 1px solid #dee2e6;
	}

	.message {
		padding: 1rem;
		border-radius: 8px;
		max-width: 80%;
		position: relative;
	}

	.message.user {
		align-self: flex-end;
		background: #007bff;
		color: white;
	}

	.message.assistant {
		align-self: flex-start;
		background: #f1f3f5;
		color: #212529;
	}

	.message.loading {
		opacity: 0.7;
	}

	.message.error {
		background: #fff3cd;
		border: 1px solid #ffc107;
	}

	.message-content {
		white-space: pre-wrap;
		word-wrap: break-word;
		line-height: 1.6;
	}

	.message-metadata {
		display: flex;
		gap: 0.5rem;
		margin-top: 0.75rem;
		flex-wrap: wrap;
	}

	.badge {
		display: inline-block;
		padding: 0.25rem 0.5rem;
		background: rgba(0, 0, 0, 0.1);
		border-radius: 4px;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.badge.cache {
		background: #d4edda;
		color: #155724;
	}

	.badge.cost {
		background: #fff3cd;
		color: #856404;
	}

	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid #f3f3f3;
		border-top: 2px solid #007bff;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		position: absolute;
		right: 1rem;
		top: 1rem;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	.quick-actions {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.quick-actions button {
		padding: 0.5rem 1rem;
		background: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s;
		font-size: 0.875rem;
	}

	.quick-actions button:hover:not(:disabled) {
		background: #e9ecef;
		border-color: #adb5bd;
	}

	.quick-actions button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.input-area {
		display: flex;
		gap: 0.5rem;
	}

	textarea {
		flex: 1;
		padding: 0.75rem;
		border: 1px solid #ced4da;
		border-radius: 6px;
		font-family: inherit;
		font-size: 1rem;
		resize: vertical;
		min-height: 60px;
	}

	textarea:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
	}

	textarea:disabled {
		background: #e9ecef;
		cursor: not-allowed;
	}

	.input-area button {
		padding: 0.75rem 1.5rem;
		background: #007bff;
		color: white;
		border: none;
		border-radius: 6px;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.2s;
		min-width: 100px;
	}

	.input-area button:hover:not(:disabled) {
		background: #0056b3;
	}

	.input-area button:disabled {
		background: #6c757d;
		cursor: not-allowed;
	}

	.info-banner {
		padding: 0.75rem 1rem;
		background: #d1ecf1;
		border: 1px solid #bee5eb;
		border-radius: 6px;
		font-size: 0.875rem;
		color: #0c5460;
		text-align: center;
	}
</style>
