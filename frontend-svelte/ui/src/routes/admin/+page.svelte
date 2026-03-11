<script lang="ts">
	import type { PageProps } from './$types';
	import * as Table from '$lib/components/ui/table/index.js';
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';

	let { data }: PageProps = $props();

	$effect(() => {
		if (data.progress?.status === 'processing') {
			const interval = setInterval(() => {
				invalidateAll();
			}, 2000);
			return () => clearInterval(interval);
		}
	});
</script>

<div class="mb-4 flex items-center justify-between">
	<h1 class="text-2xl font-bold text-foreground">Admin Dashboard</h1>
</div>

<div class="grid gap-6 md:grid-cols-2 mb-8">
	<div class="rounded-md border bg-card p-6 text-card-foreground shadow-sm">
		<h2 class="text-xl font-semibold mb-2">IMSLP Database</h2>
		<p class="mb-4 text-muted-foreground">
			The database contains {data.stats?.total_works || 0} works and {data.stats?.total_composers || 0} composers.
		</p>
		<div class="flex gap-4 items-center">
			<form method="POST" action="?/update" use:enhance class="flex gap-2">
				<input type="number" name="max_pages" value="300" min="1" class="flex h-10 w-24 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" disabled={data.progress?.status === 'processing'} />
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

		{#if data.progress?.status === 'processing'}
			<div class="mt-6 p-4 border rounded-md bg-muted/50">
				<div class="flex justify-between mb-2">
					<span class="font-medium text-sm">Status: PROCESSING PAGE ({data.progress.page}/{data.progress.total})</span>
				</div>
				<div class="w-full bg-secondary rounded-full h-2.5 mb-4 overflow-hidden">
					<div class="bg-primary h-2.5 rounded-full transition-all" style="width: {(data.progress.page / Math.max(1, data.progress.total)) * 100}%"></div>
				</div>
				<form method="POST" action="?/cancel" use:enhance>
					<button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 rounded-md px-3">
						🛑 Cancel Task
					</button>
				</form>
			</div>
		{:else if data.progress?.status === 'completed'}
			<div class="mt-6 p-4 border rounded-md bg-green-500/10 text-green-600 border-green-500/20">
				Task Finished!
			</div>
		{/if}
	</div>
</div>

<div class="mb-4 flex items-center justify-between">
	<h2 class="text-xl font-semibold text-foreground">Users</h2>
</div>

<div class="rounded-md border bg-card text-card-foreground">
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
