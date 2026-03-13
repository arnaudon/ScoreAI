<script lang="ts">
	import { enhance } from '$app/forms';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import type { ActionResult } from '@sveltejs/kit';
	import type { Snippet } from 'svelte';

	type HistoryMessage = {
		question: string;
		[key: string]: any;
	};

	let {
		form,
		action,
		title,
		placeholder,
		onResult,
		children,
		resultSnippet
	}: {
		form: any;
		action: string;
		title: string;
		placeholder: string;
		onResult: (result: any) => { question: string; answer: any; rawHistory?: any };
		children: Snippet;
		resultSnippet: Snippet<[{ msg: HistoryMessage; isLast: boolean }]>;
	} = $props();

	let history = $state<HistoryMessage[]>([]);
	let rawHistory = $state<any[]>([]);
	let loading = $state(false);
	let scrollContainer: HTMLElement | undefined = $state();

	$effect(() => {
		history;
		loading;
		if (scrollContainer) {
			scrollContainer.scrollTop = scrollContainer.scrollHeight;
		}
	});

	function clearHistory() {
		history = [];
		rawHistory = [];
	}

	function handleEnhance() {
		loading = true;
		return async ({
			result,
			update
		}: {
			result: ActionResult;
			update: (options?: { reset?: boolean }) => Promise<void>;
		}) => {
			loading = false;
			if (result.type === 'success' && result.data?.success) {
				const data = result.data as any;
				const parsed = onResult(data);
				history.push({
					question: parsed.question,
					...parsed.answer
				});

				if (parsed.rawHistory) {
					rawHistory = parsed.rawHistory;
				}
			}
			update({ reset: true });
		};
	}
</script>

<div class="flex flex-col h-full w-full">
	<h1 class="text-2xl font-bold mb-4 text-foreground">{title}</h1>

	<div class="flex-1 overflow-y-auto mb-4 space-y-4 pr-2" bind:this={scrollContainer}>
		{#each history as msg, index}
			<div class="bg-muted p-4 rounded-lg">
				<p class="font-bold text-foreground">Q: {msg.question}</p>
				{@render resultSnippet({ msg, isLast: index === history.length - 1 })}
			</div>
		{/each}
		{#if loading}
			<div class="bg-muted p-4 rounded-lg animate-pulse">
				<p class="text-muted-foreground">Thinking...</p>
			</div>
		{/if}
	</div>

	<div class="bg-card border rounded-lg p-4 shadow-sm">
		<form method="POST" {action} use:enhance={handleEnhance} class="flex gap-2">
			<input type="hidden" name="message_history" value={JSON.stringify(rawHistory)} />
			<Input name="question" {placeholder} required />
			<Button type="submit" disabled={loading}>Ask</Button>
		</form>

		{#if form?.error}
			<p class="mt-2 text-sm text-destructive">{form.error}</p>
		{/if}

		<div class="mt-4 flex justify-between items-end text-sm text-muted-foreground">
			{@render children()}
			<Button variant="outline" size="sm" onclick={clearHistory}>Clean history</Button>
		</div>
	</div>
</div>
