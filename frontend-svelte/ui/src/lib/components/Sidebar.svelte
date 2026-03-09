<script lang="ts">
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import DarkModeToggle from './DarkModeToggle.svelte';
</script>

<Sidebar.Root>
	<Sidebar.Header class="p-4 border-b">
		<h2 class="text-xl font-bold text-foreground">App Menu</h2>
	</Sidebar.Header>
	<Sidebar.Content>
		<Sidebar.Group>
			<Sidebar.GroupContent>
				<Sidebar.Menu>
					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a href="/" {...props}>Home</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>
					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a href="/login" {...props}>Login</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>
					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a href="/db-viewer" {...props}>Database Viewer</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>
				</Sidebar.Menu>
			</Sidebar.GroupContent>
		</Sidebar.Group>
	</Sidebar.Content>
	<Sidebar.Footer class="p-4">
		<DarkModeToggle />
	</Sidebar.Footer>
</Sidebar.Root>
