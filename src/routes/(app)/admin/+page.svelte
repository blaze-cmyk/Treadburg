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
				goto('/');
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
				goto('/');
			}
		} catch (e) {
			console.error('Auth check failed:', e);
			goto('/');
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

{#if !isAdmin && !loading}
	<div class="p-8">
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
			{error || 'Checking permissions...'}
		</div>
	</div>
{:else if loading}
	<div class="p-8 text-center">
		<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
		<p class="mt-4">Loading dashboard...</p>
	</div>
{:else}
	<div class="p-6">
		<h1 class="text-3xl font-bold mb-6">🛡️ Admin Dashboard</h1>
		
		<!-- Stats Cards -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
				<p class="text-sm text-gray-600 dark:text-gray-400">Total Users</p>
				<p class="text-3xl font-bold mt-2">{stats.total_users}</p>
				<p class="text-sm text-green-600 mt-2">+{stats.new_users_this_week} this week</p>
			</div>
			
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
				<p class="text-sm text-gray-600 dark:text-gray-400">Total Revenue</p>
				<p class="text-3xl font-bold mt-2">{formatCurrency(stats.total_revenue)}</p>
			</div>
			
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
				<p class="text-sm text-gray-600 dark:text-gray-400">Active Subscriptions</p>
				<p class="text-3xl font-bold mt-2">{stats.active_subscriptions}</p>
			</div>
			
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
				<p class="text-sm text-gray-600 dark:text-gray-400">Avg Revenue/User</p>
				<p class="text-3xl font-bold mt-2">
					{formatCurrency(stats.total_users > 0 ? stats.total_revenue / stats.total_users : 0)}
				</p>
			</div>
		</div>
		
		<!-- Users Table -->
		<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
			<h2 class="text-xl font-bold mb-4">Users</h2>
			
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Search users..."
				class="w-full px-4 py-2 border rounded-lg mb-4"
			/>
			
			<div class="overflow-x-auto">
				<table class="min-w-full">
					<thead>
						<tr class="border-b">
							<th class="px-4 py-2 text-left">User</th>
							<th class="px-4 py-2 text-left">Credits</th>
							<th class="px-4 py-2 text-left">Subscription</th>
							<th class="px-4 py-2 text-left">Total Spent</th>
							<th class="px-4 py-2 text-left">Joined</th>
							<th class="px-4 py-2 text-left">Actions</th>
						</tr>
					</thead>
					<tbody>
						{#each filteredUsers as user}
							<tr class="border-b hover:bg-gray-50 dark:hover:bg-gray-700">
								<td class="px-4 py-3">
									<div class="font-medium">{user.full_name || user.username || 'No name'}</div>
									<div class="text-sm text-gray-500">{user.email}</div>
								</td>
								<td class="px-4 py-3">
									<span class="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
										{user.credits || 0} credits
									</span>
								</td>
								<td class="px-4 py-3">
									<span class="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm">
										{user.subscription_tier || 'free'}
									</span>
								</td>
								<td class="px-4 py-3">{formatCurrency(user.total_spent || 0)}</td>
								<td class="px-4 py-3 text-sm">{formatDate(user.created_at)}</td>
								<td class="px-4 py-3">
									<button
										on:click={() => {
											const amount = prompt('Enter credit amount (positive to add, negative to remove):');
											if (amount) {
												const description = prompt('Enter description:') || 'Admin adjustment';
												adjustUserCredits(user.id, parseInt(amount), description);
											}
										}}
										class="text-blue-600 hover:text-blue-800 text-sm"
									>
										Adjust Credits
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	</div>
{/if}
