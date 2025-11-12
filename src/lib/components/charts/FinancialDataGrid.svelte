<script lang="ts">
	import { onMount } from 'svelte';
	import { AgGridSvelte } from 'ag-grid-svelte';
	import 'ag-grid-community/styles/ag-grid.css';
	import 'ag-grid-community/styles/ag-theme-alpine.css';

	export let rowData: Array<any> = [];
	export let columnDefs: Array<any> = [];
	export let title: string = 'Financial Data';
	export let height: string = '400px';

	let gridApi: any;
	let gridColumnApi: any;

	const defaultColDef = {
		sortable: true,
		filter: true,
		resizable: true,
		flex: 1,
		minWidth: 100
	};

	function onGridReady(params: any) {
		gridApi = params.api;
		gridColumnApi = params.columnApi;
		gridApi.sizeColumnsToFit();
	}

	function exportToCSV() {
		if (gridApi) {
			gridApi.exportDataAsCsv({
				fileName: `${title.replace(/\s+/g, '_')}.csv`
			});
		}
	}

	// Auto-format number columns
	$: if (columnDefs.length === 0 && rowData.length > 0) {
		const firstRow = rowData[0];
		columnDefs = Object.keys(firstRow).map((key) => {
			const isNumber = typeof firstRow[key] === 'number';
			return {
				field: key,
				headerName: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' '),
				valueFormatter: isNumber
					? (params: any) => {
							if (params.value == null) return '';
							return typeof params.value === 'number'
								? params.value.toLocaleString(undefined, {
										minimumFractionDigits: 2,
										maximumFractionDigits: 2
								  })
								: params.value;
					  }
					: undefined,
				cellStyle: isNumber ? { textAlign: 'right' } : undefined
			};
		});
	}
</script>

<div class="financial-grid-container">
	<div class="flex items-center justify-between mb-3">
		<h3 class="text-lg font-semibold dark:text-gray-200">{title}</h3>
		<button
			on:click={exportToCSV}
			class="px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
		>
			📊 Export CSV
		</button>
	</div>

	<div class="ag-theme-alpine dark:ag-theme-alpine-dark" style="height: {height}; width: 100%;">
		<AgGridSvelte
			{rowData}
			{columnDefs}
			{defaultColDef}
			on:gridReady={onGridReady}
			animateRows={true}
			pagination={true}
			paginationPageSize={20}
		/>
	</div>
</div>

<style>
	.financial-grid-container {
		background: rgba(255, 255, 255, 0.05);
		backdrop-filter: blur(10px);
		border-radius: 12px;
		padding: 16px;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	:global(.dark) .financial-grid-container {
		background: rgba(0, 0, 0, 0.2);
		border-color: rgba(255, 255, 255, 0.1);
	}

	:global(.ag-theme-alpine-dark) {
		--ag-background-color: transparent;
		--ag-foreground-color: #e5e7eb;
		--ag-header-background-color: rgba(0, 0, 0, 0.3);
		--ag-odd-row-background-color: rgba(255, 255, 255, 0.02);
		--ag-row-hover-color: rgba(255, 255, 255, 0.05);
	}
</style>
