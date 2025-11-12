<script lang="ts">
	import { onMount } from 'svelte';
	import { perplexityAPI, type ChatMessage, type ChatResponse, type Citation } from '$lib/apis/perplexity';

	// Component state
	let messages: ChatMessage[] = [];
	let currentMessage = '';
	let isLoading = false;
	let error = '';
	let selectedFile: File | null = null;
	let fileInput: HTMLInputElement;
	let chatContainer: HTMLElement;
	let isServiceHealthy = false;

	// Response data
	let lastResponse: ChatResponse | null = null;
	let citations: Citation[] = [];
	let relatedQuestions: string[] = [];

	onMount(async () => {
		await checkServiceHealth();
		// Load conversation from localStorage
		loadConversation();
	});

	async function checkServiceHealth() {
		try {
			const health = await perplexityAPI.getHealth();
			isServiceHealthy = health.status === 'ok' && health.perplexity_api_configured;
			if (!isServiceHealthy) {
				error = 'Perplexity API not configured. Please check your API key.';
			}
		} catch (err) {
			console.error('Service health check failed:', err);
			error = 'Perplexity service is not available. Please ensure it\'s running on port 8001.';
			isServiceHealthy = false;
		}
	}

	function loadConversation() {
		const saved = localStorage.getItem('perplexity-chat-history');
		if (saved) {
			try {
				messages = JSON.parse(saved);
			} catch (err) {
				console.error('Failed to load conversation:', err);
			}
		}
	}

	function saveConversation() {
		localStorage.setItem('perplexity-chat-history', JSON.stringify(messages));
	}

	async function sendMessage() {
		if (!currentMessage.trim() && !selectedFile) return;
		if (isLoading) return;
		if (!isServiceHealthy) {
			error = 'Service not available. Please check the connection.';
			return;
		}

		isLoading = true;
		error = '';

		// Add user message
		const userMessage: ChatMessage = {
			role: 'user',
			content: currentMessage.trim() || 'Analyze this chart'
		};
		messages = [...messages, userMessage];

		try {
			let response: ChatResponse;

			if (selectedFile) {
				response = await perplexityAPI.uploadImageForAnalysis(selectedFile, currentMessage.trim() || 'Analyze this chart');
			} else {
				response = await perplexityAPI.sendMessage({
					message: currentMessage.trim(),
					conversation_history: messages.slice(-10) // Keep last 10 messages for context
				});
			}

			if (response.success) {
				// Add assistant response
				const assistantMessage: ChatMessage = {
					role: 'assistant',
					content: response.message
				};
				messages = [...messages, assistantMessage];

				// Update response data
				lastResponse = response;
				citations = response.citations || [];
				relatedQuestions = response.related_questions || [];
			} else {
				error = response.error || 'Failed to get response';
			}
		} catch (err) {
			console.error('Send message error:', err);
			error = `Failed to send message: ${err instanceof Error ? err.message : 'Unknown error'}`;
		} finally {
			isLoading = false;
			currentMessage = '';
			selectedFile = null;
			if (fileInput) fileInput.value = '';
			saveConversation();
			scrollToBottom();
		}
	}

	function handleFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			selectedFile = target.files[0];
		}
	}

	function removeFile() {
		selectedFile = null;
		if (fileInput) fileInput.value = '';
	}

	function askRelatedQuestion(question: string) {
		currentMessage = question;
		sendMessage();
	}

	function clearChat() {
		messages = [];
		citations = [];
		relatedQuestions = [];
		lastResponse = null;
		error = '';
		localStorage.removeItem('perplexity-chat-history');
	}

	function scrollToBottom() {
		setTimeout(() => {
			if (chatContainer) {
				chatContainer.scrollTop = chatContainer.scrollHeight;
			}
		}, 100);
	}

	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}
</script>

