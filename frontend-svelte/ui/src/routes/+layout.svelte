<script lang="ts">
	import { page } from '$app/state';
	import { locales, localizeHref, setLocale } from '$lib/paraglide/runtime';
	import * as m from '$lib/paraglide/messages.js';
	import '../app.css';
	import AppSidebar from '$lib/components/Sidebar.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { ModeWatcher } from 'mode-watcher';

	let { children, data } = $props();

	function setLanguage(lang: 'en' | 'fr') {
		setLocale(lang);
	}
</script>

<svelte:head>
	<title>ScoreGuide</title>
	<meta name="description" content="Your intelligent music score library. Upload, manage, and discover scores with AI-powered assistance." />
	<meta property="og:title" content="ScoreGuide" />
	<meta property="og:description" content="Your intelligent music score library. Upload, manage, and discover scores with AI-powered assistance." />
	<meta property="og:type" content="website" />
</svelte:head>

<ModeWatcher />

{#if data.loggedIn}
	<Sidebar.Provider style="--sidebar-width: 10rem;">
		<AppSidebar />
		<Sidebar.Inset class="flex w-full flex-1 flex-col bg-background text-foreground main-wrapper">
			<main class="w-full flex-1 overflow-y-auto p-8">
				<Sidebar.Trigger class="mb-4" />
				{@render children()}
			</main>
			<footer class="p-4 text-center text-sm text-muted-foreground">
				<div class="flex flex-wrap justify-center items-center gap-x-4 gap-y-2">
					<a href="/privacy" class="hover:underline">{m.privacy_policy()}</a>
					<a href="/contact" class="hover:underline">{m.contact()}</a>
					<span>© 2026 Alexis Arnaudon</span>
				</div>
			</footer>
		</Sidebar.Inset>
	</Sidebar.Provider>
{:else}
	<div class="flex min-h-screen flex-col bg-background text-foreground main-wrapper relative">
		<main class="w-full flex-1">
			{@render children()}
		</main>
		<footer class="p-4 text-center text-sm text-muted-foreground">
			<div class="mb-4 flex justify-center">
				<div class="flex rounded-md border text-xs font-semibold">
					<a href={localizeHref(page.url.pathname, { locale: 'en' })} class="px-2 py-1 hover:bg-muted">
						EN
					</a>
					<div class="w-[1px] bg-border"></div>
					<a href={localizeHref(page.url.pathname, { locale: 'fr' })} class="px-2 py-1 hover:bg-muted">
						FR
					</a>
				</div>
			</div>
			<div class="flex flex-wrap justify-center items-center gap-x-4 gap-y-2">
				<a href="/privacy" class="hover:underline">{m.privacy_policy()}</a>
				<a href="/contact" class="hover:underline">{m.contact()}</a>
				<span>© 2026 Alexis Arnaudon</span>
			</div>
		</footer>
	</div>
{/if}

<div style="display:none">
	{#each locales as locale}
		<a href={localizeHref(page.url.pathname, { locale })}>{locale}</a>
	{/each}
</div>
