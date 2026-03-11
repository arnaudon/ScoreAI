<script lang="ts">
	import { enhance } from '$app/forms';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Table from '$lib/components/ui/table/index.js';

	let { form } = $props();
	let history = $state<{question: string, answer: string, score_id?: number, scoreDetails?: any}[]>([]);
	let loading = $state(false);

	function clearHistory() {
		history = [];
	}
</script>

<div class="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto w-full">
	<h1 class="text-2xl font-bold mb-4 text-foreground">Agent</h1>

	<div class="flex-1 overflow-y-auto mb-4 space-y-4 pr-2">
		{#each history as msg}
			<div class="bg-muted p-4 rounded-lg">
				<p class="font-bold text-foreground">Q: {msg.question}</p>
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
								<Table.Row>
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
			</div>
		{/each}
		{#if loading}
			<div class="bg-muted p-4 rounded-lg animate-pulse">
				<p class="text-muted-foreground">Thinking...</p>
			</div>
		{/if}
	</div>

	<div class="bg-card border rounded-lg p-4 shadow-sm">
		<form method="POST" action="?/ask" use:enhance={() => {
			loading = true;
			return async ({ result, update }) => {
				loading = false;
				if (result.type === 'success' && result.data) {
					const data = result.data as any;
					if (data.success) {
						let textAns = data.answer?.response;
						if (typeof textAns === 'object' && textAns !== null && 'response' in textAns) {
							textAns = textAns.response;
						}
						
						let scoreId = data.answer?.score_id || data.answer?.response?.score_id;

						history.push({
							question: data.question,
							answer: typeof textAns === 'string' ? textAns : JSON.stringify(textAns, null, 2),
							score_id: scoreId,
							scoreDetails: data.scoreDetails
						});
					}
				}
				update({ reset: true });
			};
		}} class="flex gap-2">
			<Input name="question" placeholder="Question" required />
			<Button type="submit" disabled={loading}>Ask</Button>
		</form>

		{#if form?.error}
			<p class="mt-2 text-sm text-destructive">{form.error}</p>
		{/if}

		<div class="mt-4 flex justify-between items-end text-sm text-muted-foreground">
			<div>
				<p class="mb-2">Here is how to use me:</p>
				<ul class="list-disc list-inside space-y-1">
					<li>Ask me a question about a score or a composer</li>
					<li>I can give you a random score from a composer</li>
					<li>etc...</li>
				</ul>
			</div>
			<Button variant="outline" size="sm" onclick={clearHistory}>Clean history</Button>
		</div>
	</div>
</div>
