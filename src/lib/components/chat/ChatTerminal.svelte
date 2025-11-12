<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, slide } from 'svelte/transition';

	export let visible = false;

	let terminalInput = '';
	let terminalOutput: Array<{ type: 'command' | 'output' | 'error'; text: string }> = [
		{
			type: 'output',
			text: '🚀 TradeBerg Terminal v1.0.0\nType "help" for available commands\n'
		}
	];
	let terminalContainer: HTMLDivElement;
	let inputElement: HTMLInputElement;

	// Available commands
	const commands: Record<string, (args: string[]) => string> = {
		help: () => {
			return `Available Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Financial Commands:
  price <symbol>          Get current price (e.g., price BTC)
  chart <symbol>          Generate chart data
  analyze <symbol>        Market analysis
  volume <symbol>         Volume analysis
  
🔧 System Commands:
  clear                   Clear terminal
  help                    Show this help message
  status                  System status
  version                 Show version
  
💡 Examples:
  price BTC
  chart ETH
  analyze SOL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`;
		},

		clear: () => {
			terminalOutput = [];
			return '';
		},

		version: () => {
			return 'TradeBerg Terminal v1.0.0\nBuild: 2024.01.15\nNode: v20.11.0';
		},

		status: () => {
			return `System Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ API Server:        Online
✅ WebSocket:         Connected
✅ Chart Engine:      Ready
✅ Data Sources:      Active
✅ AI Model:          Ready
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uptime: 2h 34m
Memory: 245 MB / 512 MB
CPU: 12%`;
		},

		price: (args) => {
			const symbol = args[0]?.toUpperCase() || 'BTC';
			const prices: Record<string, number> = {
				BTC: 44200,
				ETH: 2380,
				SOL: 108,
				AVAX: 38.5,
				MATIC: 0.92
			};
			const price = prices[symbol] || 0;
			if (price === 0) {
				return `❌ Error: Unknown symbol "${symbol}"`;
			}
			return `💰 ${symbol}/USDT: $${price.toLocaleString()}\n📈 24h Change: +5.2%\n📊 Volume: $52.4B`;
		},

		chart: (args) => {
			const symbol = args[0]?.toUpperCase() || 'BTC';
			return `📊 Generating chart for ${symbol}...\n\n\`\`\`json:chart:candlestick
{
  "title": "${symbol}/USDT Price Chart",
  "data": [...],
  "annotations": [...]
}
\`\`\`\n\n✅ Chart data generated! Copy the JSON block above to see the chart.`;
		},

		analyze: (args) => {
			const symbol = args[0]?.toUpperCase() || 'BTC';
			return `🔍 Market Analysis for ${symbol}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Trend:           Bullish
💪 Strength:        Strong (8/10)
📊 Volume:          Above Average (+45%)
🎯 Support:         $43,000
🚧 Resistance:      $45,000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recommendation:     BUY on pullback
Entry Zone:         $43,000 - $43,200
Stop Loss:          $42,700
Take Profit:        $45,000
Risk/Reward:        1:4 ⭐⭐⭐⭐`;
		},

		volume: (args) => {
			const symbol = args[0]?.toUpperCase() || 'BTC';
			return `📊 Volume Analysis for ${symbol}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
24h Volume:         $52.4B
Buy Volume:         $28.5B (54%)
Sell Volume:        $15.2B (29%)
Neutral:            $8.7B (17%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status:             🟢 Strong Buy Pressure`;
		}
	};

	function executeCommand(cmd: string) {
		const trimmedCmd = cmd.trim();
		if (!trimmedCmd) return;

		// Add command to output
		terminalOutput = [...terminalOutput, { type: 'command', text: `$ ${trimmedCmd}` }];

		// Parse command
		const parts = trimmedCmd.split(' ');
		const command = parts[0].toLowerCase();
		const args = parts.slice(1);

		// Execute command
		if (commands[command]) {
			const result = commands[command](args);
			if (result) {
				terminalOutput = [...terminalOutput, { type: 'output', text: result }];
			}
		} else {
			terminalOutput = [
				...terminalOutput,
				{ type: 'error', text: `❌ Command not found: "${command}"\nType "help" for available commands.` }
			];
		}

		// Clear input
		terminalInput = '';

		// Scroll to bottom
		setTimeout(() => {
			if (terminalContainer) {
				terminalContainer.scrollTop = terminalContainer.scrollHeight;
			}
		}, 10);
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Enter') {
			executeCommand(terminalInput);
		} else if (e.key === 'Escape') {
			visible = false;
		}
	}

	onMount(() => {
		if (visible && inputElement) {
			inputElement.focus();
		}
	});

	$: if (visible && inputElement) {
		setTimeout(() => inputElement.focus(), 100);
	}
