<script lang="ts">
	import type { PageProps } from './$types';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import * as m from '$lib/paraglide/messages.js';
	import { page } from '$app/state';

	let { data }: PageProps = $props();
	let sheetOpen = $state(false);
	let iframeEl: HTMLIFrameElement | undefined = $state();

	function enterPresentationMode() {
		if (iframeEl?.contentWindow?.document) {
			const button = iframeEl.contentWindow.document.getElementById('presentationMode');
			button?.click();
		}
	}

	function translateKey(key: string) {
		const map: Record<string, string> = {
			title: m.label_title(),
			composer: m.label_composer(),
			year: m.label_year(),
			period: m.label_period(),
			instrumentation: m.label_instrumentation(),
			short_description: m.label_short_description(),
			key: m.label_key_signature(),
			genre: m.label_genre(),
			form: m.label_form(),
			style: m.label_style(),
			long_description: m.label_long_description(),
			difficulty: m.label_difficulty(),
			notable_interpreters: m.label_notable_interpreters(),
			notable_interpeters: m.label_notable_interpreters(),
			youtube_url: m.label_youtube_url(),
			permlink: m.label_permlink()
		};
		return map[key] || key.replace(/_/g, ' ');
	}

	// Use the saved pdf_path from the database
	let filename = $derived(data.score?.pdf_path || '');
	
	// PDF.js viewer is hosted at /pdfjs/web/viewer.html.
	// We pass a relative URL to our own PDF proxy endpoint to avoid cross-origin issues.
	let pdfUrl = $derived(filename ? `/api/pdf/${encodeURIComponent(filename)}?token=${data.token}` : '');
	let viewerUrl = $derived(pdfUrl ? `/pdfjs/web/viewer.html?file=${encodeURIComponent(pdfUrl)}` : '');
</script>

<div class="h-full w-full p-4">
	{#if data.score}
		<div class="mb-4 flex items-center justify-between">
			<div>
				<h1 class="text-fancy-title text-2xl font-bold text-foreground">{data.score.title}</h1>
				<p class="text-muted-foreground">{data.score.composer}</p>
			</div>
			<div class="flex gap-2">
				<Button variant="outline" onclick={enterPresentationMode}>{m.presentation_mode()}</Button>
				<Button variant="outline" onclick={() => sheetOpen = true}>{m.view_details()}</Button>
			</div>
		</div>
		
		<div class="h-[calc(100vh-8rem)] rounded-md border bg-card shadow-card">
			{#if viewerUrl}
				<iframe
					bind:this={iframeEl}
					src={viewerUrl}
					class="w-full h-full border-0 rounded-md"
					title="PDF Viewer"
					allowfullscreen
				></iframe>
			{:else}
				<div class="flex h-full items-center justify-center text-muted-foreground">
					{m.no_pdf_available()}
				</div>
			{/if}
		</div>
	{:else}
		<div class="p-8 text-center text-muted-foreground">
			<h2 class="text-xl font-bold">{m.score_not_found()}</h2>
			<p>{m.score_not_found_desc()}</p>
		</div>
	{/if}
</div>

<Sheet.Root bind:open={sheetOpen}>
	<Sheet.Content class="w-full overflow-y-auto sm:max-w-md">
		<Sheet.Header>
			<Sheet.Title>{m.score_details()}</Sheet.Title>
			<Sheet.Description>{m.score_details_desc()}</Sheet.Description>
		</Sheet.Header>
		{#if data.score}
			<div class="mt-6 flex flex-col gap-3">
				{#each Object.entries(data.score).filter(([k]) => !['id', 'user_id', 'pdf_path', 'number_of_plays', 'source', 'imslp_id', 'short_description_fr', 'long_description_fr'].includes(k)).sort(([a], [b]) => {
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
							{translateKey(key)}
						</span>
						<span class="col-span-2 text-sm text-muted-foreground break-words">
							{#if key === 'youtube_url' && value}
								<a href={value as string} target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">
									{m.watch_on_youtube()}
								</a>
							{:else if (key === 'short_description' || key === 'long_description') && (page.url.pathname.startsWith('/fr/') || page.url.pathname === '/fr')}
								{data.score[key + '_fr'] || value || '-'}
							{:else}
								{value !== null && value !== '' ? value : '-'}
							{/if}
						</span>
					</div>
				{/each}
			</div>
		{/if}
	</Sheet.Content>
</Sheet.Root>
