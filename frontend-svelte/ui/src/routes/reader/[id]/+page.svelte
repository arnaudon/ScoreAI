<script lang="ts">
	import type { PageProps } from './$types';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';

	let { data }: PageProps = $props();
	let sheetOpen = $state(false);
	let iframeEl: HTMLIFrameElement | undefined = $state();

	function enterPresentationMode() {
		if (iframeEl?.contentWindow?.document) {
			const button = iframeEl.contentWindow.document.getElementById('presentationMode');
			button?.click();
		}
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
				<h1 class="text-2xl font-bold text-foreground">{data.score.title}</h1>
				<p class="text-muted-foreground">{data.score.composer}</p>
			</div>
			<div class="flex gap-2">
				<Button variant="outline" onclick={enterPresentationMode}>Presentation Mode</Button>
				<Button variant="outline" onclick={() => sheetOpen = true}>View Details</Button>
			</div>
		</div>
		
		<div class="rounded-md border bg-card shadow-sm h-[calc(100vh-8rem)]">
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
					No PDF available for this score.
				</div>
			{/if}
		</div>
	{:else}
		<div class="p-8 text-center text-muted-foreground">
			<h2 class="text-xl font-bold">Score not found.</h2>
			<p>We could not find the details for this score.</p>
		</div>
	{/if}
</div>

<Sheet.Root bind:open={sheetOpen}>
	<Sheet.Content class="w-full overflow-y-auto sm:max-w-md">
		<Sheet.Header>
			<Sheet.Title>Score Details</Sheet.Title>
			<Sheet.Description>Full metadata for the selected score.</Sheet.Description>
		</Sheet.Header>
		{#if data.score}
			<div class="mt-6 flex flex-col gap-3">
				{#each Object.entries(data.score) as [key, value]}
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
		{/if}
	</Sheet.Content>
</Sheet.Root>