</script>

{#if visible}
	<div
		class="fixed bottom-0 left-0 right-0 z-50 bg-gray-950 border-t border-gray-800 shadow-2xl"
		transition:slide={{ duration: 200 }}
	>
		<!-- Terminal Header -->
		<div
			class="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-800"
		>
			<div class="flex items-center gap-3">
				<span class="text-lg">💻</span>
				<span class="font-semibold text-sm">TradeBerg Terminal</span>
				<span class="text-xs text-gray-500">Press ESC to close</span>
			</div>
			<div class="flex items-center gap-2">
				<div class="flex gap-1">
					<div class="w-3 h-3 rounded-full bg-green-500"></div>
					<div class="w-3 h-3 rounded-full bg-yellow-500"></div>
					<div class="w-3 h-3 rounded-full bg-red-500"></div>
				</div>
				<button
					on:click={() => (visible = false)}
					class="ml-2 px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700 rounded transition-colors"
				>
					Close
				</button>
			</div>
		</div>

		<!-- Terminal Content -->
		<div
			bind:this={terminalContainer}
			class="h-96 overflow-y-auto p-4 font-mono text-sm bg-gray-950 text-green-400"
			style="scrollbar-width: thin;"
		>
			{#each terminalOutput as line}
				<div
					class="mb-2 {line.type === 'command'
						? 'text-blue-400'
						: line.type === 'error'
							? 'text-red-400'
							: 'text-green-400'}"
				>
					<pre class="whitespace-pre-wrap font-mono">{line.text}</pre>
				</div>
			{/each}

			<!-- Input Line -->
			<div class="flex items-center gap-2 mt-2">
				<span class="text-blue-400">$</span>
				<input
					bind:this={inputElement}
					bind:value={terminalInput}
					on:keydown={handleKeyDown}
					type="text"
					class="flex-1 bg-transparent outline-none text-green-400 font-mono"
					placeholder="Type a command..."
					autocomplete="off"
					spellcheck="false"
				/>
			</div>
		</div>

		<!-- Quick Commands -->
		<div class="px-4 py-2 bg-gray-900 border-t border-gray-800 flex gap-2 overflow-x-auto">
			<button
				on:click={() => executeCommand('help')}
				class="px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700 rounded transition-colors whitespace-nowrap"
			>
				📚 help
			</button>
			<button
				on:click={() => executeCommand('status')}
				class="px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700 rounded transition-colors whitespace-nowrap"
			>
				📊 status
			</button>
			<button
				on:click={() => executeCommand('price BTC')}
				class="px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700 rounded transition-colors whitespace-nowrap"
			>
				💰 price BTC
			</button>
			<button
				on:click={() => executeCommand('analyze ETH')}
				class="px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700 rounded transition-colors whitespace-nowrap"
			>
				🔍 analyze ETH
			</button>
			<button
				on:click={() => executeCommand('clear')}
				class="px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700 rounded transition-colors whitespace-nowrap"
			>
				🗑️ clear
			</button>
		</div>
	</div>
{/if}

<style>
	/* Custom scrollbar for terminal */
	div::-webkit-scrollbar {
		width: 8px;
	}

	div::-webkit-scrollbar-track {
		background: #111827;
	}

	div::-webkit-scrollbar-thumb {
		background: #374151;
		border-radius: 4px;
	}

	div::-webkit-scrollbar-thumb:hover {
		background: #4b5563;
	}
</style>
