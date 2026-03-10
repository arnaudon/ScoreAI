<script lang="ts">
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	// Use the saved pdf_path from the database
	let filename = $derived(data.score?.pdf_path || '');
	
	// PDF.js viewer is hosted at /pdfjs/web/viewer.html on the backend
	// We pass the absolute URL to ensure PDF.js correctly parses the query parameters instead of URL-encoding them into the filename
	let pdfUrl = $derived(filename ? `${data.backendUrl}/pdf/${encodeURIComponent(filename)}?token=${data.token}` : '');
	let viewerUrl = $derived(pdfUrl ? `${data.backendUrl}/pdfjs/web/viewer.html?file=${encodeURIComponent(pdfUrl)}` : '');
</script>

<div class="h-full w-full p-4">
	{#if data.score}
		<div class="mb-4 flex items-center justify-between">
			<h1 class="text-2xl font-bold text-foreground">{data.score.title}</h1>
			<p class="text-muted-foreground">{data.score.composer}</p>
		</div>
		
		<div class="rounded-md border bg-card shadow-sm h-[calc(100vh-8rem)]">
			{#if viewerUrl}
				<iframe 
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
