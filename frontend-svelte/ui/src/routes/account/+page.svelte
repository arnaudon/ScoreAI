<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	let loadingPassword = $state(false);
	let loadingDelete = $state(false);
</script>

<div class="max-w-3xl py-4">
	<h1 class="text-fancy-title mb-8 text-3xl font-bold text-foreground">Account Management</h1>

	<div class="space-y-8">
		<section class="rounded-md border bg-card p-6 text-card-foreground shadow-card">
			<h2 class="text-fancy-title mb-4 text-xl font-semibold">Profile Information</h2>
			<p class="mb-6 text-sm text-muted-foreground">View your account's profile information.</p>
			
			<div class="space-y-4">
				<div class="space-y-2">
					<label for="username" class="text-sm font-medium">Username</label>
					<Input id="username" value={data.user?.username} disabled class="max-w-md" />
				</div>
				<div class="space-y-2">
					<label for="role" class="text-sm font-medium">Role</label>
					<Input id="role" value={data.user?.role || (data.user?.is_admin ? 'admin' : 'user')} disabled class="max-w-md capitalize" />
				</div>
				<div class="space-y-2">
					<label for="credits" class="text-sm font-medium">Credits</label>
					<Input id="credits" value={data.user?.credits} disabled class="max-w-md" />
				</div>
			</div>
		</section>

		<section class="rounded-md border bg-card p-6 text-card-foreground shadow-card">
			<h2 class="text-fancy-title mb-4 text-xl font-semibold">Change Password</h2>
			<p class="mb-6 text-sm text-muted-foreground">Ensure your account is using a long, random password to stay secure.</p>
			
			<form method="POST" action="?/update_password" class="space-y-4" use:enhance={() => {
				loadingPassword = true;
				return async ({ update }) => {
					loadingPassword = false;
					update({ reset: true });
				};
			}}>
				<div class="space-y-2">
					<label for="current_password" class="text-sm font-medium">Current Password</label>
					<Input id="current_password" name="current_password" type="password" required class="max-w-md" />
				</div>
				<div class="space-y-2">
					<label for="new_password" class="text-sm font-medium">New Password</label>
					<Input id="new_password" name="new_password" type="password" required class="max-w-md" />
				</div>
				<div class="space-y-2">
					<label for="confirm_password" class="text-sm font-medium">Confirm Password</label>
					<Input id="confirm_password" name="confirm_password" type="password" required class="max-w-md" />
				</div>

				{#if form?.form === 'password' && form?.error}
					<p class="text-sm font-medium text-destructive">{form.error}</p>
				{/if}
				{#if form?.form === 'password' && form?.success}
					<p class="text-sm font-medium text-green-600 dark:text-green-400">Password updated successfully!</p>
				{/if}

				<Button type="submit" disabled={loadingPassword}>
					{loadingPassword ? 'Updating...' : 'Update Password'}
				</Button>
			</form>
		</section>
		
		<section class="rounded-md border border-destructive/20 bg-card p-6 text-card-foreground shadow-card">
			<h2 class="text-fancy-title mb-4 text-xl font-semibold text-destructive">Danger Zone</h2>
			<p class="mb-6 text-sm text-muted-foreground">Once you delete your account, there is no going back. Please be certain.</p>
			
			<form method="POST" action="?/delete_account" use:enhance={() => {
				loadingDelete = true;
				return async ({ update }) => {
					loadingDelete = false;
					update();
				};
			}}>
				{#if form?.form === 'delete' && form?.error}
					<p class="mb-4 text-sm font-medium text-destructive">{form.error}</p>
				{/if}
				<Button type="submit" variant="destructive" disabled={loadingDelete} onclick={(e) => {
					if (!confirm('Are you absolutely sure you want to delete your account? This action cannot be undone.')) {
						e.preventDefault();
					}
				}}>
					{loadingDelete ? 'Deleting...' : 'Delete Account'}
				</Button>
			</form>
		</section>
	</div>
</div>
