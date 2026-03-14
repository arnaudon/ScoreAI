<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import type { ActionResult } from '@sveltejs/kit';
	import type { Snippet } from 'svelte';
	import * as m from '$lib/paraglide/messages.js';

	type HistoryMessage = {
		question: string;
		[key: string]: any;
	};

	type HistoryStore = {
		history: HistoryMessage[];
		rawHistory: any[];
		clear: () => void;
	};

	let {
		form,
		action,
		title,
		placeholder,
		onResult,
		children,
		resultSnippet,
		user,
		store
	}: {
		form: any;
		action: string;
		title: string;
		placeholder: string;
		onResult: (result: any) => { question: string; answer: any; rawHistory?: any };
		children: Snippet;
		resultSnippet: Snippet<[{ msg: HistoryMessage; isLast: boolean }]>;
		user: any;
		store: HistoryStore;
	} = $props();

	let loading = $state(false);
	let scrollContainer: HTMLElement | undefined = $state();

	$effect(() => {
		store.history;
		loading;
		if (scrollContainer) {
			scrollContainer.scrollTop = scrollContainer.scrollHeight;
		}
	});

	function clearHistory() {
		store.clear();
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
			const success = result.type === 'success' && result.data?.success;
			if (success) {
				const data = result.data as any;
				const parsed = onResult(data);
				store.history = [
					...store.history,
					{
						question: parsed.question,
						...parsed.answer
					}
				];

				if (parsed.rawHistory) {
					store.rawHistory = parsed.rawHistory;
				}
			}
			await update({ reset: true });
			if (success) {
				await invalidateAll();
			}
		};
	}
</script>

<div class="flex flex-col h-full w-full {store.history.length === 0 && !loading ? 'justify-center' : ''}">
	<div class="mb-4">
		<h1 class="text-lg font-bold text-foreground">
			{title}{#if store.history.length === 0 && !loading} {m.how_can_i_help()}{/if}
		</h1>
	</div>

	<div class="overflow-y-auto space-y-4 pr-2 {store.history.length > 0 || loading ? 'mb-4' : ''}" bind:this={scrollContainer}>
		{#each store.history as msg, index}
			<div class="bg-muted p-4 rounded-lg">
				<p class="font-bold text-foreground">Q: {msg.question}</p>
				{@render resultSnippet({ msg, isLast: index === store.history.length - 1 })}
			</div>
		{/each}
		{#if loading}
			<div class="bg-muted p-4 rounded-lg animate-pulse">
				<p class="text-muted-foreground">Thinking...</p>
			</div>
		{/if}
	</div>

	<div class="bg-card border rounded-lg p-4 shadow-sm {store.history.length > 0 || loading ? 'mt-auto' : ''}">
		<form method="POST" {action} use:enhance={handleEnhance} class="flex gap-2">
			<input type="hidden" name="message_history" value={JSON.stringify(store.rawHistory)} />
			<Input name="question" {placeholder} required />
			<Button type="submit" disabled={loading}>{m.ask()}</Button>
		</form>

		{#if form?.error}
			<p class="mt-2 text-sm text-destructive">{form.error}</p>
		{/if}

		<div class="mt-4 flex justify-between items-end text-sm text-muted-foreground">
			{@render children()}
			<div class="flex items-center gap-4">
				{#if user?.credits !== undefined}
					<span class="font-medium">Credits: {user.credits}/{user.max_credits}</span>
				{/if}
				<Button variant="outline" size="sm" onclick={clearHistory}>{m.clean_history()}</Button>
			</div>
		</div>
	</div>
</div>
