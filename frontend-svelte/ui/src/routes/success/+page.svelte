<script lang="ts">
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import AgentChat from '$lib/components/AgentChat.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { mainAgentHistoryStore } from '$lib/stores/chat.svelte';
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

	let { form, data } = $props();
	let sheetOpen = $state(false);
	let selectedScoreDetails = $state<any>(null);

	let pagination = $state<PaginationState>({ pageIndex: 0, pageSize: 5 });
	let sorting = $state<SortingState>([]);
	let columnFilters = $state<ColumnFiltersState>([]);
	let currentScores = $state<any[]>([]);

	const columns: ColumnDef<any>[] = [
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

	const table = createSvelteTable({
		get data() { return currentScores; },
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

	function onResult(data: any) {
		let textAns = data.answer?.response;
		if (typeof textAns === 'object' && textAns !== null && 'response' in textAns) {
			textAns = textAns.response;
		}

		let scoreId = data.answer?.score_id || data.answer?.response?.score_id;
		const scores = data.scores || [];
		currentScores = scores;

		return {
			question: data.question,
			answer: {
				answer: typeof textAns === 'string' ? textAns : JSON.stringify(textAns, null, 2),
				score_id: scoreId,
				scoreDetails: data.scoreDetails,
				scores: scores
			},
			rawHistory: data.answer?.message_history
		};
	}
</script>

<div class="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto w-full">
	<AgentChat
		{form}
		action="?/ask"
		title={m.hello_user({ name: data.user.username })}
		emptyMessage={m.what_to_play()}
		placeholder={m.agent_placeholder_main()}
		{onResult}
		user={data.user}
		store={mainAgentHistoryStore}
	>
		{#snippet children()}
			<div />
		{/snippet}

		{#snippet resultSnippet({ msg, isLast })}
			<p class="mt-2 text-muted-foreground whitespace-pre-wrap">{msg.answer}</p>
			{#if isLast && msg.scores && msg.scores.length > 0}
				<div class="mt-4 overflow-hidden rounded-md border bg-card text-card-foreground shadow-card">
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
									class="cursor-pointer transition-colors hover:bg-muted/50 {selectedScoreDetails?.id === row.original.id ? 'bg-muted' : ''}"
									onclick={() => {
										selectedScoreDetails = row.original;
										sheetOpen = true;
									}}
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
							{/each}
						</Table.Body>
					</Table.Root>

					<div class="flex items-center justify-end space-x-2 py-4 px-4 border-t border-border">
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
			{/if}
			{#if msg.score_id}
				<div class="mt-4">
					<Button variant="secondary" size="sm" href="/reader/{msg.score_id}">
						Open PDF (Score ID: {msg.score_id})
					</Button>
				</div>
			{/if}
		{/snippet}
	</AgentChat>
</div>

<Sheet.Root bind:open={sheetOpen}>
	<Sheet.Content class="w-full overflow-y-auto sm:max-w-md">
		<Sheet.Header>
			<Sheet.Title>Score Details</Sheet.Title>
			<Sheet.Description>Full metadata for the selected score.</Sheet.Description>
		</Sheet.Header>
		{#if selectedScoreDetails}
			<div class="mt-6 flex flex-col gap-3">
				{#each Object.entries(selectedScoreDetails).filter(([k]) => !['id', 'user_id', 'pdf_path', 'number_of_plays', 'source', 'imslp_id'].includes(k)).sort(([a], [b]) => {
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
								<a href={value as string} target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">
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
				<Button href="/reader/{selectedScoreDetails.id}" class="w-full">View PDF</Button>
			</div>
		{/if}
	</Sheet.Content>
</Sheet.Root>
