<script lang="ts">
	import type { PageProps } from './$types';
	import * as Table from '$lib/components/ui/table/index.js';
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import {
		type ColumnDef,
		type PaginationState,
		type SortingState,
		type ColumnFiltersState,
		getCoreRowModel,
		getPaginationRowModel,
		getSortedRowModel,
		getFilteredRowModel
	} from '@tanstack/table-core';
	import { FlexRender, createSvelteTable, renderComponent } from '$lib/components/ui/data-table/index.js';
	import DataTableSortButton from '../db-viewer/data-table-sort-button.svelte';
	import * as m from '$lib/paraglide/messages.js';

	let { data }: PageProps = $props();

	let selectedUser = $state<any>(null);
	let max_credits = $state(0);
	let editDialogOpen = $state(false);

	function openEditDialog(user: any) {
		selectedUser = user;
		max_credits = user.max_credits ?? 20;
		editDialogOpen = true;
	}

	let pagination = $state<PaginationState>({ pageIndex: 0, pageSize: 10 });
	let sorting = $state<SortingState>([]);
	let columnFilters = $state<ColumnFiltersState>([]);

	const columns: ColumnDef<any>[] = [
		{ accessorKey: 'id', header: ({ column }) => renderComponent(DataTableSortButton, { title: m.id(), onclick: column.getToggleSortingHandler() }) },
		{ accessorKey: 'username', header: ({ column }) => renderComponent(DataTableSortButton, { title: m.username(), onclick: column.getToggleSortingHandler() }) },
		{ accessorKey: 'email', header: ({ column }) => renderComponent(DataTableSortButton, { title: m.email(), onclick: column.getToggleSortingHandler() }), cell: ({ row }) => row.original.email || '-' },
		{ accessorKey: 'role', header: ({ column }) => renderComponent(DataTableSortButton, { title: m.role(), onclick: column.getToggleSortingHandler() }), cell: ({ row }) => (row.original.role || (row.original.is_admin ? 'Admin' : 'User')).charAt(0).toUpperCase() + (row.original.role || (row.original.is_admin ? 'Admin' : 'User')).slice(1) },
		{ accessorKey: 'credits', header: ({ column }) => renderComponent(DataTableSortButton, { title: m.credits(), onclick: column.getToggleSortingHandler() }), cell: ({ row }) => `${row.original.credits ?? '-'}/${row.original.max_credits ?? '-'}` },
		{ accessorKey: 'score_count', header: ({ column }) => renderComponent(DataTableSortButton, { title: 'Scores', onclick: column.getToggleSortingHandler() }), cell: ({ row }) => row.original.score_count ?? 0 },
		{ accessorKey: 'last_login', header: ({ column }) => renderComponent(DataTableSortButton, { title: 'Last Login', onclick: column.getToggleSortingHandler() }), cell: ({ row }) => row.original.last_login ? new Date(row.original.last_login).toLocaleString() : '-' }
	];

	const table = createSvelteTable({
		get data() { return data.users; },
		columns,
		state: {
			get pagination() { return pagination; },
			get sorting() { return sorting; },
			get columnFilters() { return columnFilters; }
		},
		onPaginationChange: (updater) => {
			if (typeof updater === 'function') pagination = updater(pagination);
			else pagination = updater;
		},
		onSortingChange: (updater) => {
			if (typeof updater === 'function') sorting = updater(sorting);
			else sorting = updater;
		},
		onColumnFiltersChange: (updater) => {
			if (typeof updater === 'function') columnFilters = updater(columnFilters);
			else columnFilters = updater;
		},
		getCoreRowModel: getCoreRowModel(),
		getPaginationRowModel: getPaginationRowModel(),
		getSortedRowModel: getSortedRowModel(),
		getFilteredRowModel: getFilteredRowModel()
	});

	$effect(() => {
		if (data.progress?.status === 'processing' || data.progress?.status === 'cancelling') {
			const interval = setInterval(() => {
				invalidateAll();
			}, 2000);
			return () => clearInterval(interval);
		}
	});
</script>

<div class="mb-4 flex items-center justify-between">
	<h1 class="text-fancy-title text-2xl font-bold text-foreground">{m.admin_dashboard()}</h1>
</div>

