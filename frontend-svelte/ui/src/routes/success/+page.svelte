<script lang="ts">
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import AgentChat from '$lib/components/AgentChat.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { mainAgentHistoryStore } from '$lib/stores/chat.svelte';

	let { form, data } = $props();
	let sheetOpen = $state(false);
	let selectedScoreDetails = $state<any>(null);

	function onResult(data: any) {
		let textAns = data.answer?.response;
		if (typeof textAns === 'object' && textAns !== null && 'response' in textAns) {
			textAns = textAns.response;
		}

		let scoreId = data.answer?.score_id || data.answer?.response?.score_id;

		return {
			question: data.question,
			answer: {
				answer: typeof textAns === 'string' ? textAns : JSON.stringify(textAns, null, 2),
				score_id: scoreId,
				scoreDetails: data.scoreDetails
			},
			rawHistory: data.answer?.message_history
		};
	}
</script>

<div class="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto w-full">
	<AgentChat
		{form}
		action="?/ask"
		title="Agent"
		placeholder="Question"
		{onResult}
		user={data.user}
		store={mainAgentHistoryStore}
	>
		{#snippet children()}
			<div>
				<p class="mb-2">Here is how to use me:</p>
				<ul class="list-disc list-inside space-y-1">
					<li>Ask me a question about a score or a composer</li>
					<li>I can give you a random score from a composer</li>
					<li>etc...</li>
				</ul>
			</div>
		{/snippet}

		{#snippet resultSnippet({ msg })}
			<p class="mt-2 text-muted-foreground whitespace-pre-wrap">{msg.answer}</p>
			{#if msg.scoreDetails}
				<div class="mt-4 rounded-md border bg-card text-card-foreground">
					<Table.Root>
						<Table.Header>
							<Table.Row>
								<Table.Head>ID</Table.Head>
								<Table.Head>Title</Table.Head>
								<Table.Head>Composer</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							<Table.Row
								class="cursor-pointer transition-colors hover:bg-muted/50"
								onclick={() => {
									selectedScoreDetails = msg.scoreDetails;
									sheetOpen = true;
								}}
							>
								<Table.Cell>{msg.scoreDetails.id}</Table.Cell>
								<Table.Cell>{msg.scoreDetails.title}</Table.Cell>
								<Table.Cell>{msg.scoreDetails.composer}</Table.Cell>
							</Table.Row>
						</Table.Body>
					</Table.Root>
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
				{#each Object.entries(selectedScoreDetails) as [key, value]}
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
