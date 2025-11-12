<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { writable } from 'svelte/store';

	// Chat state
	let messages = writable<Array<{role: string, content: string, timestamp: Date}>>([]);
	let chatId = '';
	let chatFound = false;
	let loading = true;

	onMount(() => {
		chatId = $page.params.id;
		loadSharedChat();
	});

	function loadSharedChat() {
		try {
			// Try to load from localStorage first
			const savedChat = localStorage.getItem(`chat_${chatId}`);
			
			if (savedChat) {
				const parsedMessages = JSON.parse(savedChat);
				// Convert timestamp strings back to Date objects
				const messagesWithDates = parsedMessages.map((msg: any) => ({
					...msg,
					timestamp: new Date(msg.timestamp)
				}));
				
				messages.set(messagesWithDates);
				chatFound = true;
			} else {
				// In a real app, you'd fetch from a database here
				chatFound = false;
			}
		} catch (error) {
			console.error('Error loading shared chat:', error);
			chatFound = false;
		} finally {
			loading = false;
		}
	}

	function shareOnWhatsApp() {
		const text = `Check out this TradeBerg market analysis: ${window.location.href}`;
		const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(text)}`;
		window.open(whatsappUrl, '_blank');
	}

	function copyLink() {
		navigator.clipboard.writeText(window.location.href);
		alert('Link copied to clipboard!');
	}
</script>

<svelte:head>
	<title>Shared TradeBerg Chat - {chatId}</title>
	<meta name="description" content="TradeBerg market analysis chat shared by a user" />
</svelte:head>

<div class="shared-chat-container">
	{#if loading}
		<div class="loading">
			<h2>🔄 Loading shared chat...</h2>
		</div>
	{:else if !chatFound}
		<div class="not-found">
			<h2>❌ Chat Not Found</h2>
			<p>This shared chat link is invalid or has expired.</p>
			<a href="/tradeberg-chat" class="start-new-chat">🚀 Start New Chat</a>
		</div>
	{:else}
		<header class="shared-header">
			<h1>📤 Shared TradeBerg Analysis</h1>
			<div class="share-actions">
				<button on:click={shareOnWhatsApp} class="whatsapp-share">
					📱 Share on WhatsApp
				</button>
				<button on:click={copyLink} class="copy-link">
					📋 Copy Link
				</button>
				<a href="/tradeberg-chat" class="start-new-chat">🚀 Start New Chat</a>
			</div>
		</header>

		<div class="shared-messages">
			{#each $messages as message}
				<div class="message {message.role}">
					<div class="message-content">
						{@html message.content.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
					</div>
					<div class="message-time">
						{message.timestamp.toLocaleString()}
					</div>
				</div>
			{/each}
		</div>

		<footer class="shared-footer">
			<div class="branding">
				<h3>🚀 TradeBerg Enhanced Chat</h3>
				<p>Professional market analysis with real-time data</p>
				<a href="/tradeberg-chat" class="cta-button">Try TradeBerg Chat</a>
			</div>
		</footer>
	{/if}
</div>

<style>
	.shared-chat-container {
		max-width: 1000px;
		margin: 0 auto;
		min-height: 100vh;
		background: #0a0a0a;
		color: #ffffff;
	}

	.loading, .not-found {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		text-align: center;
		padding: 2rem;
	}

	.not-found h2 {
		color: #ff6b6b;
		margin-bottom: 1rem;
	}

	.shared-header {
		background: linear-gradient(135deg, #1a1a2e, #16213e);
		padding: 2rem;
		text-align: center;
		border-bottom: 2px solid #00ff88;
	}

	.shared-header h1 {
		color: #00ff88;
		margin: 0 0 1rem 0;
		font-size: 2rem;
	}

	.share-actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
	}

	.whatsapp-share {
		background: #25d366;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 10px;
		cursor: pointer;
		font-weight: bold;
		transition: all 0.3s;
	}

	.copy-link {
		background: #666;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 10px;
		cursor: pointer;
		font-weight: bold;
		transition: all 0.3s;
	}

	.start-new-chat {
		background: #00ff88;
		color: #000;
		text-decoration: none;
		padding: 0.75rem 1.5rem;
		border-radius: 10px;
		font-weight: bold;
		transition: all 0.3s;
		display: inline-block;
	}

	.whatsapp-share:hover, .copy-link:hover, .start-new-chat:hover {
		transform: translateY(-2px);
		opacity: 0.9;
	}

	.shared-messages {
		padding: 2rem;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		min-height: 60vh;
	}

	.message {
		display: flex;
		flex-direction: column;
		max-width: 80%;
	}

	.message.user {
		align-self: flex-end;
	}

	.message.assistant {
		align-self: flex-start;
	}

	.message-content {
		padding: 1.5rem;
		border-radius: 15px;
		line-height: 1.6;
		font-size: 1rem;
	}

	.message.user .message-content {
		background: #00ff88;
		color: #000;
		border-bottom-right-radius: 5px;
	}

	.message.assistant .message-content {
		background: #222;
		color: #fff;
		border: 1px solid #444;
		border-bottom-left-radius: 5px;
	}

	.message-time {
		font-size: 0.9rem;
		color: #888;
		margin-top: 0.5rem;
		align-self: flex-end;
	}

	.shared-footer {
		background: #111;
		padding: 3rem 2rem;
		text-align: center;
		border-top: 1px solid #333;
		margin-top: 2rem;
	}

	.branding h3 {
		color: #00ff88;
		margin: 0 0 1rem 0;
		font-size: 1.8rem;
	}

	.branding p {
		color: #ccc;
		margin: 0 0 2rem 0;
		font-size: 1.1rem;
	}

	.cta-button {
		background: linear-gradient(135deg, #00ff88, #00cc6a);
		color: #000;
		text-decoration: none;
		padding: 1rem 2rem;
		border-radius: 10px;
		font-weight: bold;
		font-size: 1.1rem;
		display: inline-block;
		transition: all 0.3s;
	}

	.cta-button:hover {
		transform: translateY(-3px);
		box-shadow: 0 10px 20px rgba(0, 255, 136, 0.3);
	}

	/* Responsive */
	@media (max-width: 768px) {
		.shared-header {
			padding: 1.5rem 1rem;
		}
		
		.shared-header h1 {
			font-size: 1.5rem;
		}
		
		.share-actions {
			flex-direction: column;
			align-items: center;
		}
		
		.shared-messages {
			padding: 1rem;
		}
		
		.message {
			max-width: 95%;
		}
		
		.shared-footer {
			padding: 2rem 1rem;
		}
	}
</style>
