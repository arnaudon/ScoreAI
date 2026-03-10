<script lang="ts">
	import type { PageProps } from './$types';
	import { enhance } from '$app/forms';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { type ColumnDef, getCoreRowModel } from '@tanstack/table-core';
	import { FlexRender, createSvelteTable } from '$lib/components/ui/data-table/index.js';

	let { data, form }: PageProps = $props();
	let selectedScoreId = $state<number | null>(null);
	let uploading = $state(false);
	let sheetOpen = $state(false);
	let selectedScore = $derived(data.scores.find((s: any) => s.id === selectedScoreId));

	const columns: ColumnDef<any>[] = [
		{ accessorKey: 'title', header: 'Title' },
		{ accessorKey: 'composer', header: 'Composer' },
		{ accessorKey: 'year', header: 'Year' },
		{ accessorKey: 'period', header: 'Period' },
		{ accessorKey: 'genre', header: 'Genre' }
	];

	const table = createSvelteTable({
		get data() {
			return data.scores;
		},
		columns,
		getCoreRowModel: getCoreRowModel()
	});
</script>

<div class="p-8">
	<div class="mb-8 rounded-md border bg-card p-4 shadow-sm text-card-foreground">
		<h2 class="mb-4 text-lg font-semibold">Add New Score</h2>
		<form method="POST" action="?/upload" enctype="multipart/form-data" use:enhance={() => {
			uploading = true;
			return async ({ update }) => {
				uploading = false;
				update();
			};
		}} class="flex flex-col gap-4 md:flex-row md:items-end">
			<div class="flex-1 space-y-2">
				<label for="title" class="text-sm font-medium leading-none">Title</label>
				<Input id="title" name="title" required />
			</div>
			<div class="flex-1 space-y-2">
				<label for="composer" class="text-sm font-medium leading-none">Composer</label>
				<Input id="composer" name="composer" required />
			</div>
			<div class="flex-1 space-y-2">
				<label for="file" class="text-sm font-medium leading-none">PDF File</label>
				<Input id="file" name="file" type="file" accept="application/pdf" required />
			</div>
			<Button type="submit" disabled={uploading}>
				{uploading ? 'Uploading...' : 'Upload & Save'}
			</Button>
		</form>
		{#if form?.error}
			<p class="mt-4 text-sm font-medium text-destructive">{form.error}</p>
		{/if}
		{#if form?.success}
			<p class="mt-4 text-sm font-medium text-green-600 dark:text-green-400">Score added successfully!</p>
		{/if}
	</div>

	<div class="mb-4 flex items-center justify-between">
		<h1 class="text-2xl font-bold text-foreground">Database Viewer</h1>
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
					<Button type="submit" variant="destructive">Delete</Button>
				</form>
				<Button href="/reader/{selectedScoreId}">View PDF</Button>
			</div>
		{/if}
	</div>
	
	<div class="rounded-md border bg-card text-card-foreground">
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
							<Table.Cell>
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
</div>

<Sheet.Root bind:open={sheetOpen}>
	<Sheet.Content class="w-full overflow-y-auto sm:max-w-md">
		<Sheet.Header>
			<Sheet.Title>Score Details</Sheet.Title>
			<Sheet.Description>Full metadata for the selected score.</Sheet.Description>
		</Sheet.Header>
		{#if selectedScore}
			<div class="mt-6 flex flex-col gap-3">
				{#each Object.entries(selectedScore) as [key, value]}
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
