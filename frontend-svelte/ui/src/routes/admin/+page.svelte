<script lang="ts">
	import type { PageProps } from './$types';
	import * as Table from '$lib/components/ui/table/index.js';
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import { Input } from '$lib/components/ui/input/index.js';

	let { data }: PageProps = $props();

	let selectedUser = $state<any>(null);
	let max_credits = $state(0);
	let editDialogOpen = $state(false);

	function openEditDialog(user: any) {
		selectedUser = user;
		max_credits = user.max_credits ?? 50;
		editDialogOpen = true;
	}

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
		<p class="mb-4 text-muted-foreground">Select the models used by the different agents.</p>
		<form method="POST" action="?/set_models" use:enhance class="flex flex-col gap-4">
			<div class="space-y-2">
				<label for="model_main" class="text-sm font-medium leading-none">Main Agent Model</label>
				<select id="model_main" name="model_main" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
					<option value="google-gla:gemini-2.5-flash" selected={data.activeModels.main === 'google-gla:gemini-2.5-flash' || data.activeModels.main === ''}>Gemini 2.5 Flash</option>
					<option value="google-gla:gemini-2.5-pro" selected={data.activeModels.main === 'google-gla:gemini-2.5-pro'}>Gemini 2.5 Pro</option>
					<option value="google-gla:gemini-3-pro-preview" selected={data.activeModels.main === 'google-gla:gemini-3-pro-preview'}>Gemini 3 Pro Preview</option>
				</select>
			</div>
			<div class="space-y-2">
				<label for="model_imslp" class="text-sm font-medium leading-none">IMSLP Agent Model</label>
				<select id="model_imslp" name="model_imslp" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
					<option value="google-gla:gemini-2.5-flash" selected={data.activeModels.imslp === 'google-gla:gemini-2.5-flash' || data.activeModels.imslp === ''}>Gemini 2.5 Flash</option>
					<option value="google-gla:gemini-2.5-pro" selected={data.activeModels.imslp === 'google-gla:gemini-2.5-pro'}>Gemini 2.5 Pro</option>
					<option value="google-gla:gemini-3-pro-preview" selected={data.activeModels.imslp === 'google-gla:gemini-3-pro-preview'}>Gemini 3 Pro Preview</option>
				</select>
			</div>
			<div class="space-y-2">
				<label for="model_complete" class="text-sm font-medium leading-none">Complete Agent Model</label>
				<select id="model_complete" name="model_complete" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
					<option value="google-gla:gemini-2.5-flash" selected={data.activeModels.complete === 'google-gla:gemini-2.5-flash' || data.activeModels.complete === ''}>Gemini 2.5 Flash</option>
					<option value="google-gla:gemini-2.5-pro" selected={data.activeModels.complete === 'google-gla:gemini-2.5-pro'}>Gemini 2.5 Pro</option>
					<option value="google-gla:gemini-3-pro-preview" selected={data.activeModels.complete === 'google-gla:gemini-3-pro-preview'}>Gemini 3 Pro Preview</option>
				</select>
			</div>
			<button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 self-start" type="submit">
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
				<Table.Head>Credits</Table.Head>
				<Table.Head class="text-right">Actions</Table.Head>
			</Table.Row>
		</Table.Header>
		<Table.Body>
			{#each data.users as user}
				<Table.Row>
					<Table.Cell>{user.id || '-'}</Table.Cell>
					<Table.Cell>{user.username}</Table.Cell>
					<Table.Cell class="capitalize">{user.role || (user.is_admin ? 'Admin' : 'User')}</Table.Cell>
					<Table.Cell>{user.credits ?? '-'}/{user.max_credits ?? '-'}</Table.Cell>
					<Table.Cell class="text-right">
						<div class="flex items-center justify-end gap-2">
							<Button variant="outline" size="sm" onclick={() => openEditDialog(user)}>Edit</Button>
							<form method="POST" action="?/refill_credits" use:enhance>
								<input type="hidden" name="user_id" value={user.id} />
								<Button
									variant="outline"
									size="sm"
									type="submit"
									disabled={user.credits === user.max_credits}
								>
									Refill
								</Button>
							</form>
						</div>
					</Table.Cell>
				</Table.Row>
			{:else}
				<Table.Row>
					<Table.Cell colspan={5} class="text-center text-muted-foreground py-4">
						No users found.
					</Table.Cell>
				</Table.Row>
			{/each}
		</Table.Body>
	</Table.Root>
</div>

<Sheet.Root bind:open={editDialogOpen}>
	<Sheet.Content>
		<Sheet.Header>
			<Sheet.Title>Edit Max Credits for {selectedUser?.username}</Sheet.Title>
			<Sheet.Description>
				Set the maximum credit balance for the user.
			</Sheet.Description>
		</Sheet.Header>
		{#if selectedUser}
			<form
				method="POST"
				action="?/set_credits"
				use:enhance={() => {
					return async ({ update }) => {
						editDialogOpen = false;
						await update();
					};
				}}
				class="space-y-4"
			>
				<input type="hidden" name="user_id" value={selectedUser.id} />
				<div class="space-y-2">
					<label for="max_credits" class="text-sm font-medium">Max Credits</label>
					<Input id="max_credits" name="max_credits" type="number" bind:value={max_credits} />
				</div>
				<Sheet.Footer>
					<Button type="submit">Save Changes</Button>
				</Sheet.Footer>
			</form>
		{/if}
	</Sheet.Content>
</Sheet.Root>
