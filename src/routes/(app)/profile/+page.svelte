<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { getUserProfile, updateUserProfile, type UserProfile, type UserStats } from '$lib/apis/user-management';
	
	let userProfile: UserProfile | null = null;
	let userStats: UserStats | null = null;
	let loading = true;
	let error = '';
	let editing = false;
	
	// Edit form
	let editForm = {
		username: '',
		full_name: '',
		bio: ''
	};
	
	onMount(async () => {
		await loadProfile();
	});
	
	async function loadProfile() {
		loading = true;
		try {
			const token = localStorage.getItem('token');
			if (!token) {
				goto('/');
				return;
			}
			
			// Try to fetch from new API
			try {
				const data = await getUserProfile(token);
				userProfile = data.user;
				userStats = data.stats;
			} catch (apiError: any) {
				console.warn('API not available, using fallback data:', apiError);
				
				// Fallback to existing user store
				if ($user) {
					userProfile = {
						id: $user.id,
						email: $user.email,
						username: $user.name,
						full_name: $user.name,
						avatar_url: $user.profile_image_url,
						bio: '',
						credits: 0,
						total_credits_purchased: 0,
						total_credits_used: 0,
						subscription_tier: 'free',
						subscription_status: 'inactive',
						is_verified: true,
						created_at: new Date().toISOString(),
						last_login_at: new Date().toISOString()
					};
					
					userStats = {
						total_credits_purchased: 0,
						total_credits_used: 0,
						current_credits: 0,
						total_payments: 0,
						total_spent: 0,
						api_calls_count: 0,
						login_count: 0,
						member_since: new Date().toISOString()
					};
					
					error = 'Using local data. Full features will be available after database sync.';
				} else {
					throw new Error('No user data available');
				}
			}
			
			// Populate edit form
			if (userProfile) {
				editForm = {
					username: userProfile.username || '',
					full_name: userProfile.full_name || '',
					bio: userProfile.bio || ''
				};
			}
		} catch (e: any) {
			error = e.message;
			console.error('Error loading profile:', e);
		} finally {
			loading = false;
		}
	}
	
	async function saveProfile() {
		try {
			const token = localStorage.getItem('token');
			if (!token) return;
			
			await updateUserProfile(token, editForm);
			await loadProfile();
			editing = false;
		} catch (e: any) {
			error = e.message;
		}
	}
	
	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}
	
	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(amount);
	}
</script>

<svelte:head>
	<title>My Profile - TradeBerg</title>
</svelte:head>

