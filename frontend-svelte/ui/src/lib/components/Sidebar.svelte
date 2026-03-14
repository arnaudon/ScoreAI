<script lang="ts">
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import DarkModeToggle from './DarkModeToggle.svelte';
	import { page } from '$app/state';
	import { setLocale } from '$lib/paraglide/runtime';
	import * as m from '$lib/paraglide/messages.js';

	function setLanguage(lang: 'en' | 'fr') {
		setLocale(lang);
	}
</script>

<Sidebar.Root>
	<Sidebar.Header class="p-4 border-b">
		<h2 class="text-xl font-bold text-foreground">ScoreGuide</h2>
	</Sidebar.Header>
	<Sidebar.Content>
		<Sidebar.Group>
			<Sidebar.GroupContent>
				<Sidebar.Menu>
					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a href="/" {...props}>{m.nav_home()}</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>
					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a href="/db-viewer" {...props}>{m.nav_db_viewer()}</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>
					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a href="/reader" {...props}>{m.nav_pdf_viewer()}</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>
					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a href="/account" {...props}>{m.nav_account()}</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>
					{#if page.data.isAdmin}
						<Sidebar.MenuItem>
							<Sidebar.MenuButton>
								{#snippet child({ props })}
									<a href="/admin" {...props}>{m.nav_admin()}</a>
								{/snippet}
							</Sidebar.MenuButton>
						</Sidebar.MenuItem>
					{/if}
				</Sidebar.Menu>
			</Sidebar.GroupContent>
		</Sidebar.Group>
	</Sidebar.Content>
	<Sidebar.Footer class="p-4 gap-4">
		<Sidebar.Menu>
			<Sidebar.MenuItem>
				<Sidebar.MenuButton>
					{#snippet child({ props })}
						<form method="POST" action="/logout" class="w-full">
							<button type="submit" {...props} class="w-full text-left">{m.nav_logout()}</button>
						</form>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		</Sidebar.Menu>
		<div class="flex items-center gap-2">
			<DarkModeToggle />
			<div class="flex rounded-md border text-xs font-semibold">
				<button onclick={() => setLanguage('en')} class="p-2 hover:bg-muted">
					EN
				</button>
				<div class="w-[1px] bg-border"></div>
				<button onclick={() => setLanguage('fr')} class="p-2 hover:bg-muted">
					FR
				</button>
			</div>
		</div>
	</Sidebar.Footer>
</Sidebar.Root>
