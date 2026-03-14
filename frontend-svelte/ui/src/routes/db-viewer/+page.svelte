<script lang="ts">
	import type { PageProps } from './$types';
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
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
	import AgentChat from '$lib/components/AgentChat.svelte';
	import DataTableSortButton from './data-table-sort-button.svelte';
	import { imslpAgentHistoryStore } from '$lib/stores/chat.svelte';
	import * as m from '$lib/paraglide/messages.js';

	let { data, form }: PageProps = $props();
	let selectedScoreId = $state<number | null>(null);
	let agentSelectedScore = $state<any>(null);
	let imslpSheetOpen = $state(false);
	let uploading = $state(false);
	let recompleting = $state(false);
	let sheetOpen = $state(false);
	let selectedScore = $derived(data.scores.find((s: any) => s.id === selectedScoreId));

	let pagination = $state<PaginationState>({ pageIndex: 0, pageSize: 10 });
	let sorting = $state<SortingState>([]);
	let columnFilters = $state<ColumnFiltersState>([]);

	const columns: ColumnDef<any>[] = [
		{ 
			accessorKey: 'title', 
			header: ({ column }) => renderComponent(DataTableSortButton, { title: 'Title', onclick: column.getToggleSortingHandler() }) 
		},
		{ 
			accessorKey: 'composer', 
			header: ({ column }) => renderComponent(DataTableSortButton, { title: 'Composer', onclick: column.getToggleSortingHandler() }) 
		},
		{ 
			accessorKey: 'instrumentation', 
			header: ({ column }) => renderComponent(DataTableSortButton, { title: 'Instrumentation', onclick: column.getToggleSortingHandler() }),
			cell: ({ row }) => row.original.instrumentation || '-'
		},
		{ 
			accessorKey: 'year', 
			header: ({ column }) => renderComponent(DataTableSortButton, { title: 'Year', onclick: column.getToggleSortingHandler() }),
			filterFn: (row, columnId, filterValue) => {
				const val = row.getValue(columnId) as number;
				const [min, max] = (filterValue as [number | undefined, number | undefined]) || [undefined, undefined];
				if (min !== undefined && !isNaN(min) && val < min) return false;
				if (max !== undefined && !isNaN(max) && val > max) return false;
				return true;
			}
		},
		{ accessorKey: 'period', header: 'Period' },
		{ accessorKey: 'genre', header: 'Genre' }
	];

	const table = createSvelteTable({
		get data() {
			return data.scores;
		},
		columns,
		state: {
			get pagination() {
				return pagination;
			},
			get sorting() {
				return sorting;
			},
			get columnFilters() {
				return columnFilters;
			}
		},
		onPaginationChange: (updater) => {
			if (typeof updater === 'function') {
				pagination = updater(pagination);
			} else {
				pagination = updater;
			}
		},
		onSortingChange: (updater) => {
			if (typeof updater === 'function') {
				sorting = updater(sorting);
			} else {
				sorting = updater;
			}
		},
		onColumnFiltersChange: (updater) => {
			if (typeof updater === 'function') {
				columnFilters = updater(columnFilters);
			} else {
				columnFilters = updater;
			}
		},
		getCoreRowModel: getCoreRowModel(),
		getPaginationRowModel: getPaginationRowModel(),
		getSortedRowModel: getSortedRowModel(),
		getFilteredRowModel: getFilteredRowModel()
	});

	let imslpPagination = $state<PaginationState>({ pageIndex: 0, pageSize: 5 });
	let imslpSorting = $state<SortingState>([]);
	let imslpColumnFilters = $state<ColumnFiltersState>([]);

	const imslpColumns: ColumnDef<any>[] = [
		{ 
			accessorKey: 'composer', 
			header: ({ column }) => renderComponent(DataTableSortButton, { title: 'Composer', onclick: column.getToggleSortingHandler() }) 
		},
		{ 
			accessorKey: 'title', 
			header: ({ column }) => renderComponent(DataTableSortButton, { title: 'Title', onclick: column.getToggleSortingHandler() }) 
		},
		{ 
			accessorKey: 'instrumentation', 
			header: ({ column }) => renderComponent(DataTableSortButton, { title: 'Instrumentation', onclick: column.getToggleSortingHandler() }),
			cell: ({ row }) => row.original.instrumentation || '-'
		},
		{ 
			accessorKey: 'year', 
			header: ({ column }) => renderComponent(DataTableSortButton, { title: 'Year', onclick: column.getToggleSortingHandler() }),
			cell: ({ row }) => row.original.year || '-'
		}
	];

	let imslpScores = $state<any[]>([]);
	function onImslpResult(data: any) {
		const res = data.agent_results;
		const scores = res.scores || [];
		imslpScores = scores;
		return {
			question: data.question,
			answer: {
				answer: res.response,
				scores: scores
			},
			rawHistory: res.message_history
		};
	}

	const imslpTable = createSvelteTable({
		get data() {
			return imslpScores;
		},
		columns: imslpColumns,
		state: {
			get pagination() { return imslpPagination; },
			get sorting() { return imslpSorting; },
			get columnFilters() { return imslpColumnFilters; }
		},
		onPaginationChange: (updater) => {
			if (typeof updater === 'function') {
				imslpPagination = updater(imslpPagination);
			} else {
				imslpPagination = updater;
			}
		},
		onSortingChange: (updater) => {
			if (typeof updater === 'function') {
				imslpSorting = updater(imslpSorting);
			} else {
				imslpSorting = updater;
			}
		},
		onColumnFiltersChange: (updater) => {
			if (typeof updater === 'function') {
				imslpColumnFilters = updater(imslpColumnFilters);
			} else {
				imslpColumnFilters = updater;
			}
		},
		getCoreRowModel: getCoreRowModel(),
		getPaginationRowModel: getPaginationRowModel(),
		getSortedRowModel: getSortedRowModel(),
		getFilteredRowModel: getFilteredRowModel()
	});