<div class="max-w-5xl mx-auto p-6">
	<h1 class="text-3xl font-bold mb-6">My Profile</h1>
	
	{#if error && error.includes('local data')}
		<div class="bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded mb-6">
			<strong>Note:</strong> {error}
		</div>
	{:else if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
			{error}
		</div>
	{/if}
	
	{#if loading}
		<div class="text-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
			<p class="mt-4 text-gray-600 dark:text-gray-400">Loading profile...</p>
		</div>
	{:else if userProfile}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Profile Card -->
			<div class="lg:col-span-1">
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
					<div class="text-center">
						{#if userProfile.avatar_url}
							<img src={userProfile.avatar_url} alt="Avatar" class="w-24 h-24 rounded-full mx-auto mb-4" />
						{:else}
							<div class="w-24 h-24 rounded-full bg-blue-600 flex items-center justify-center text-white text-3xl font-bold mx-auto mb-4">
								{userProfile.email?.[0]?.toUpperCase() || 'U'}
							</div>
						{/if}
						
						<h2 class="text-xl font-bold">{userProfile.full_name || userProfile.username || 'User'}</h2>
						<p class="text-sm text-gray-500 dark:text-gray-400">{userProfile.email}</p>
						
						{#if userProfile.subscription_tier !== 'free'}
							<span class="inline-block mt-2 px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 text-sm rounded-full font-medium">
								{userProfile.subscription_tier.toUpperCase()}
							</span>
						{/if}
						
						<div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
							<div class="text-sm text-gray-600 dark:text-gray-400">
								Member since {formatDate(userProfile.created_at)}
							</div>
						</div>
					</div>
				</div>
				
				<!-- Credits Card -->
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mt-6">
					<h3 class="text-lg font-bold mb-4">Credits</h3>
					<div class="text-center">
						<div class="text-4xl font-bold text-blue-600 dark:text-blue-400">
							{userProfile.credits}
						</div>
						<div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Available Credits</div>
					</div>
					
					<button
						on:click={() => goto('/credits')}
						class="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
					>
						Buy More Credits
					</button>
				</div>
			</div>
			
			<!-- Details Section -->
			<div class="lg:col-span-2 space-y-6">
				<!-- Profile Information -->
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
					<div class="flex justify-between items-center mb-4">
						<h3 class="text-lg font-bold">Profile Information</h3>
						{#if !editing}
							<button
								on:click={() => editing = true}
								class="px-4 py-2 text-sm bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600"
							>
								Edit Profile
							</button>
						{/if}
					</div>
					
					{#if editing}
						<div class="space-y-4">
							<div>
								<label class="block text-sm font-medium mb-1">Username</label>
								<input
									type="text"
									bind:value={editForm.username}
									class="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
									placeholder="Enter username"
								/>
							</div>
							
							<div>
								<label class="block text-sm font-medium mb-1">Full Name</label>
								<input
									type="text"
									bind:value={editForm.full_name}
									class="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
									placeholder="Enter full name"
								/>
							</div>
							
							<div>
								<label class="block text-sm font-medium mb-1">Bio</label>
								<textarea
									bind:value={editForm.bio}
									rows="3"
									class="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
									placeholder="Tell us about yourself"
								></textarea>
							</div>
							
							<div class="flex gap-2">
								<button
									on:click={saveProfile}
									class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
								>
									Save Changes
								</button>
								<button
									on:click={() => editing = false}
									class="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
								>
									Cancel
								</button>
							</div>
						</div>
					{:else}
						<div class="space-y-3">
							<div>
								<div class="text-sm text-gray-500 dark:text-gray-400">Username</div>
								<div class="font-medium">{userProfile.username || 'Not set'}</div>
							</div>
							<div>
								<div class="text-sm text-gray-500 dark:text-gray-400">Full Name</div>
								<div class="font-medium">{userProfile.full_name || 'Not set'}</div>
							</div>
							<div>
								<div class="text-sm text-gray-500 dark:text-gray-400">Email</div>
								<div class="font-medium">{userProfile.email}</div>
							</div>
							{#if userProfile.bio}
								<div>
									<div class="text-sm text-gray-500 dark:text-gray-400">Bio</div>
									<div class="font-medium">{userProfile.bio}</div>
								</div>
							{/if}
						</div>
					{/if}
				</div>
				
				<!-- Statistics -->
				{#if userStats}
					<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
						<h3 class="text-lg font-bold mb-4">Statistics</h3>
						
						<div class="grid grid-cols-2 md:grid-cols-3 gap-4">
							<div class="text-center p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
								<div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
									{userStats.total_credits_purchased}
								</div>
								<div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Credits Purchased</div>
							</div>
							
							<div class="text-center p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
								<div class="text-2xl font-bold text-green-600 dark:text-green-400">
									{userStats.total_credits_used}
								</div>
								<div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Credits Used</div>
							</div>
							
							<div class="text-center p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
								<div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
									{formatCurrency(userStats.total_spent)}
								</div>
								<div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Total Spent</div>
							</div>
							
							<div class="text-center p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
								<div class="text-2xl font-bold text-orange-600 dark:text-orange-400">
									{userStats.total_payments}
								</div>
								<div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Payments</div>
							</div>
							
							<div class="text-center p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
								<div class="text-2xl font-bold text-teal-600 dark:text-teal-400">
									{userStats.api_calls_count}
								</div>
								<div class="text-sm text-gray-500 dark:text-gray-400 mt-1">API Calls</div>
							</div>
							
							<div class="text-center p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
								<div class="text-2xl font-bold text-pink-600 dark:text-pink-400">
									{userStats.login_count}
								</div>
								<div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Logins</div>
							</div>
						</div>
					</div>
				{/if}
				
				<!-- Quick Actions -->
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
					<h3 class="text-lg font-bold mb-4">Quick Actions</h3>
					
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<button
							on:click={() => goto('/credits')}
							class="p-4 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition text-left"
						>
							<div class="font-bold">Buy Credits</div>
							<div class="text-sm mt-1">Purchase more credits</div>
						</button>
						
						<button
							on:click={() => goto('/transactions')}
							class="p-4 border-2 border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition text-left"
						>
							<div class="font-bold">View Transactions</div>
							<div class="text-sm mt-1">See your credit history</div>
						</button>
						
						<button
							on:click={() => goto('/payments')}
							class="p-4 border-2 border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition text-left"
						>
							<div class="font-bold">Payment History</div>
							<div class="text-sm mt-1">View all payments</div>
						</button>
						
						<button
							on:click={() => goto('/subscription')}
							class="p-4 border-2 border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition text-left"
						>
							<div class="font-bold">Subscription</div>
							<div class="text-sm mt-1">Manage your plan</div>
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>
