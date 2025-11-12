<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getUserCredits, purchaseCredits, getCreditTransactions, type CreditTransaction } from '$lib/apis/user-management';
	
	let credits = 0;
	let totalPurchased = 0;
	let totalUsed = 0;
	let transactions: CreditTransaction[] = [];
	let loading = true;
	let purchasing = false;
	let error = '';
	
	// Credit packages
	const packages = [
		{ name: 'Starter', credits: 100, price: 15.00, popular: false },
		{ name: 'Pro', credits: 500, price: 60.00, popular: true },
		{ name: 'Enterprise', credits: 2000, price: 200.00, popular: false }
	];
	
	onMount(async () => {
		await loadCredits();
		await loadTransactions();
	});
	
	async function loadCredits() {
		loading = true;
		try {
			const token = localStorage.getItem('token');
			if (!token) {
				goto('/');
				return;
			}
			
			try {
				const data = await getUserCredits(token);
				credits = data.credits;
				totalPurchased = data.total_purchased;
				totalUsed = data.total_used;
			} catch (apiError) {
				console.warn('API not available, using fallback:', apiError);
				// Use fallback data
				credits = 0;
				totalPurchased = 0;
				totalUsed = 0;
				error = 'Credits system will be available after database sync. You can still purchase credits below.';
			}
		} catch (e: any) {
			error = e.message;
			console.error('Error loading credits:', e);
		} finally {
			loading = false;
		}
	}
	
	async function loadTransactions() {
		try {
			const token = localStorage.getItem('token');
			if (!token) return;
			
			const data = await getCreditTransactions(token, 20);
			transactions = data.transactions;
		} catch (e: any) {
			console.error('Error loading transactions:', e);
		}
	}
	
	async function buyCredits(pkg: typeof packages[0]) {
		purchasing = true;
		try {
			const token = localStorage.getItem('token');
			if (!token) {
				goto('/');
				return;
			}
			
			const baseUrl = window.location.origin;
			const data = await purchaseCredits(token, {
				amount: pkg.price,
				credits: pkg.credits,
				success_url: `${baseUrl}/credits/success`,
				cancel_url: `${baseUrl}/credits`
			});
			
			// Redirect to Stripe checkout
			window.location.href = data.checkout_url;
		} catch (e: any) {
			error = e.message;
			purchasing = false;
		}
	}
	
	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
	
	function getTransactionIcon(type: string): string {
		switch (type) {
			case 'purchase': return '💳';
			case 'usage': return '📉';
			case 'refund': return '↩️';
			case 'bonus': return '🎁';
			case 'admin_adjustment': return '⚙️';
			default: return '•';
		}
	}
	
	function getTransactionColor(type: string): string {
		switch (type) {
			case 'purchase': return 'text-green-600 dark:text-green-400';
			case 'usage': return 'text-red-600 dark:text-red-400';
			case 'refund': return 'text-blue-600 dark:text-blue-400';
			case 'bonus': return 'text-purple-600 dark:text-purple-400';
			default: return 'text-gray-600 dark:text-gray-400';
		}
	}
</script>

<svelte:head>
	<title>Credits - TradeBerg</title>
</svelte:head>

<div class="max-w-6xl mx-auto p-6">
	<div class="flex items-center gap-4 mb-6">
		<button
			on:click={() => window.history.back()}
			class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
			title="Go back"
		>
			<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
		</button>
		<h1 class="text-3xl font-bold">Credits</h1>
	</div>
	
	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
			{error}
		</div>
	{/if}
	
	{#if loading}
		<div class="text-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
			<p class="mt-4 text-gray-600 dark:text-gray-400">Loading credits...</p>
		</div>
	{:else}
		<!-- Current Balance -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
			<div class="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg shadow-lg p-6">
				<div class="text-sm opacity-90 mb-2">Available Credits</div>
				<div class="text-4xl font-bold">{credits}</div>
			</div>
			
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
				<div class="text-sm text-gray-500 dark:text-gray-400 mb-2">Total Purchased</div>
				<div class="text-3xl font-bold text-green-600 dark:text-green-400">{totalPurchased}</div>
			</div>
			
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
				<div class="text-sm text-gray-500 dark:text-gray-400 mb-2">Total Used</div>
				<div class="text-3xl font-bold text-orange-600 dark:text-orange-400">{totalUsed}</div>
			</div>
		</div>
		
		<!-- Credit Packages -->
		<div class="mb-8">
			<h2 class="text-2xl font-bold mb-4">Buy Credits</h2>
			
			<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
				{#each packages as pkg}
					<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 relative {pkg.popular ? 'ring-2 ring-blue-600' : ''}">
						{#if pkg.popular}
							<div class="absolute top-0 right-0 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-bl-lg rounded-tr-lg">
								POPULAR
							</div>
						{/if}
						
						<div class="text-center">
							<h3 class="text-xl font-bold mb-2">{pkg.name}</h3>
							<div class="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
								{pkg.credits}
							</div>
							<div class="text-sm text-gray-500 dark:text-gray-400 mb-4">Credits</div>
							
							<div class="text-3xl font-bold mb-1">
								${pkg.price.toFixed(2)}
							</div>
							<div class="text-sm text-gray-500 dark:text-gray-400 mb-6">
								${(pkg.price / pkg.credits).toFixed(3)} per credit
							</div>
							
							<button
								on:click={() => buyCredits(pkg)}
								disabled={purchasing}
								class="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
							>
								{purchasing ? 'Processing...' : 'Buy Now'}
							</button>
						</div>
					</div>
				{/each}
			</div>
		</div>
		
		<!-- Transaction History -->
		<div class="bg-white dark:bg-gray-800 rounded-lg shadow">
			<div class="p-6 border-b border-gray-200 dark:border-gray-700">
				<h2 class="text-xl font-bold">Recent Transactions</h2>
			</div>
			
			<div class="p-6">
				{#if transactions.length === 0}
					<div class="text-center py-8 text-gray-500 dark:text-gray-400">
						No transactions yet
					</div>
				{:else}
					<div class="space-y-3">
						{#each transactions as transaction}
							<div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
								<div class="flex items-center gap-3">
									<span class="text-2xl">{getTransactionIcon(transaction.transaction_type)}</span>
									<div>
										<div class="font-medium capitalize">{transaction.transaction_type.replace('_', ' ')}</div>
										{#if transaction.description}
											<div class="text-sm text-gray-500 dark:text-gray-400">{transaction.description}</div>
										{/if}
										<div class="text-xs text-gray-400 dark:text-gray-500">{formatDate(transaction.created_at)}</div>
									</div>
								</div>
								
								<div class="text-right">
									<div class="font-bold {getTransactionColor(transaction.transaction_type)}">
										{transaction.amount > 0 ? '+' : ''}{transaction.amount}
									</div>
									<div class="text-sm text-gray-500 dark:text-gray-400">
										Balance: {transaction.balance_after}
									</div>
								</div>
							</div>
						{/each}
					</div>
					
					<button
						on:click={() => goto('/transactions')}
						class="w-full mt-4 px-4 py-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition"
					>
						View All Transactions
					</button>
				{/if}
			</div>
		</div>
	{/if}
</div>