<div class="grid gap-6 md:grid-cols-2 mb-8">
	<div class="rounded-md border bg-card p-6 text-card-foreground shadow-card">
		<h2 class="text-fancy-title mb-2 text-xl font-semibold">{m.agent_configuration()}</h2>
		<p class="mb-4 text-muted-foreground">{m.agent_configuration_desc()}</p>
		<form method="POST" action="?/set_models" use:enhance class="flex flex-col gap-4">
			<div class="space-y-2">
				<label for="model_main" class="text-sm font-medium leading-none">{m.main_agent_model()}</label>
				<select id="model_main" name="model_main" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
					<option value="google-gla:gemini-2.5-flash" selected={data.activeModels.main === 'google-gla:gemini-2.5-flash' || data.activeModels.main === ''}>Gemini 2.5 Flash</option>
					<option value="google-gla:gemini-2.5-pro" selected={data.activeModels.main === 'google-gla:gemini-2.5-pro'}>Gemini 2.5 Pro</option>
					<option value="google-gla:gemini-3-pro-preview" selected={data.activeModels.main === 'google-gla:gemini-3-pro-preview'}>Gemini 3 Pro Preview</option>
				</select>
			</div>
			<div class="space-y-2">
				<label for="model_imslp" class="text-sm font-medium leading-none">{m.imslp_agent_model()}</label>
				<select id="model_imslp" name="model_imslp" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
					<option value="google-gla:gemini-2.5-flash" selected={data.activeModels.imslp === 'google-gla:gemini-2.5-flash' || data.activeModels.imslp === ''}>Gemini 2.5 Flash</option>
					<option value="google-gla:gemini-2.5-pro" selected={data.activeModels.imslp === 'google-gla:gemini-2.5-pro'}>Gemini 2.5 Pro</option>
					<option value="google-gla:gemini-3-pro-preview" selected={data.activeModels.imslp === 'google-gla:gemini-3-pro-preview'}>Gemini 3 Pro Preview</option>
				</select>
			</div>
			<div class="space-y-2">
				<label for="model_complete" class="text-sm font-medium leading-none">{m.complete_agent_model()}</label>
				<select id="model_complete" name="model_complete" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
					<option value="google-gla:gemini-2.5-flash" selected={data.activeModels.complete === 'google-gla:gemini-2.5-flash' || data.activeModels.complete === ''}>Gemini 2.5 Flash</option>
					<option value="google-gla:gemini-2.5-pro" selected={data.activeModels.complete === 'google-gla:gemini-2.5-pro'}>Gemini 2.5 Pro</option>
					<option value="google-gla:gemini-3-pro-preview" selected={data.activeModels.complete === 'google-gla:gemini-3-pro-preview'}>Gemini 3 Pro Preview</option>
				</select>
			</div>
			<div class="space-y-2">
				<label for="model_imslp_complete" class="text-sm font-medium leading-none">IMSLP Complete Agent Model</label>
				<select id="model_imslp_complete" name="model_imslp_complete" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
					<option value="google-gla:gemini-2.5-flash" selected={data.activeModels.imslp_complete === 'google-gla:gemini-2.5-flash' || data.activeModels.imslp_complete === ''}>Gemini 2.5 Flash</option>
					<option value="google-gla:gemini-2.5-pro" selected={data.activeModels.imslp_complete === 'google-gla:gemini-2.5-pro'}>Gemini 2.5 Pro</option>
					<option value="google-gla:gemini-3-pro-preview" selected={data.activeModels.imslp_complete === 'google-gla:gemini-3-pro-preview'}>Gemini 3 Pro Preview</option>
				</select>
			</div>
			<button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 self-start" type="submit">
				{m.save()}
			</button>
		</form>
	</div>

	<div class="rounded-md border bg-card p-6 text-card-foreground shadow-card">
		<h2 class="text-fancy-title mb-2 text-xl font-semibold">{m.imslp_database()}</h2>
		<p class="mb-4 text-muted-foreground">
			{m.imslp_database_stats({ works: data.stats?.total_works || 0, composers: data.stats?.total_composers || 0 })}
		</p>
		<div class="flex gap-4 items-center">
			<form method="POST" action="?/update" use:enhance>
				<button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2" disabled={data.progress?.status === 'processing'}>
					{m.update_database()}
				</button>
			</form>
			<form method="POST" action="?/empty" use:enhance onsubmit={(e) => {
				if (!confirm(m.delete_imslp_confirm())) e.preventDefault();
			}}>
				<button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-destructive text-destructive-foreground hover:bg-destructive/90 h-10 px-4 py-2" disabled={data.progress?.status === 'processing'}>
					{m.delete_all_data()}
				</button>
			</form>
		</div>

		{#if data.progress?.status === 'processing' || data.progress?.status === 'cancelling'}
			<div class="mt-6 p-4 border rounded-md bg-muted/50">
				<div class="flex justify-between mb-2">
					<span class="font-medium text-sm">
						{#if data.progress.status === 'cancelling'}
							{m.status_cancelling()}
						{:else}
							{m.status_processing({ page: data.progress.page, total: data.progress.total })}
						{/if}
					</span>
				</div>
				<div class="w-full bg-secondary rounded-full h-2.5 mb-4 overflow-hidden">
					<div class="bg-primary h-2.5 rounded-full transition-all" style="width: {(data.progress.page / Math.max(1, data.progress.total)) * 100}%"></div>
				</div>
				<form method="POST" action="?/cancel" use:enhance>
					<button 
						disabled={data.progress.status === 'cancelling'}
						class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 rounded-md px-3 disabled:opacity-50"
					>
						{data.progress.status === 'cancelling' ? m.cancelling() : m.cancel_task()}
					</button>
				</form>
			</div>
		{/if}
	</div>
</div>

<div class="mb-4 flex items-center justify-between">
	<h2 class="text-fancy-title text-xl font-semibold text-foreground">{m.users()}</h2>
</div>

<div class="flex flex-wrap items-center gap-4 py-4">
	<Input
		placeholder={m.filter_titles()}
		value={(table.getColumn("username")?.getFilterValue() as string) ?? ""}
		oninput={(e) => table.getColumn("username")?.setFilterValue(e.currentTarget.value)}
		class="max-w-xs"
	/>
</div>

<div class="rounded-md border bg-card text-card-foreground shadow-card">
	<Table.Root>
		<Table.Header>
			{#each table.getHeaderGroups() as headerGroup (headerGroup.id)}
				<Table.Row>
					{#each headerGroup.headers as header (header.id)}
						<Table.Head>
							{#if !header.isPlaceholder}
								<FlexRender
									content={header.column.columnDef.header}
									context={header.getContext()}
								/>
							{/if}
						</Table.Head>
					{/each}
					<Table.Head class="text-right">{m.actions()}</Table.Head>
				</Table.Row>
			{/each}
		</Table.Header>
		<Table.Body>
			{#each table.getRowModel().rows as row (row.id)}
				<Table.Row class="transition-colors hover:bg-muted/50">
					{#each row.getVisibleCells() as cell (cell.id)}
						<Table.Cell>
							<FlexRender
								content={cell.column.columnDef.cell}
								context={cell.getContext()}
							/>
						</Table.Cell>
					{/each}
					<Table.Cell class="text-right">
						<div class="flex items-center justify-end gap-2">
							<Button variant="outline" size="sm" onclick={() => openEditDialog(row.original)}>{m.edit()}</Button>
						</div>
					</Table.Cell>
				</Table.Row>
			{:else}
				<Table.Row>
					<Table.Cell colspan={columns.length + 1} class="text-center text-muted-foreground py-4">
						{m.no_users_found()}
					</Table.Cell>
				</Table.Row>
			{/each}
		</Table.Body>
	</Table.Root>
</div>

<div class="flex items-center justify-end space-x-2 py-4">
	<div class="flex-1 text-sm text-muted-foreground">
		{m.page_of({ page: table.getState().pagination.pageIndex + 1, total: Math.max(1, table.getPageCount()) })}
	</div>
	<Button
		variant="outline"
		size="sm"
		onclick={() => table.previousPage()}
		disabled={!table.getCanPreviousPage()}
	>
		{m.previous()}
	</Button>
	<Button
		variant="outline"
		size="sm"
		onclick={() => table.nextPage()}
		disabled={!table.getCanNextPage()}
	>
		{m.next()}
	</Button>
</div>

<Sheet.Root bind:open={editDialogOpen}>
	<Sheet.Content>
		<Sheet.Header>
			<Sheet.Title>{m.edit_max_credits({ username: selectedUser?.username || '' })}</Sheet.Title>
			<Sheet.Description>
				{m.edit_max_credits_desc()}
			</Sheet.Description>
		</Sheet.Header>
		{#if selectedUser}
			<div class="mt-4 space-y-6">
				<form
					method="POST"
					action="?/set_credits"
					use:enhance={() => {
						return async ({ update }) => {
							editDialogOpen = false;
							await update();
						};
					}}
					class="space-y-4"
				>
					<input type="hidden" name="user_id" value={selectedUser.id} />
					<div class="space-y-2">
						<label for="max_credits" class="text-sm font-medium">{m.max_credits()}</label>
						<Input id="max_credits" name="max_credits" type="number" bind:value={max_credits} />
					</div>
					<Sheet.Footer>
						<Button type="submit">{m.save_changes()}</Button>
					</Sheet.Footer>
				</form>

				<form method="POST" action="?/refill_credits" use:enhance={() => {
					return async ({ update }) => {
						editDialogOpen = false;
						await update();
					};
				}}>
					<input type="hidden" name="user_id" value={selectedUser.id} />
					<Button
						variant="outline"
						type="submit"
						class="w-full"
						disabled={selectedUser.credits === selectedUser.max_credits}
					>
						{m.refill_credits()}
					</Button>
				</form>
			</div>
		{/if}
	</Sheet.Content>
</Sheet.Root>
