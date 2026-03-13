<script lang="ts">
	import type { PageProps } from './$types';
	import * as Table from '$lib/components/ui/table/index.js';
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';

	let { data }: PageProps = $props();

	$effect(() => {
		if (data.progress?.status === 'processing' || data.progress?.status === 'cancelling') {
			const interval = setInterval(() => {
				invalidateAll();
			}, 2000);
			return () => clearInterval(interval);
		}
	});
</script>

<div class="mb-4 flex items-center justify-between">
	<h1 class="text-fancy-title text-2xl font-bold text-foreground">Admin Dashboard</h1>
</div>

<div class="grid gap-6 md:grid-cols-2 mb-8">
	<div class="rounded-md border bg-card p-6 text-card-foreground shadow-card">
		<h2 class="text-fancy-title mb-2 text-xl font-semibold">Agent Configuration</h2>
		<p class="mb-4 text-muted-foreground">Select the global model used by agents.</p>
		<form method="POST" action="?/set_model" use:enhance class="flex gap-4 items-end">
			<div class="flex-1 space-y-2">
				<label for="model" class="text-sm font-medium leading-none">Agent Model</label>
				<select id="model" name="model" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
					<option value="openai:gpt-4o" selected={data.activeModel === 'openai:gpt-4o' || data.activeModel === ''}>GPT-4o</option>
					<option value="openai:gpt-4o-mini" selected={data.activeModel === 'openai:gpt-4o-mini'}>GPT-4o-Mini</option>
					<option value="anthropic:claude-3-5-sonnet-latest" selected={data.activeModel === 'anthropic:claude-3-5-sonnet-latest'}>Claude 3.5 Sonnet</option>
				</select>
			</div>
			<button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2" type="submit">
				Save
			</button>
		</form>
	</div>

	<div class="rounded-md border bg-card p-6 text-card-foreground shadow-card">
		<h2 class="text-fancy-title mb-2 text-xl font-semibold">IMSLP Database</h2>
		<p class="mb-4 text-muted-foreground">
			The database contains {data.stats?.total_works || 0} works and {data.stats?.total_composers || 0} composers.
		</p>
		<div class="flex gap-4 items-center">
			<form method="POST" action="?/update" use:enhance>
				<button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2" disabled={data.progress?.status === 'processing'}>
					Update Database
				</button>
			</form>
			<form method="POST" action="?/empty" use:enhance onsubmit={(e) => {
				if (!confirm('Are you sure you want to delete all IMSLP data?')) e.preventDefault();
			}}>
				<button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-destructive text-destructive-foreground hover:bg-destructive/90 h-10 px-4 py-2" disabled={data.progress?.status === 'processing'}>
					Delete All Data
				</button>
			</form>
		</div>

		{#if data.progress?.status === 'processing' || data.progress?.status === 'cancelling'}
			<div class="mt-6 p-4 border rounded-md bg-muted/50">
				<div class="flex justify-between mb-2">
					<span class="font-medium text-sm">
						{#if data.progress.status === 'cancelling'}
							Status: CANCELLING... (finishing current item)
						{:else}
							Status: PROCESSING PAGE ({data.progress.page}/{data.progress.total})
						{/if}
					</span>
				</div>
				<div class="w-full bg-secondary rounded-full h-2.5 mb-4 overflow-hidden">
					<div class="bg-primary h-2.5 rounded-full transition-all" style="width: {(data.progress.page / Math.max(1, data.progress.total)) * 100}%"></div>
				</div>
				<form method="POST" action="?/cancel" use:enhance>
					<button 
						disabled={data.progress.status === 'cancelling'}
						class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 rounded-md px-3 disabled:opacity-50"
					>
						{data.progress.status === 'cancelling' ? '⏳ Cancelling...' : '🛑 Cancel Task'}
					</button>
				</form>
			</div>
		{/if}
	</div>
</div>

<div class="mb-4 flex items-center justify-between">
	<h2 class="text-fancy-title text-xl font-semibold text-foreground">Users</h2>
</div>

<div class="rounded-md border bg-card text-card-foreground shadow-card">
	<Table.Root>
		<Table.Header>
			<Table.Row>
				<Table.Head>ID</Table.Head>
				<Table.Head>Username</Table.Head>
				<Table.Head>Role</Table.Head>
			</Table.Row>
		</Table.Header>
		<Table.Body>
			{#each data.users as user}
				<Table.Row>
					<Table.Cell>{user.id || '-'}</Table.Cell>
					<Table.Cell>{user.username}</Table.Cell>
					<Table.Cell class="capitalize">{user.role || (user.is_admin ? 'Admin' : 'User')}</Table.Cell>
				</Table.Row>
			{:else}
				<Table.Row>
					<Table.Cell colspan={3} class="text-center text-muted-foreground py-4">
						No users found.
					</Table.Cell>
				</Table.Row>
			{/each}
		</Table.Body>
	</Table.Root>
</div>
