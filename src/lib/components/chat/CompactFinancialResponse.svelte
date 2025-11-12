<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';

	export let data: any = {};

	// Compact metric card component
	function formatNumber(num: number): string {
		if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`;
		if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`;
		if (num >= 1e3) return `${(num / 1e3).toFixed(2)}K`;
		return num.toFixed(2);
	}

	function formatPercent(num: number): string {
		return `${num > 0 ? '+' : ''}${num.toFixed(1)}%`;
	}

	let expanded = false;
</script>

<div class="compact-response">
	<!-- Header with minimal text -->
	{#if data.title}
		<div class="response-header">
			<h3>{data.title}</h3>
			{#if data.subtitle}
				<p class="subtitle">{data.subtitle}</p>
			{/if}
		</div>
	{/if}

	<!-- Compact Metrics Grid -->
	{#if data.metrics}
		<div class="metrics-grid">
			{#each data.metrics as metric}
				<div class="metric-card">
					<div class="metric-label">{metric.label}</div>
					<div class="metric-value">
						{formatNumber(metric.value)}
						{#if metric.badge}
							<span class="badge">{metric.badge}</span>
						{/if}
					</div>
					{#if metric.change}
						<div class="metric-change {metric.change > 0 ? 'positive' : 'negative'}">
							{formatPercent(metric.change)}
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}

	<!-- Compact Data Table (like your images) -->
	{#if data.table}
		<div class="compact-table">
			<table>
				<thead>
					<tr>
						{#each data.table.columns as col}
							<th>{col}</th>
						{/each}
					</tr>
				</thead>
				<tbody>
					{#each data.table.rows as row}
						<tr>
							{#each row.values as value, idx}
								<td>
									{#if idx === 0}
										<div class="company-cell">
											{#if row.icon}
												<span class="company-icon" style="background: {row.color}"
													>{row.icon}</span
												>
											{/if}
											<span>{value}</span>
										</div>
									{:else if typeof value === 'number'}
										<span class="number-cell">
											{formatNumber(value)}
											{#if row.badges && row.badges[idx]}
												<span class="table-badge">{row.badges[idx]}</span>
											{/if}
										</span>
									{:else}
										{value}
									{/if}
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}

	<!-- Line Chart (like your revenue charts) -->
	{#if data.lineChart}
		<div class="chart-container">
			<div id="line-chart-{data.id || 'default'}" class="line-chart"></div>
		</div>
	{/if}

	<!-- Expandable Details -->
	{#if data.details}
		<button class="expand-btn" on:click={() => (expanded = !expanded)}>
			<span>{expanded ? '▲' : '▼'}</span>
			{expanded ? 'Show less' : 'Show more'}
		</button>

		{#if expanded}
			<div class="details-section">
				{@html data.details}
			</div>
		{/if}
	{/if}
</div>

<style>
	.compact-response {
		background: #1a1a1a;
		border-radius: 12px;
		padding: 20px;
		margin: 16px 0;
		color: #e5e5e5;
	}

	.response-header h3 {
		font-size: 18px;
		font-weight: 600;
		margin: 0 0 4px 0;
		color: #fff;
	}

	.subtitle {
		font-size: 13px;
		color: #888;
		margin: 0 0 16px 0;
	}

	/* Metrics Grid */
	.metrics-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 12px;
		margin-bottom: 20px;
	}

	.metric-card {
		background: #252525;
		border-radius: 8px;
		padding: 12px;
		border: 1px solid #333;
	}

	.metric-label {
		font-size: 11px;
		color: #888;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		margin-bottom: 6px;
	}

	.metric-value {
		font-size: 20px;
		font-weight: 700;
		color: #fff;
		display: flex;
		align-items: center;
		gap: 6px;
	}

	.badge {
		font-size: 10px;
		background: #444;
		color: #aaa;
		padding: 2px 6px;
		border-radius: 4px;
		font-weight: 500;
	}

	.metric-change {
		font-size: 12px;
		margin-top: 4px;
		font-weight: 600;
	}

	.metric-change.positive {
		color: #10b981;
	}

	.metric-change.negative {
		color: #ef4444;
	}

	/* Compact Table */
	.compact-table {
		overflow-x: auto;
		margin: 20px 0;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 13px;
	}

	thead {
		border-bottom: 1px solid #333;
	}

	th {
		text-align: left;
		padding: 10px 12px;
		font-size: 11px;
		color: #888;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		font-weight: 500;
	}

	td {
		padding: 12px;
		border-bottom: 1px solid #2a2a2a;
	}

	.company-cell {
		display: flex;
		align-items: center;
		gap: 10px;
		font-weight: 500;
	}

	.company-icon {
		width: 24px;
		height: 24px;
		border-radius: 6px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 12px;
		font-weight: 600;
	}

	.number-cell {
		display: flex;
		align-items: center;
		gap: 6px;
		font-variant-numeric: tabular-nums;
	}

	.table-badge {
		font-size: 9px;
		background: #333;
		color: #888;
		padding: 2px 5px;
		border-radius: 3px;
	}

	/* Chart Container */
	.chart-container {
		margin: 20px 0;
		background: #252525;
		border-radius: 8px;
		padding: 16px;
		border: 1px solid #333;
	}

	.line-chart {
		width: 100%;
		height: 300px;
	}

	/* Expand Button */
	.expand-btn {
		width: 100%;
		padding: 10px;
		background: #252525;
		border: 1px solid #333;
		border-radius: 6px;
		color: #888;
		font-size: 12px;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 6px;
		margin-top: 16px;
		transition: all 0.2s;
	}

	.expand-btn:hover {
		background: #2a2a2a;
		color: #fff;
	}

	.details-section {
		margin-top: 16px;
		padding: 16px;
		background: #252525;
		border-radius: 8px;
		border: 1px solid #333;
		font-size: 13px;
		line-height: 1.6;
		color: #ccc;
	}

	/* Mobile Responsive */
	@media (max-width: 768px) {
		.metrics-grid {
			grid-template-columns: repeat(2, 1fr);
		}

		.compact-table {
			font-size: 11px;
		}

		th,
		td {
			padding: 8px;
		}
	}
</style>