<div class="perplexity-chat-container">
	<!-- Header -->
	<div class="chat-header">
		<div class="header-content">
			<h2>🧠 Perplexity Trading Bot</h2>
			<div class="header-status">
				<span class="status-indicator {isServiceHealthy ? 'healthy' : 'unhealthy'}"></span>
				<span class="status-text">{isServiceHealthy ? 'Connected' : 'Disconnected'}</span>
			</div>
		</div>
		<button class="clear-btn" on:click={clearChat} title="Clear Chat">
			🗑️
		</button>
	</div>

	<!-- Error Display -->
	{#if error}
		<div class="error-banner">
			⚠️ {error}
		</div>
	{/if}

	<!-- Chat Messages -->
	<div class="chat-messages" bind:this={chatContainer}>
		{#if messages.length === 0}
			<div class="welcome-message">
				<h3>Welcome to Perplexity Trading Bot</h3>
				<p>Ask me about market analysis, chart interpretation, or trading strategies.</p>
				<div class="quick-actions">
					<button class="quick-btn" on:click={() => { currentMessage = 'Analyze Bitcoin price action'; sendMessage(); }}>
						📈 Analyze Bitcoin
					</button>
					<button class="quick-btn" on:click={() => { currentMessage = 'What\'s the current market sentiment?'; sendMessage(); }}>
						📊 Market Sentiment
					</button>
					<button class="quick-btn" on:click={() => { currentMessage = 'Show me key support and resistance levels for ETH'; sendMessage(); }}>
						🎯 ETH Levels
					</button>
				</div>
			</div>
		{/if}

		{#each messages as message, i}
			<div class="message {message.role}">
				<div class="message-content">
					{@html message.content.replace(/\n/g, '<br>')}
				</div>
				{#if message.role === 'assistant' && i === messages.length - 1}
					<!-- Show metadata for last assistant message -->
					{#if lastResponse}
						<div class="message-metadata">
							<span>Model: {lastResponse.model_used}</span>
							{#if lastResponse.processing_time}
								<span>Time: {perplexityAPI.formatProcessingTime(lastResponse.processing_time)}</span>
							{/if}
							{#if lastResponse.tokens_used}
								<span>Tokens: {perplexityAPI.formatTokenUsage(lastResponse.tokens_used)}</span>
							{/if}
						</div>
					{/if}
				{/if}
			</div>
		{/each}

		{#if isLoading}
			<div class="message assistant loading">
				<div class="message-content">
					<div class="typing-indicator">
						<span></span>
						<span></span>
						<span></span>
					</div>
					Analyzing...
				</div>
			</div>
		{/if}
	</div>

	<!-- Citations -->
	{#if citations.length > 0}
		<div class="citations-section">
			<h4>📚 Sources</h4>
			<div class="citations-list">
				{#each citations as citation}
					<a href={citation.url} target="_blank" class="citation-item">
						<div class="citation-title">{citation.title}</div>
						{#if citation.snippet}
							<div class="citation-snippet">{citation.snippet}</div>
						{/if}
					</a>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Related Questions -->
	{#if relatedQuestions.length > 0}
		<div class="related-questions">
			<h4>💡 Related Questions</h4>
			<div class="questions-list">
				{#each relatedQuestions as question}
					<button class="question-chip" on:click={() => askRelatedQuestion(question)}>
						{question}
					</button>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Input Area -->
	<div class="input-area">
		<!-- File Upload -->
		<div class="file-upload-section">
			<input
				type="file"
				accept="image/*"
				bind:this={fileInput}
				on:change={handleFileSelect}
				class="file-input"
			/>
			<button class="file-btn" on:click={() => fileInput?.click()}>
				📎 Upload Chart
			</button>
			{#if selectedFile}
				<div class="selected-file">
					<span>{selectedFile.name}</span>
					<button class="remove-file" on:click={removeFile}>❌</button>
				</div>
			{/if}
		</div>

		<!-- Message Input -->
		<div class="message-input-container">
			<textarea
				bind:value={currentMessage}
				on:keypress={handleKeyPress}
				placeholder="Ask about market analysis, chart patterns, or trading strategies..."
				class="message-input"
				rows="2"
				disabled={isLoading || !isServiceHealthy}
			></textarea>
			<button
				class="send-btn"
				on:click={sendMessage}
				disabled={isLoading || !isServiceHealthy || (!currentMessage.trim() && !selectedFile)}
			>
				{isLoading ? '⏳' : '🚀'}
			</button>
		</div>
	</div>
</div>

<style>
	.perplexity-chat-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		max-width: 1200px;
		margin: 0 auto;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 12px;
		overflow: hidden;
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
	}

	.chat-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 1.5rem;
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(10px);
		border-bottom: 1px solid rgba(255, 255, 255, 0.2);
	}

	.header-content {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.header-content h2 {
		margin: 0;
		color: white;
		font-size: 1.5rem;
		font-weight: 600;
	}

	.header-status {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.status-indicator {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: #ef4444;
	}

	.status-indicator.healthy {
		background: #10b981;
	}

	.status-text {
		color: rgba(255, 255, 255, 0.8);
		font-size: 0.875rem;
	}

	.clear-btn {
		background: rgba(255, 255, 255, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.2);
		color: white;
		padding: 0.5rem;
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.clear-btn:hover {
		background: rgba(255, 255, 255, 0.2);
	}

	.error-banner {
		background: #ef4444;
		color: white;
		padding: 1rem 1.5rem;
		text-align: center;
		font-weight: 500;
	}

	.chat-messages {
		flex: 1;
		overflow-y: auto;
		padding: 1rem;
		background: rgba(255, 255, 255, 0.05);
	}

	.welcome-message {
		text-align: center;
		color: white;
		padding: 2rem;
	}

	.welcome-message h3 {
		margin: 0 0 1rem 0;
		font-size: 1.5rem;
	}

	.welcome-message p {
		margin: 0 0 2rem 0;
		opacity: 0.8;
	}

	.quick-actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
	}

	.quick-btn {
		background: rgba(255, 255, 255, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.2);
		color: white;
		padding: 0.75rem 1rem;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s;
		font-size: 0.875rem;
	}

	.quick-btn:hover {
		background: rgba(255, 255, 255, 0.2);
		transform: translateY(-2px);
	}

	.message {
		margin-bottom: 1rem;
		display: flex;
		flex-direction: column;
	}

	.message.user {
		align-items: flex-end;
	}

	.message.assistant {
		align-items: flex-start;
	}

	.message-content {
		max-width: 80%;
		padding: 1rem 1.5rem;
		border-radius: 18px;
		line-height: 1.5;
	}

	.message.user .message-content {
		background: rgba(255, 255, 255, 0.9);
		color: #333;
	}

	.message.assistant .message-content {
		background: rgba(255, 255, 255, 0.1);
		color: white;
		border: 1px solid rgba(255, 255, 255, 0.2);
	}

	.message.loading .message-content {
		background: rgba(255, 255, 255, 0.05);
	}

	.message-metadata {
		margin-top: 0.5rem;
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.6);
		display: flex;
		gap: 1rem;
	}

	.typing-indicator {
		display: inline-flex;
		gap: 4px;
		margin-right: 8px;
	}

	.typing-indicator span {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.6);
		animation: typing 1.4s infinite ease-in-out;
	}

	.typing-indicator span:nth-child(2) {
		animation-delay: 0.2s;
	}

	.typing-indicator span:nth-child(3) {
		animation-delay: 0.4s;
	}

	@keyframes typing {
		0%, 80%, 100% {
			transform: scale(0.8);
			opacity: 0.5;
		}
		40% {
			transform: scale(1);
			opacity: 1;
		}
	}

	.citations-section, .related-questions {
		padding: 1rem 1.5rem;
		background: rgba(255, 255, 255, 0.05);
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	.citations-section h4, .related-questions h4 {
		margin: 0 0 1rem 0;
		color: white;
		font-size: 1rem;
		font-weight: 600;
	}

	.citations-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.citation-item {
		display: block;
		padding: 0.75rem;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 8px;
		text-decoration: none;
		color: white;
		transition: all 0.2s;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.citation-item:hover {
		background: rgba(255, 255, 255, 0.2);
		transform: translateY(-1px);
	}

	.citation-title {
		font-weight: 500;
		margin-bottom: 0.25rem;
	}

	.citation-snippet {
		font-size: 0.875rem;
		opacity: 0.8;
		line-height: 1.4;
	}

	.questions-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.question-chip {
		background: rgba(255, 255, 255, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.2);
		color: white;
		padding: 0.5rem 1rem;
		border-radius: 20px;
		cursor: pointer;
		transition: all 0.2s;
		font-size: 0.875rem;
	}

	.question-chip:hover {
		background: rgba(255, 255, 255, 0.2);
		transform: translateY(-1px);
	}

	.input-area {
		padding: 1rem 1.5rem;
		background: rgba(255, 255, 255, 0.1);
		border-top: 1px solid rgba(255, 255, 255, 0.2);
	}

	.file-upload-section {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.file-input {
		display: none;
	}

	.file-btn {
		background: rgba(255, 255, 255, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.2);
		color: white;
		padding: 0.5rem 1rem;
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s;
		font-size: 0.875rem;
	}

	.file-btn:hover {
		background: rgba(255, 255, 255, 0.2);
	}

	.selected-file {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		background: rgba(255, 255, 255, 0.1);
		padding: 0.5rem 1rem;
		border-radius: 6px;
		color: white;
		font-size: 0.875rem;
	}

	.remove-file {
		background: none;
		border: none;
		color: white;
		cursor: pointer;
		padding: 0;
		font-size: 0.75rem;
	}

	.message-input-container {
		display: flex;
		gap: 1rem;
		align-items: flex-end;
	}

	.message-input {
		flex: 1;
		background: rgba(255, 255, 255, 0.9);
		border: 1px solid rgba(255, 255, 255, 0.3);
		border-radius: 12px;
		padding: 1rem;
		font-size: 1rem;
		resize: vertical;
		min-height: 60px;
		max-height: 120px;
	}

	.message-input:focus {
		outline: none;
		border-color: rgba(255, 255, 255, 0.5);
		box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
	}

	.message-input:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.send-btn {
		background: linear-gradient(135deg, #10b981, #059669);
		border: none;
		color: white;
		padding: 1rem 1.5rem;
		border-radius: 12px;
		cursor: pointer;
		transition: all 0.2s;
		font-size: 1.2rem;
		min-width: 60px;
		height: 60px;
	}

	.send-btn:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
	}

	.send-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}

	/* Responsive Design */
	@media (max-width: 768px) {
		.perplexity-chat-container {
			height: 100vh;
			border-radius: 0;
		}

		.header-content {
			flex-direction: column;
			align-items: flex-start;
			gap: 0.5rem;
		}

		.header-content h2 {
			font-size: 1.25rem;
		}

		.quick-actions {
			flex-direction: column;
			align-items: center;
		}

		.quick-btn {
			width: 100%;
			max-width: 300px;
		}

		.message-content {
			max-width: 90%;
		}

		.file-upload-section {
			flex-direction: column;
			align-items: flex-start;
		}

		.message-input-container {
			flex-direction: column;
			gap: 0.5rem;
		}

		.send-btn {
			align-self: flex-end;
		}
	}
</style>
