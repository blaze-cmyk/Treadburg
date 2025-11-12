<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	
	// Admin Dashboard State
	let stats = {
		total_users: 0,
		total_revenue: 0,
		active_subscriptions: 0,
		new_users_this_week: 0
	};
	
	let users: any[] = [];
	let payments: any[] = [];
	let loading = true;
	let error = '';
	let selectedTab = 'overview';
	let searchQuery = '';
	
	// Check if user is admin
	let isAdmin = false;
	let currentUser: any = null;
	
	onMount(async () => {
		await checkAdminAccess();
		if (isAdmin) {
			await loadDashboardData();
		}
	});
	
	async function checkAdminAccess() {
		try {
			const token = localStorage.getItem('token');
			if (!token) {
				goto('/login');
				return;
			}
			
			const response = await fetch('/api/user-management/profile', {
				headers: {
					'Authorization': `Bearer ${token}`
				}
			});
			
			if (response.ok) {
				const data = await response.json();
				currentUser = data.user;
				isAdmin = data.user.is_admin;
				
				if (!isAdmin) {
					error = 'Access denied. Admin privileges required.';
					setTimeout(() => goto('/'), 3000);
				}
			} else {
				goto('/login');
			}
		} catch (e) {
			console.error('Auth check failed:', e);
			goto('/login');
		}
	}
	
	async function loadDashboardData() {
		loading = true;
		try {
			const token = localStorage.getItem('token');
			
			// Load stats
			const statsResponse = await fetch('/api/user-management/admin/stats', {
				headers: { 'Authorization': `Bearer ${token}` }
			});
			if (statsResponse.ok) {
				const statsData = await statsResponse.json();
				stats = statsData.stats;
			}
			
			// Load users
			const usersResponse = await fetch('/api/user-management/admin/users?limit=100', {
				headers: { 'Authorization': `Bearer ${token}` }
			});
			if (usersResponse.ok) {
				const usersData = await usersResponse.json();
				users = usersData.users;
			}
			
		} catch (e) {
			error = 'Failed to load dashboard data';
			console.error(e);
		} finally {
			loading = false;
		}
	}
	
	async function adjustUserCredits(userId: string, amount: number, description: string) {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/user-management/admin/users/${userId}/credits`, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ amount, description })
			});
			
			if (response.ok) {
				alert('Credits adjusted successfully');
				await loadDashboardData();
			} else {
				alert('Failed to adjust credits');
			}
		} catch (e) {
			console.error('Error adjusting credits:', e);
			alert('Error adjusting credits');
		}
	}
	
	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(amount);
	}
	
	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
	
	$: filteredUsers = users.filter(user => 
		user.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
		user.username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
		user.full_name?.toLowerCase().includes(searchQuery.toLowerCase())
	);
</script>

<svelte:head>
	<title>Admin Dashboard - TradeBerg</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<!-- Header -->
	<header class="bg-white dark:bg-gray-800 shadow">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
			<div class="flex justify-between items-center">
				<h1 class="text-3xl font-bold text-gray-900 dark:text-white">
					🛡️ Admin Dashboard
				</h1>
				<div class="flex items-center gap-4">
					<span class="text-sm text-gray-600 dark:text-gray-400">
						{currentUser?.email}
					</span>
					<button
						on:click={() => goto('/')}
						class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
					>
						Back to App
					</button>
				</div>
			</div>
		</div>
	</header>

	{#if !isAdmin}
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
			<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
				{error || 'Checking permissions...'}
			</div>
		</div>
	{:else if loading}
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
			<div class="text-center">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
				<p class="mt-4 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
			</div>
		</div>
	{:else}
		<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
			<!-- Stats Cards -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm text-gray-600 dark:text-gray-400">Total Users</p>
							<p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">
								{stats.total_users.toLocaleString()}
							</p>
						</div>
						<div class="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
							<svg class="w-8 h-8 text-blue-600 dark:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
							</svg>
						</div>
					</div>
					<p class="text-sm text-green-600 dark:text-green-400 mt-2">
						+{stats.new_users_this_week} this week
					</p>
				</div>

				<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm text-gray-600 dark:text-gray-400">Total Revenue</p>
							<p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">
								{formatCurrency(stats.total_revenue)}
							</p>
						</div>
						<div class="p-3 bg-green-100 dark:bg-green-900 rounded-full">
							<svg class="w-8 h-8 text-green-600 dark:text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
						</div>
					</div>
				</div>

				<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm text-gray-600 dark:text-gray-400">Active Subscriptions</p>
							<p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">
								{stats.active_subscriptions.toLocaleString()}
							</p>
						</div>
						<div class="p-3 bg-purple-100 dark:bg-purple-900 rounded-full">
							<svg class="w-8 h-8 text-purple-600 dark:text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
						</div>
					</div>
				</div>

				<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm text-gray-600 dark:text-gray-400">Avg Revenue/User</p>
							<p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">
								{formatCurrency(stats.total_users > 0 ? stats.total_revenue / stats.total_users : 0)}
							</p>
						</div>
						<div class="p-3 bg-yellow-100 dark:bg-yellow-900 rounded-full">
							<svg class="w-8 h-8 text-yellow-600 dark:text-yellow-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
							</svg>
						</div>
					</div>
				</div>
			</div>

			<!-- Tabs -->
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow mb-6">
				<div class="border-b border-gray-200 dark:border-gray-700">
					<nav class="flex -mb-px">
						<button
							on:click={() => selectedTab = 'overview'}
							class="px-6 py-3 text-sm font-medium border-b-2 {selectedTab === 'overview' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						>
							Overview
						</button>
						<button
							on:click={() => selectedTab = 'users'}
							class="px-6 py-3 text-sm font-medium border-b-2 {selectedTab === 'users' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						>
							Users ({users.length})
						</button>
						<button
							on:click={() => selectedTab = 'payments'}
							class="px-6 py-3 text-sm font-medium border-b-2 {selectedTab === 'payments' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
						>
							Payments
						</button>
					</nav>
				</div>

				<!-- Tab Content -->
				<div class="p-6">
					{#if selectedTab === 'users'}
						<!-- Users Tab -->
						<div class="mb-4">
							<input
								type="text"
								bind:value={searchQuery}
								placeholder="Search users by email, username, or name..."
								class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
							/>
						</div>

						<div class="overflow-x-auto">
							<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
								<thead class="bg-gray-50 dark:bg-gray-900">
									<tr>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">User</th>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Credits</th>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Subscription</th>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total Spent</th>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Joined</th>
										<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
									</tr>
								</thead>
								<tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
									{#each filteredUsers as user}
										<tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
											<td class="px-6 py-4 whitespace-nowrap">
												<div class="flex items-center">
													<div class="flex-shrink-0 h-10 w-10">
														{#if user.avatar_url}
															<img class="h-10 w-10 rounded-full" src={user.avatar_url} alt="" />
														{:else}
															<div class="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
																{user.email?.[0]?.toUpperCase() || '?'}
															</div>
														{/if}
													</div>
													<div class="ml-4">
														<div class="text-sm font-medium text-gray-900 dark:text-white">
															{user.full_name || user.username || 'No name'}
														</div>
														<div class="text-sm text-gray-500 dark:text-gray-400">
															{user.email}
														</div>
													</div>
												</div>
											</td>
											<td class="px-6 py-4 whitespace-nowrap">
												<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
													{user.credits || 0} credits
												</span>
											</td>
											<td class="px-6 py-4 whitespace-nowrap">
												<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {user.subscription_status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
													{user.subscription_tier || 'free'}
												</span>
											</td>
											<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
												{formatCurrency(user.total_spent || 0)}
											</td>
											<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
												{formatDate(user.created_at)}
											</td>
											<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
												<button
													on:click={() => {
														const amount = prompt('Enter credit amount (positive to add, negative to remove):');
														if (amount) {
															const description = prompt('Enter description:') || 'Admin adjustment';
															adjustUserCredits(user.id, parseInt(amount), description);
														}
													}}
													class="text-blue-600 hover:text-blue-900 dark:text-blue-400"
												>
													Adjust Credits
												</button>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					{:else if selectedTab === 'overview'}
						<!-- Overview Tab -->
						<div class="space-y-6">
							<div>
								<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Platform Overview</h3>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div class="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
										<p class="text-sm text-gray-600 dark:text-gray-400">Total Users</p>
										<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_users}</p>
									</div>
									<div class="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
										<p class="text-sm text-gray-600 dark:text-gray-400">Total Revenue</p>
										<p class="text-2xl font-bold text-gray-900 dark:text-white">{formatCurrency(stats.total_revenue)}</p>
									</div>
								</div>
							</div>

							<div>
								<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Users</h3>
								<div class="space-y-2">
									{#each users.slice(0, 5) as user}
										<div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
											<div class="flex items-center">
												<div class="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-bold">
													{user.email?.[0]?.toUpperCase() || '?'}
												</div>
												<div class="ml-3">
													<p class="text-sm font-medium text-gray-900 dark:text-white">{user.email}</p>
													<p class="text-xs text-gray-500 dark:text-gray-400">{formatDate(user.created_at)}</p>
												</div>
											</div>
											<span class="text-sm text-gray-600 dark:text-gray-400">{user.credits} credits</span>
										</div>
									{/each}
								</div>
							</div>
						</div>
					{:else if selectedTab === 'payments'}
						<!-- Payments Tab -->
						<div class="text-center py-8 text-gray-500 dark:text-gray-400">
							Payment history will be displayed here
						</div>
					{/if}
				</div>
			</div>
		</main>
	{/if}
</div>

<style>
	/* Add any custom styles here */
</style>
