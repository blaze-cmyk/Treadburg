<script lang="ts">
	import { onMount } from 'svelte';
	import { getDeFiHoldings, type DeFiHolding } from '$lib/apis/nansen';
	import { toast } from 'svelte-sonner';

	// Props
	export let walletAddress: string = '';
	export let autoLoad: boolean = false;

	// State
	let holdings: DeFiHolding[] = [];
	let totalValue: number = 0;
	let chains: string[] = [];
	let isLoading: boolean = false;
	let error: string | null = null;

	// Format USD value
	function formatUSD(value: number): string {
		if (value >= 1000000) {
			return `$${(value / 1000000).toFixed(2)}M`;
		} else if (value >= 1000) {
			return `$${(value / 1000).toFixed(2)}K`;
		}
		return `$${value.toFixed(2)}`;
	}

	// Format balance
	function formatBalance(balance: string): string {
		const num = parseFloat(balance);
		if (num >= 1000000) {
			return `${(num / 1000000).toFixed(2)}M`;
		} else if (num >= 1000) {
			return `${(num / 1000).toFixed(2)}K`;
		} else if (num >= 1) {
			return num.toFixed(2);
		}
		return num.toFixed(6);
	}

	// Load DeFi positions
	async function loadPositions() {
		if (!walletAddress.trim()) {
			error = 'Please enter a wallet address';
			return;
		}

		isLoading = true;
		error = null;

		try {
			const response = await getDeFiHoldings({ wallet_address: walletAddress });
			
			if (response.success) {
				holdings = response.data.holdings || [];
				totalValue = response.data.total_value_usd || 0;
				chains = response.data.chains || [];
				
				toast.success(`Loaded ${holdings.length} positions`);
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load positions';
			toast.error(error);
			console.error('Error loading DeFi positions:', err);
		} finally {
			isLoading = false;
		}
	}

	// Handle enter key
	function handleKeyDown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			loadPositions();
		}
	}

	// Auto-load on mount if enabled
	onMount(() => {
		if (autoLoad && walletAddress) {
			loadPositions();
		}
	});
</script>

<div class="defi-positions w-full">
	<!-- Header -->
	<div class="mb-4">
		<h2 class="text-xl font-semibold text-gray-100 mb-2">DeFi Positions</h2>
		<p class="text-sm text-gray-400">View wallet holdings across multiple chains</p>
	</div>

	<!-- Wallet Input -->
	<div class="mb-6 flex gap-2">
		<input
			type="text"
			bind:value={walletAddress}
			on:keydown={handleKeyDown}
			placeholder="Enter wallet address (0x...)"
			class="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500"
		/>
		<button
			on:click={loadPositions}
			disabled={isLoading || !walletAddress.trim()}
			class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
		>
			{isLoading ? 'Loading...' : 'Load'}
		</button>
	</div>

	<!-- Error Message -->
	{#if error}
		<div class="mb-4 p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-400">
			{error}
		</div>
	{/if}

	<!-- Loading State -->
	{#if isLoading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
		</div>
	{/if}

	<!-- Holdings Summary -->
	{#if !isLoading && holdings.length > 0}
		<div class="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
			<div class="p-4 bg-gray-800 rounded-lg border border-gray-700">
				<div class="text-sm text-gray-400 mb-1">Total Value</div>
				<div class="text-2xl font-bold text-green-400">{formatUSD(totalValue)}</div>
			</div>
			<div class="p-4 bg-gray-800 rounded-lg border border-gray-700">
				<div class="text-sm text-gray-400 mb-1">Positions</div>
				<div class="text-2xl font-bold text-blue-400">{holdings.length}</div>
			</div>
			<div class="p-4 bg-gray-800 rounded-lg border border-gray-700">
				<div class="text-sm text-gray-400 mb-1">Chains</div>
				<div class="text-2xl font-bold text-purple-400">{chains.length}</div>
			</div>
		</div>

		<!-- Holdings Table -->
		<div class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead class="bg-gray-900">
						<tr>
							<th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
								Token
							</th>
							<th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
								Chain
							</th>
							<th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
								Balance
							</th>
							<th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
								Value (USD)
							</th>
							<th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
								Protocol
							</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-700">
						{#each holdings as holding}
							<tr class="hover:bg-gray-750 transition-colors">
								<td class="px-4 py-3">
									<div class="flex items-center">
										<div>
											<div class="text-sm font-medium text-gray-100">
												{holding.token_symbol}
											</div>
											<div class="text-xs text-gray-500">
												{holding.token_name}
											</div>
										</div>
									</div>
								</td>
								<td class="px-4 py-3">
									<span class="px-2 py-1 text-xs font-medium bg-gray-700 text-gray-300 rounded">
										{holding.chain}
									</span>
								</td>
								<td class="px-4 py-3 text-right text-sm text-gray-300">
									{formatBalance(holding.balance)}
								</td>
								<td class="px-4 py-3 text-right text-sm font-medium text-green-400">
									{formatUSD(holding.value_usd)}
								</td>
								<td class="px-4 py-3 text-sm text-gray-400">
									{holding.protocol || '-'}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}

	<!-- Empty State -->
	{#if !isLoading && !error && holdings.length === 0 && walletAddress}
		<div class="text-center py-12 text-gray-500">
			No positions found for this wallet
		</div>
	{/if}
</div>

<style>
	.defi-positions {
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
	}
</style>
