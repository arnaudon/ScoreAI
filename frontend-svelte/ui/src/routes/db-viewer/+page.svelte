<script lang="ts">
	import type { PageProps } from './$types';
	import * as Table from '$lib/components/ui/table/index.js';
	import { Button } from '$lib/components/ui/button/index.js';

	let { data }: PageProps = $props();
	let selectedScoreId = $state<number | null>(null);
</script>

<div class="p-8">
	<div class="mb-4 flex items-center justify-between">
		<h1 class="text-2xl font-bold text-foreground">Database Viewer</h1>
		{#if selectedScoreId}
			<Button href="/reader/{selectedScoreId}">View PDF</Button>
		{/if}
	</div>
	
	<div class="rounded-md border bg-card text-card-foreground">
		<Table.Root>
			<Table.Header>
				<Table.Row>
					<Table.Head>ID</Table.Head>
					<Table.Head>Title</Table.Head>
					<Table.Head>Composer</Table.Head>
				</Table.Row>
			</Table.Header>
			<Table.Body>
				{#each data.scores as score}
					<Table.Row 
						class="cursor-pointer transition-colors hover:bg-muted/50 {selectedScoreId === score.id ? 'bg-muted' : ''}"
						onclick={() => selectedScoreId = score.id}
					>
						<Table.Cell>{score.id}</Table.Cell>
						<Table.Cell>{score.title}</Table.Cell>
						<Table.Cell>{score.composer}</Table.Cell>
					</Table.Row>
				{:else}
					<Table.Row>
						<Table.Cell colspan={3} class="text-center text-muted-foreground py-4">
							No scores found.
						</Table.Cell>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>
</div>
