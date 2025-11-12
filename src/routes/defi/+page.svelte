<script lang="ts">
	import { onMount } from 'svelte';
	import DeFiPositions from '$lib/components/DeFiPositions.svelte';
	import { getSmartMoneyHoldings, type SmartMoneyHolding } from '$lib/apis/nansen';
	import { toast } from 'svelte-sonner';

	// State for smart money
	let smartMoneyHoldings: SmartMoneyHolding[] = [];
	let isLoadingSmartMoney: boolean = false;
	let selectedChains: string[] = ['ethereum'];
	let availableChains = [
		{ id: 'ethereum', name: 'Ethereum' },
		{ id: 'solana', name: 'Solana' },
		{ id: 'base', name: 'Base' },
		{ id: 'arbitrum', name: 'Arbitrum' },
		{ id: 'polygon', name: 'Polygon' }
	];

	// Format USD
	function formatUSD(value: number): string {
		if (value >= 1000000000) {
			return `$${(value / 1000000000).toFixed(2)}B`;
		} else if (value >= 1000000) {
			return `$${(value / 1000000).toFixed(2)}M`;
		} else if (value >= 1000) {
			return `$${(value / 1000).toFixed(2)}K`;
		}
		return `$${value.toFixed(2)}`;
	}

	// Toggle chain selection
	function toggleChain(chainId: string) {
		if (selectedChains.includes(chainId)) {
			selectedChains = selectedChains.filter(c => c !== chainId);
		} else {
			selectedChains = [...selectedChains, chainId];
		}
	}

	// Load smart money holdings
	async function loadSmartMoney() {
		if (selectedChains.length === 0) {
			toast.error('Please select at least one chain');
			return;
		}

		isLoadingSmartMoney = true;

		try {
			const response = await getSmartMoneyHoldings({
				chains: selectedChains,
				page: 1,
				per_page: 50
			});

			if (response.success) {
				smartMoneyHoldings = response.data.holdings || [];
				toast.success(`Loaded ${smartMoneyHoldings.length} smart money holdings`);
			}
		} catch (err) {
			const errorMsg = err instanceof Error ? err.message : 'Unknown error';
			console.error('Error loading smart money:', err);
			toast.error(`Failed to load smart money: ${errorMsg}`);
		} finally {
			isLoadingSmartMoney = false;
		}
	}

	// Check API health on mount (silent)
	onMount(async () => {
		try {
			const health = await fetch('/api/tradeberg/nansen-health');
			const healthData = await health.json();
			if (!healthData.configured) {
				console.error('Nansen API not configured');
			} else {
				console.log('Nansen API ready');
			}
		} catch (err) {
			console.error('Health check failed:', err);
		}
	});
</script>

<svelte:head>
	<title>DeFi Positions - TradeBerg</title>
</svelte:head>

<div class="min-h-screen bg-gray-900 text-gray-100">
	<!-- Header -->
	<div class="border-b border-gray-800 bg-gray-900/50 backdrop-blur">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold text-white">DeFi Analytics</h1>
					<p class="mt-1 text-sm text-gray-400">Track wallet positions and smart money movements</p>
				</div>
				<a
					href="/"
					class="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors"
				>
					← Back to Chat
				</a>
			</div>
		</div>
	</div>

	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

		<!-- DeFi Positions Section -->
		<div class="mb-12">
			<DeFiPositions walletAddress="" autoLoad={false} />
		</div>

		<!-- Smart Money Section -->
		<div class="mt-12">
			<div class="mb-6">
				<h2 class="text-xl font-semibold text-gray-100 mb-2">Smart Money Holdings</h2>
				<p class="text-sm text-gray-400 mb-4">Top tokens held by institutional investors and funds</p>

				<!-- Chain Selector -->
				<div class="flex flex-wrap gap-2 mb-4">
					{#each availableChains as chain}
						<button
							on:click={() => toggleChain(chain.id)}
							class="px-4 py-2 rounded-lg font-medium transition-colors {selectedChains.includes(
								chain.id
							)
								? 'bg-blue-600 text-white'
								: 'bg-gray-800 text-gray-400 hover:bg-gray-700'}"
						>
							{chain.name}
						</button>
					{/each}
					<button
						on:click={loadSmartMoney}
						disabled={isLoadingSmartMoney || selectedChains.length === 0}
						class="ml-auto px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
					>
						{isLoadingSmartMoney ? 'Loading...' : 'Refresh'}
					</button>
				</div>
			</div>

			{#if isLoadingSmartMoney}
				<div class="flex items-center justify-center py-12">
					<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
				</div>
			{:else if smartMoneyHoldings.length > 0}
				<!-- Smart Money Table -->
				<div class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
					<div class="overflow-x-auto">
						<table class="w-full">
							<thead class="bg-gray-900">
								<tr>
									<th
										class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider"
									>
										Rank
									</th>
									<th
										class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider"
									>
										Token
									</th>
									<th
										class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider"
									>
										Chain
									</th>
									<th
										class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider"
									>
										Holders
									</th>
									<th
										class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider"
									>
										Total Value
									</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-gray-700">
								{#each smartMoneyHoldings as holding, index}
									<tr class="hover:bg-gray-750 transition-colors">
										<td class="px-4 py-3 text-sm text-gray-400">
											#{index + 1}
										</td>
										<td class="px-4 py-3">
											<div>
												<div class="text-sm font-medium text-gray-100">
													{holding.token_symbol}
												</div>
												<div class="text-xs text-gray-500">
													{holding.token_name}
												</div>
											</div>
										</td>
										<td class="px-4 py-3">
											<span
												class="px-2 py-1 text-xs font-medium bg-gray-700 text-gray-300 rounded"
											>
												{holding.chain}
											</span>
										</td>
										<td class="px-4 py-3 text-right text-sm text-gray-300">
											{holding.holders_count.toLocaleString()}
										</td>
										<td class="px-4 py-3 text-right text-sm font-medium text-green-400">
											{formatUSD(holding.total_value_usd)}
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>
			{:else}
				<div class="text-center py-12 text-gray-500">
					{#if smartMoneyHoldings.length === 0}
						<div class="text-lg mb-2">Click "Refresh" to load smart money holdings</div>
						<div class="text-sm">Select chains above and click Refresh</div>
					{:else}
						No smart money holdings found. Try selecting different chains.
					{/if}
				</div>
			{/if}
		</div>
	</div>
</div>