</script>

<div class="p-8">
	<div class="mb-8 rounded-md border bg-card p-4 text-card-foreground shadow-card">
		<h2 class="text-fancy-title mb-4 text-lg font-semibold">{m.add_new_score()}</h2>
		<Tabs.Root value="manual" class="w-full">
			<Tabs.List class="mb-4">
				<Tabs.Trigger value="manual">{m.manual_upload()}</Tabs.Trigger>
				<Tabs.Trigger value="imslp">{m.from_imslp()}</Tabs.Trigger>
			</Tabs.List>
			<Tabs.Content value="manual">
				<form method="POST" action="?/upload" enctype="multipart/form-data" use:enhance={() => {
					uploading = true;
					return async ({ update }) => {
						uploading = false;
						update();
					};
				}} class="flex flex-col gap-4 md:flex-row md:items-end">
					<div class="flex-1 space-y-2">
						<label for="title" class="text-sm font-medium leading-none">{m.title()}</label>
						<Input id="title" name="title" required />
					</div>
					<div class="flex-1 space-y-2">
						<label for="composer" class="text-sm font-medium leading-none">{m.composer()}</label>
						<Input id="composer" name="composer" required />
					</div>
					<div class="flex-1 space-y-2">
						<label for="file" class="text-sm font-medium leading-none">{m.pdf_file()}</label>
						<Input id="file" name="file" type="file" accept="application/pdf" required />
					</div>
					<Button type="submit" disabled={uploading}>
						{uploading ? m.adding() : m.add()}
					</Button>
				</form>
			</Tabs.Content>
			<Tabs.Content value="imslp">
				<div class="flex flex-col {imslpAgentHistoryStore.history.length > 0 ? 'h-[500px]' : 'h-auto'} w-full">
					<AgentChat
						{form}
						action="?/ask_agent"
						title={m.imslp_search_help()}
						placeholder={m.agent_placeholder_imslp()}
						onResult={onImslpResult}
						user={data.user}
						store={imslpAgentHistoryStore}
					>
						{#snippet children()}
							<div class="text-xs max-w-sm">
								{m.warning_limit_100()}
							</div>
						{/snippet}
						{#snippet resultSnippet({ msg, isLast })}
							<p class="mb-4 text-sm whitespace-pre-wrap">{msg.answer}</p>
							{#if isLast}
								{#if msg.scores && msg.scores.length > 0}
									<div
										class="mb-4 overflow-hidden rounded-md border bg-card text-card-foreground shadow-card"
									>
										<Table.Root>
											<Table.Header>
												{#each imslpTable.getHeaderGroups() as headerGroup (headerGroup.id)}
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
													</Table.Row>
												{/each}
											</Table.Header>
											<Table.Body>
												{#each imslpTable.getRowModel().rows as row (row.id)}
													<Table.Row
														class="cursor-pointer transition-colors hover:bg-muted/50 {agentSelectedScore?.id ===
														row.original.id
															? 'bg-muted'
															: ''}"
														onclick={() => {
															if (!uploading) {
																agentSelectedScore = row.original;
																imslpSheetOpen = true;
															}
														}}
													>
														{#each row.getVisibleCells() as cell (cell.id)}
															<Table.Cell
																class="max-w-[120px] truncate sm:max-w-[150px] md:max-w-[200px]"
															>
																<FlexRender
																	content={cell.column.columnDef.cell}
																	context={cell.getContext()}
																/>
															</Table.Cell>
														{/each}
													</Table.Row>
												{/each}
											</Table.Body>
										</Table.Root>

										<div class="flex items-center justify-end space-x-2 py-4 px-4 border-t">
											<div class="flex-1 text-sm text-muted-foreground">
												Page {imslpTable.getState().pagination.pageIndex + 1} of {Math.max(1, imslpTable.getPageCount())}
											</div>
											<Button
												variant="outline"
												size="sm"
												onclick={() => imslpTable.previousPage()}
												disabled={!imslpTable.getCanPreviousPage()}
											>
												Previous
											</Button>
											<Button
												variant="outline"
												size="sm"
												onclick={() => imslpTable.nextPage()}
												disabled={!imslpTable.getCanNextPage()}
											>
												Next
											</Button>
										</div>
									</div>
								{:else if msg.answer}
									<p class="text-sm text-muted-foreground mt-2 text-center">
										No matching scores found.
									</p>
								{/if}
							{/if}
						{/snippet}
					</AgentChat>
				</div>
			</Tabs.Content>
		</Tabs.Root>
		{#if form?.error}
			<p class="mt-4 text-sm font-medium text-destructive">{form.error}</p>
		{/if}
		{#if form?.scoreAdded}
			<p class="mt-4 text-sm font-medium text-green-600 dark:text-green-400">{m.score_added_success()}</p>
		{/if}
	</div>

	<div class="mb-4 flex items-center justify-between">
		<h1 class="text-fancy-title text-2xl font-bold text-foreground">{m.database_viewer()}</h1>
		{#if selectedScoreId}
			<div class="flex gap-2">
				<form method="POST" action="?/delete" use:enhance={() => {
					return async ({ update, result }) => {
						if (result.type === 'success') {
							selectedScoreId = null;
						}
						update();
					};
				}}>
					<input type="hidden" name="id" value={selectedScoreId} />
					<Button type="submit" variant="destructive">{m.delete()}</Button>
				</form>
				<Button href="/reader/{selectedScoreId}">{m.view_pdf()}</Button>
			</div>
		{/if}
	</div>
	
	<div class="flex flex-wrap items-center gap-4 py-4">
		<Input
			placeholder="Filter titles..."
			value={(table.getColumn("title")?.getFilterValue() as string) ?? ""}
			oninput={(e) => table.getColumn("title")?.setFilterValue(e.currentTarget.value)}
			class="max-w-xs"
		/>
		<Input
			placeholder="Filter composers..."
			value={(table.getColumn("composer")?.getFilterValue() as string) ?? ""}
			oninput={(e) => table.getColumn("composer")?.setFilterValue(e.currentTarget.value)}
			class="max-w-xs"
		/>
		<Input
			placeholder="Filter instrumentation..."
			value={(table.getColumn("instrumentation")?.getFilterValue() as string) ?? ""}
			oninput={(e) => table.getColumn("instrumentation")?.setFilterValue(e.currentTarget.value)}
			class="max-w-xs"
		/>
		<div class="flex items-center gap-2">
			<span class="text-sm font-medium">Year:</span>
			<Input
				type="number"
				placeholder="Min"
				value={((table.getColumn("year")?.getFilterValue() as [number, number])?.[0]) ?? ""}
				oninput={(e) => {
					const current = (table.getColumn("year")?.getFilterValue() as [number | undefined, number | undefined]) || [undefined, undefined];
					const val = e.currentTarget.value ? parseInt(e.currentTarget.value, 10) : undefined;
					table.getColumn("year")?.setFilterValue([val, current[1]]);
				}}
				class="w-20"
			/>
			<span>-</span>
			<Input
				type="number"
				placeholder="Max"
				value={((table.getColumn("year")?.getFilterValue() as [number, number])?.[1]) ?? ""}
				oninput={(e) => {
					const current = (table.getColumn("year")?.getFilterValue() as [number | undefined, number | undefined]) || [undefined, undefined];
					const val = e.currentTarget.value ? parseInt(e.currentTarget.value, 10) : undefined;
					table.getColumn("year")?.setFilterValue([current[0], val]);
				}}
				class="w-20"
			/>
		</div>
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
					</Table.Row>
				{/each}
			</Table.Header>
			<Table.Body>
				{#each table.getRowModel().rows as row (row.id)}
					<Table.Row 
						class="cursor-pointer transition-colors hover:bg-muted/50 {selectedScoreId === row.original.id ? 'bg-muted' : ''}"
						onclick={() => { selectedScoreId = row.original.id; sheetOpen = true; }}
					>
						{#each row.getVisibleCells() as cell (cell.id)}
							<Table.Cell class="max-w-[120px] truncate sm:max-w-[150px] md:max-w-[200px]">
								<FlexRender
									content={cell.column.columnDef.cell}
									context={cell.getContext()}
								/>
							</Table.Cell>
						{/each}
					</Table.Row>
				{:else}
					<Table.Row>
						<Table.Cell colspan={columns.length} class="text-center text-muted-foreground py-4">
							No scores found.
						</Table.Cell>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>

	<div class="flex items-center justify-end space-x-2 py-4">
		<div class="flex-1 text-sm text-muted-foreground">
			Page {table.getState().pagination.pageIndex + 1} of {Math.max(1, table.getPageCount())}
		</div>
		<Button
			variant="outline"
			size="sm"
			onclick={() => table.previousPage()}
			disabled={!table.getCanPreviousPage()}
		>
			Previous
		</Button>
		<Button
			variant="outline"
			size="sm"
			onclick={() => table.nextPage()}
			disabled={!table.getCanNextPage()}
		>
			Next
		</Button>
	</div>
</div>

<Sheet.Root bind:open={sheetOpen}>
	<Sheet.Content class="w-full overflow-y-auto sm:max-w-md">
		<Sheet.Header>
			<Sheet.Title>Score Details</Sheet.Title>
			<Sheet.Description>Full metadata for the selected score.</Sheet.Description>
		</Sheet.Header>
		{#if selectedScore}
			<div class="mt-6 flex flex-col gap-3">
				{#each Object.entries(selectedScore).filter(([k]) => !['id', 'user_id', 'pdf_path', 'number_of_plays', 'source', 'imslp_id'].includes(k)).sort(([a], [b]) => {
					const order = ['title', 'composer', 'year', 'period', 'instrumentation', 'short_description', 'key', 'genre', 'form', 'style', 'long_description', 'difficulty', 'notable_interpreters', 'notable_interpeters', 'youtube_url'];
					const idxA = order.indexOf(a);
					const idxB = order.indexOf(b);
					if (idxA !== -1 && idxB !== -1) return idxA - idxB;
					if (idxA !== -1) return -1;
					if (idxB !== -1) return 1;
					return a.localeCompare(b);
				}) as [key, value]}
					<div class="grid grid-cols-3 gap-2 border-b border-border pb-2 last:border-0">
						<span class="text-sm font-semibold capitalize text-foreground">
							{key.replace(/_/g, ' ')}
						</span>
						<span class="col-span-2 text-sm text-muted-foreground break-words">
							{#if key === 'youtube_url' && value}
								<a href={value} target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">
									Watch on YouTube
								</a>
							{:else}
								{value !== null && value !== '' ? value : '-'}
							{/if}
						</span>
					</div>
				{/each}
			</div>
			
			<div class="mt-8 flex flex-col gap-2">
				<Button href="/reader/{selectedScore.id}" class="w-full">View PDF</Button>
				<form method="POST" action="?/recomplete" use:enhance={() => {
					recompleting = true;
					return async ({ update, result }) => {
						recompleting = false;
						if (result.type === 'success') {
							await invalidateAll();
						}
						await update({ reset: false });
					};
				}}>
					<input type="hidden" name="id" value={selectedScore.id} />
					<input type="hidden" name="title" value={selectedScore.title} />
					<input type="hidden" name="composer" value={selectedScore.composer} />
					<input type="hidden" name="pdf_path" value={selectedScore.pdf_path || ''} />
					<Button type="submit" variant="secondary" class="w-full" disabled={recompleting}>
						{recompleting ? 'Running Agent...' : 'Rerun Complete Agent'}
					</Button>
				</form>
				<form method="POST" action="?/delete" use:enhance={() => {
					return async ({ update, result }) => {
						if (result.type === 'success') {
							sheetOpen = false;
							selectedScoreId = null;
						}
						update();
					};
				}}>
					<input type="hidden" name="id" value={selectedScore.id} />
					<Button type="submit" variant="destructive" class="w-full">Delete Score</Button>
				</form>
			</div>
		{/if}
	</Sheet.Content>
</Sheet.Root>

<Sheet.Root bind:open={imslpSheetOpen}>
	<Sheet.Content class="w-full overflow-y-auto sm:max-w-md">
		<Sheet.Header>
			<Sheet.Title>IMSLP Score Details</Sheet.Title>
			<Sheet.Description>Full metadata for the selected IMSLP score.</Sheet.Description>
		</Sheet.Header>
		{#if agentSelectedScore}
			<div class="mt-6 flex flex-col gap-3">
				{#each Object.entries(agentSelectedScore).filter(([k]) => !['id', 'user_id', 'pdf_path', 'number_of_plays', 'source', 'imslp_id', 'score_metadata'].includes(k)).sort(([a], [b]) => {
					const order = ['title', 'composer', 'year', 'period', 'instrumentation', 'short_description', 'key', 'genre', 'form', 'style', 'long_description', 'difficulty', 'notable_interpreters', 'notable_interpeters', 'youtube_url'];
					const idxA = order.indexOf(a);
					const idxB = order.indexOf(b);
					if (idxA !== -1 && idxB !== -1) return idxA - idxB;
					if (idxA !== -1) return -1;
					if (idxB !== -1) return 1;
					return a.localeCompare(b);
				}) as [key, value]}
					<div class="grid grid-cols-3 gap-2 border-b border-border pb-2 last:border-0">
						<span class="text-sm font-semibold capitalize text-foreground">
							{key.replace(/_/g, ' ')}
						</span>
						<span class="col-span-2 text-sm text-muted-foreground break-words">
							{#if key === 'permlink' && value}
								<a href={value as string} target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">
									View on IMSLP
								</a>
							{:else}
								{value !== null && value !== '' ? value : '-'}
							{/if}
						</span>
					</div>
				{/each}
			</div>
			
			<div class="mt-8 flex flex-col gap-4 border-t border-border pt-4">
				<h3 class="font-semibold text-foreground">Add this Score</h3>
				<p class="text-sm text-muted-foreground">
					1. Download PDF from IMSLP: <br/>
					<a href={agentSelectedScore.permlink} target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline break-all">{agentSelectedScore.permlink}</a>
				</p>
				<p class="text-sm text-muted-foreground">
					2. Upload the downloaded PDF below:
				</p>
				<form method="POST" action="?/add_imslp" enctype="multipart/form-data" use:enhance={() => {
					uploading = true;
					return async ({ update }) => {
						uploading = false;
						agentSelectedScore = null;
						imslpSheetOpen = false;
						update();
					};
				}} class="flex flex-col gap-4">
					<input type="hidden" name="imslp_id" value={agentSelectedScore.id} />
					<div class="space-y-2">
						<label for="agent_file_sheet" class="text-sm font-medium leading-none">PDF File</label>
						<Input id="agent_file_sheet" name="file" type="file" accept="application/pdf" required />
					</div>
					<Button type="submit" disabled={uploading} class="w-full">
						{uploading ? 'Adding...' : 'Add Score'}
					</Button>
				</form>
			</div>
		{/if}
	</Sheet.Content>
</Sheet.Root>
