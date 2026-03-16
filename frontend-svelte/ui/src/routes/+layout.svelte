<script lang="ts">
	import { page } from '$app/state';
	import { locales, localizeHref, setLocale } from '$lib/paraglide/runtime';
	import * as m from '$lib/paraglide/messages.js';
	import '../app.css';
	import AppSidebar from '$lib/components/Sidebar.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { ModeWatcher } from 'mode-watcher';
	import { onMount } from 'svelte';

	let { children, data } = $props();
	let showCookieBanner = $state(false);

	onMount(() => {
		if (!localStorage.getItem('cookie_consent')) {
			showCookieBanner = true;
		}
	});

	function acceptCookies() {
		localStorage.setItem('cookie_consent', 'true');
		showCookieBanner = false;
	}

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
			<footer class="p-4 text-sm text-muted-foreground flex flex-col md:flex-row items-center justify-between gap-4">
				<div class="text-xs text-center md:text-left w-full md:w-1/3">
					{m.beta_warning()} <a href="mailto:alexis.arnaudon@scoreguide.ch" class="text-primary hover:underline">alexis.arnaudon@scoreguide.ch</a>.
				</div>
				<div class="flex flex-wrap justify-center items-center gap-x-4 gap-y-2 w-full md:w-1/3">
					<a href="/terms" class="hover:underline">{m.terms_of_service()}</a>
					<a href="/privacy" class="hover:underline">{m.privacy_policy()}</a>
					<a href="/contact" class="hover:underline">{m.contact()}</a>
					<span>© 2026 Alexis Arnaudon</span>
				</div>
				<div class="hidden md:block w-full md:w-1/3"></div>
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
					<button onclick={() => setLanguage('en')} class="px-2 py-1 hover:bg-muted">
						EN
					</button>
					<div class="w-[1px] bg-border"></div>
					<button onclick={() => setLanguage('fr')} class="px-2 py-1 hover:bg-muted">
						FR
					</button>
				</div>
			</div>
			<div class="flex flex-col md:flex-row items-center justify-between gap-4">
				<div class="text-xs text-center md:text-left w-full md:w-1/3">
					{m.beta_warning()} <a href="mailto:alexis.arnaudon@scoreguide.ch" class="text-primary hover:underline">alexis.arnaudon@scoreguide.ch</a>.
				</div>
				<div class="flex flex-wrap justify-center items-center gap-x-4 gap-y-2 w-full md:w-1/3">
					<a href="/terms" class="hover:underline">{m.terms_of_service()}</a>
					<a href="/privacy" class="hover:underline">{m.privacy_policy()}</a>
					<a href="/contact" class="hover:underline">{m.contact()}</a>
					<span>© 2026 Alexis Arnaudon</span>
				</div>
				<div class="hidden md:block w-full md:w-1/3"></div>
			</div>
		</footer>
	</div>
{/if}

{#if showCookieBanner}
	<div class="fixed bottom-0 left-0 right-0 z-50 flex flex-col sm:flex-row items-center justify-between gap-4 bg-card p-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)] border-t border-border">
		<p class="text-sm text-card-foreground">{m.cookie_consent_msg()}</p>
		<button onclick={acceptCookies} class="whitespace-nowrap rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
			{m.cookie_consent_accept()}
		</button>
	</div>
{/if}

<div style="display:none">
	{#each locales as locale}
		<a href={localizeHref(page.url.pathname, { locale })}>{locale}</a>
	{/each}
</div>
