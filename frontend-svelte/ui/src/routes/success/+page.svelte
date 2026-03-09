<script lang="ts">
	import { enhance } from '$app/forms';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Button } from '$lib/components/ui/button/index.js';

	let { form } = $props();
	let history = $state<{question: string, answer: string, score_id?: number}[]>([]);
	let loading = $state(false);

	function clearHistory() {
		history = [];
	}
</script>

<div class="flex flex-col h-full max-w-4xl mx-auto py-8 px-4">
	<h1 class="text-2xl font-bold mb-4 text-foreground">Agent</h1>

	<div class="flex-1 overflow-y-auto mb-4 space-y-4 min-h-[50vh]">
		{#each history as msg}
			<div class="bg-muted p-4 rounded-lg">
				<p class="font-bold text-foreground">Q: {msg.question}</p>
				<p class="mt-2 text-muted-foreground whitespace-pre-wrap">{msg.answer}</p>
				{#if msg.score_id}
					<div class="mt-4">
						<Button variant="secondary" size="sm">Open PDF (Score ID: {msg.score_id})</Button>
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
						let answerText = data.answer?.response;
						if (typeof answerText === 'object') {
							answerText = JSON.stringify(answerText, null, 2);
						} else if (!answerText) {
							answerText = typeof data.answer === 'object' ? JSON.stringify(data.answer, null, 2) : String(data.answer);
						}
						
						history.push({
							question: data.question,
							answer: answerText,
							score_id: data.answer?.score_id
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
