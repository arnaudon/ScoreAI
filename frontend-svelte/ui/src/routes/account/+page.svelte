<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	let loadingProfile = $state(false);
	let loadingPassword = $state(false);
	let loadingDelete = $state(false);
</script>

<div class="max-w-3xl py-4">
	<h1 class="text-fancy-title mb-8 text-3xl font-bold text-foreground">Account Management</h1>

	<div class="space-y-8">
		<section class="rounded-md border bg-card p-6 text-card-foreground shadow-card">
			<h2 class="text-fancy-title mb-4 text-xl font-semibold">Profile Information</h2>
			<p class="mb-6 text-sm text-muted-foreground">View and update your account's profile information.</p>

			<form
				method="POST"
				action="?/update_profile"
				class="space-y-4"
				use:enhance={() => {
					loadingProfile = true;
					return async ({ update }) => {
						loadingProfile = false;
						update({ reset: false });
					};
				}}
			>
				<div class="space-y-2">
					<label for="username" class="text-sm font-medium">Username</label>
					<Input id="username" value={data.user?.username} disabled class="max-w-md" />
				</div>
				<div class="space-y-2">
					<label for="email" class="text-sm font-medium">Email</label>
					<Input id="email" name="email" type="email" value={data.user?.email || ''} class="max-w-md" required />
				</div>
				<div class="space-y-2">
					<label for="instrument" class="text-sm font-medium">Preferred Instrument</label>
					<select
						id="instrument"
						name="instrument"
						class="flex h-10 w-full max-w-md items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
					>
						<option value="" disabled selected={!data.user?.instrument}>Select an instrument...</option>
						<option value="piano" selected={data.user?.instrument === 'piano'}>Piano</option>
						<option value="violin" selected={data.user?.instrument === 'violin'}>Violin</option>
						<option value="viola" selected={data.user?.instrument === 'viola'}>Viola</option>
						<option value="cello" selected={data.user?.instrument === 'cello'}>Cello</option>
						<option value="guitar" selected={data.user?.instrument === 'guitar'}>Guitar</option>
						<option value="flute" selected={data.user?.instrument === 'flute'}>Flute</option>
						<option value="clarinet" selected={data.user?.instrument === 'clarinet'}>Clarinet</option>
						<option value="trumpet" selected={data.user?.instrument === 'trumpet'}>Trumpet</option>
						<option value="other" selected={data.user?.instrument === 'other'}>Other</option>
					</select>
				</div>
				<div class="space-y-2">
					<label for="role" class="text-sm font-medium">Role</label>
					<Input
						id="role"
						value={data.user?.role || (data.user?.is_admin ? 'admin' : 'user')}
						disabled
						class="max-w-md capitalize"
					/>
				</div>
				<div class="space-y-2">
					<label for="credits" class="text-sm font-medium">Credits</label>
					<Input
						id="credits"
						value={`${data.user?.credits} / ${data.user?.max_credits}`}
						disabled
						class="max-w-md"
					/>
				</div>

				{#if form?.form === 'profile' && form?.error}
					<p class="text-sm font-medium text-destructive">{form.error}</p>
				{/if}
				{#if form?.form === 'profile' && form?.success}
					<p class="text-sm font-medium text-green-600 dark:text-green-400">
						Profile updated successfully!
					</p>
				{/if}

				<Button type="submit" disabled={loadingProfile}>
					{loadingProfile ? 'Saving...' : 'Save Profile'}
				</Button>
			</form>
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
