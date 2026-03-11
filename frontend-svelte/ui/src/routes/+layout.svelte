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
	<Sidebar.Provider style="--sidebar-width: 10rem;">
		<AppSidebar />
		<Sidebar.Inset class="flex w-full flex-1 flex-col bg-background text-foreground">
			<main class="w-full flex-1 overflow-y-auto p-8">
				<Sidebar.Trigger class="mb-4" />
				{@render children()}
			</main>
			<footer class="p-4 text-center text-sm text-muted-foreground">
				© 2026 Alexis Arnaudon. Contact:
				<a href="mailto:alexis.arnaudon@gmail.com" class="hover:underline">
					alexis.arnaudon@gmail.com
				</a>
			</footer>
		</Sidebar.Inset>
	</Sidebar.Provider>
{:else}
	<div class="flex min-h-screen flex-col bg-background text-foreground">
		<main class="w-full flex-1">
			{@render children()}
		</main>
		<footer class="p-4 text-center text-sm text-muted-foreground">
			© 2026 Alexis Arnaudon. Contact:
			<a href="mailto:alexis.arnaudon@gmail.com" class="hover:underline">
				alexis.arnaudon@gmail.com
			</a>
		</footer>
	</div>
{/if}

<div style="display:none">
	{#each locales as locale}
		<a href={localizeHref(page.url.pathname, { locale })}>{locale}</a>
	{/each}
</div>
