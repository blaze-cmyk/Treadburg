<script lang="ts">
	export let rowData: Array<any> = [];
	export let title: string = 'Financial Data';
	export let height: string = '400px';

	let sortColumn: string = '';
	let sortDirection: 'asc' | 'desc' = 'asc';
	let searchTerm: string = '';
	let currentPage: number = 1;
	let pageSize: number = 20;

	$: columns = rowData.length > 0 ? Object.keys(rowData[0]) : [];
	
	$: filteredData = rowData.filter((row) =>
		Object.values(row).some((val) =>
			String(val).toLowerCase().includes(searchTerm.toLowerCase())
		)
	);

	$: sortedData = [...filteredData].sort((a, b) => {
		if (!sortColumn) return 0;
		const aVal = a[sortColumn];
		const bVal = b[sortColumn];
		
		if (typeof aVal === 'number' && typeof bVal === 'number') {
			return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
		}
		
		const aStr = String(aVal).toLowerCase();
		const bStr = String(bVal).toLowerCase();
		return sortDirection === 'asc' 
			? aStr.localeCompare(bStr)
			: bStr.localeCompare(aStr);
	});

	$: totalPages = Math.ceil(sortedData.length / pageSize);
	$: paginatedData = sortedData.slice(
		(currentPage - 1) * pageSize,
		currentPage * pageSize
	);

	function handleSort(column: string) {
		if (sortColumn === column) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortColumn = column;
			sortDirection = 'asc';
		}
	}

	function formatValue(value: any): string {
		if (typeof value === 'number') {
			return value.toLocaleString(undefined, {
				minimumFractionDigits: 2,
				maximumFractionDigits: 2
			});
		}
		return String(value);
	}

	function formatHeader(key: string): string {
		return key
			.split('_')
			.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
			.join(' ');
	}

	function exportToCSV() {
		const headers = columns.join(',');
		const rows = sortedData.map((row) =>
			columns.map((col) => `"${row[col]}"`).join(',')
		);
		const csv = [headers, ...rows].join('\n');
		
		const blob = new Blob([csv], { type: 'text/csv' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `${title.replace(/\s+/g, '_')}.csv`;
		a.click();
		URL.revokeObjectURL(url);
	}
</script>

<div class="financial-grid-container">
	<div class="flex items-center justify-between mb-3">
		<h3 class="text-lg font-semibold dark:text-gray-200">{title}</h3>
		<div class="flex items-center gap-2">
			<input
				type="text"
				bind:value={searchTerm}
				placeholder="Search..."
				class="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
			/>
			<button
				on:click={exportToCSV}
				class="px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
			>
				📊 Export CSV
			</button>
		</div>
	</div>

	<div class="table-container" style="max-height: {height};">
		<table class="data-table">
			<thead>
				<tr>
					{#each columns as column}
						<th on:click={() => handleSort(column)}>
							<div class="th-content">
								{formatHeader(column)}
								{#if sortColumn === column}
									<span class="sort-indicator">
										{sortDirection === 'asc' ? '↑' : '↓'}
									</span>
								{/if}
							</div>
						</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each paginatedData as row, i}
					<tr class:even={i % 2 === 0}>
						{#each columns as column}
							<td class:number={typeof row[column] === 'number'}>
								{formatValue(row[column])}
							</td>
						{/each}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	{#if totalPages > 1}
		<div class="pagination">
			<button
				on:click={() => currentPage = Math.max(1, currentPage - 1)}
				disabled={currentPage === 1}
				class="pagination-btn"
			>
				Previous
			</button>
			<span class="page-info">
				Page {currentPage} of {totalPages}
			</span>
			<button
				on:click={() => currentPage = Math.min(totalPages, currentPage + 1)}
				disabled={currentPage === totalPages}
				class="pagination-btn"
			>
				Next
			</button>
		</div>
	{/if}
</div>

<style>
	.financial-grid-container {
		background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
		backdrop-filter: blur(20px);
		border-radius: 16px;
		padding: 24px;
		border: 1px solid rgba(255, 255, 255, 0.1);
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
		position: relative;
		overflow: hidden;
	}
	
	.financial-grid-container::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 2px;
		background: linear-gradient(90deg, #f59e0b, #ef4444, #ec4899);
		background-size: 200% 100%;
		animation: shimmer 3s linear infinite;
	}
	
	@keyframes shimmer {
		0% { background-position: -200% 0; }
		100% { background-position: 200% 0; }
	}

	:global(.dark) .financial-grid-container {
		background: rgba(0, 0, 0, 0.2);
		border-color: rgba(255, 255, 255, 0.1);
	}

	.table-container {
		overflow: auto;
		border-radius: 8px;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.data-table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.875rem;
	}

	.data-table thead {
		position: sticky;
		top: 0;
		background: rgba(99, 102, 241, 0.1);
		backdrop-filter: blur(10px);
		z-index: 10;
	}

	.data-table th {
		padding: 12px 16px;
		text-align: left;
		font-weight: 600;
		cursor: pointer;
		user-select: none;
		transition: background 0.2s;
		border-bottom: 2px solid rgba(99, 102, 241, 0.3);
	}

	.data-table th:hover {
		background: rgba(99, 102, 241, 0.15);
	}

	.th-content {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.sort-indicator {
		font-size: 1rem;
		color: #6366f1;
	}

	.data-table td {
		padding: 10px 16px;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	}

	.data-table td.number {
		text-align: right;
		font-family: 'Courier New', monospace;
	}

	.data-table tbody tr:hover {
		background: rgba(255, 255, 255, 0.05);
	}

	.data-table tbody tr.even {
		background: rgba(255, 255, 255, 0.02);
	}

	.pagination {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 16px;
		margin-top: 16px;
	}

	.pagination-btn {
		px: 12px;
		padding: 8px 16px;
		background: rgba(99, 102, 241, 0.1);
		border: 1px solid rgba(99, 102, 241, 0.3);
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s;
		font-size: 0.875rem;
	}

	.pagination-btn:hover:not(:disabled) {
		background: rgba(99, 102, 241, 0.2);
		border-color: rgba(99, 102, 241, 0.5);
	}

	.pagination-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.page-info {
		font-size: 0.875rem;
		color: #9ca3af;
	}
</style>
