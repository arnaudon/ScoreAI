<script lang="ts">
	import type { PageProps } from './$types';
	import { enhance } from '$app/forms';
	import * as Table from '$lib/components/ui/table/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';

	let { data, form }: PageProps = $props();
	let selectedScoreId = $state<number | null>(null);
	let uploading = $state(false);
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
				<Table.Row>
					<Table.Head>Title</Table.Head>
					<Table.Head>Composer</Table.Head>
					<Table.Head>Year</Table.Head>
					<Table.Head>Period</Table.Head>
					<Table.Head>Genre</Table.Head>
				</Table.Row>
			</Table.Header>
			<Table.Body>
				{#each data.scores as score}
					<Table.Row 
						class="cursor-pointer transition-colors hover:bg-muted/50 {selectedScoreId === score.id ? 'bg-muted' : ''}"
						onclick={() => selectedScoreId = score.id}
					>
						<Table.Cell>{score.title}</Table.Cell>
						<Table.Cell>{score.composer}</Table.Cell>
						<Table.Cell>{score.year}</Table.Cell>
						<Table.Cell>{score.period}</Table.Cell>
						<Table.Cell>{score.genre}</Table.Cell>
					</Table.Row>
				{:else}
					<Table.Row>
						<Table.Cell colspan={5} class="text-center text-muted-foreground py-4">
							No scores found.
						</Table.Cell>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>
</div>
