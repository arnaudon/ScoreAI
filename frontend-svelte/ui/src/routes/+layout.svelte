<script lang="ts">
	import { page } from '$app/state';
	import { locales, localizeHref } from '$lib/paraglide/runtime';
	import '../app.css';
	import AppSidebar from '$lib/components/Sidebar.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { ModeWatcher } from 'mode-watcher';

	let { children, data } = $props();
</script>

<ModeWatcher />

{#if data.loggedIn}
	<Sidebar.Provider>
		<AppSidebar />
		<Sidebar.Inset class="w-full flex-1 bg-background text-foreground">
			<main class="w-full h-full overflow-y-auto p-8">
				<Sidebar.Trigger class="mb-4" />
				{@render children()}
			</main>
		</Sidebar.Inset>
	</Sidebar.Provider>
{:else}
	<main class="w-full min-h-screen bg-background text-foreground overflow-y-auto">
		{@render children()}
	</main>
{/if}

<div style="display:none">
	{#each locales as locale}
		<a href={localizeHref(page.url.pathname, { locale })}>{locale}</a>
	{/each}
</div>
