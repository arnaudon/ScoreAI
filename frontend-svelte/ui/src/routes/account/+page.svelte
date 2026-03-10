<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
</script>

<div class="max-w-3xl py-4">
	<h1 class="mb-8 text-3xl font-bold text-foreground">Account Management</h1>

	<div class="space-y-8">
		<section class="rounded-md border bg-card p-6 text-card-foreground shadow-sm">
			<h2 class="mb-4 text-xl font-semibold">Profile Information</h2>
			<p class="mb-6 text-sm text-muted-foreground">Update your account's profile information and email address.</p>
			
			<form class="space-y-4" onsubmit={(e) => e.preventDefault()}>
				<div class="space-y-2">
					<label for="username" class="text-sm font-medium">Username</label>
					<Input id="username" value="mock_user" disabled class="max-w-md" />
				</div>
				<div class="space-y-2">
					<label for="email" class="text-sm font-medium">Email</label>
					<Input id="email" type="email" value="user@example.com" disabled class="max-w-md" />
				</div>
				<Button disabled>Save Changes</Button>
			</form>
		</section>

		<section class="rounded-md border bg-card p-6 text-card-foreground shadow-sm">
			<h2 class="mb-4 text-xl font-semibold">Change Password</h2>
			<p class="mb-6 text-sm text-muted-foreground">Ensure your account is using a long, random password to stay secure.</p>
			
			<form class="space-y-4" onsubmit={(e) => e.preventDefault()}>
				<div class="space-y-2">
					<label for="current_password" class="text-sm font-medium">Current Password</label>
					<Input id="current_password" type="password" placeholder="••••••••" disabled class="max-w-md" />
				</div>
				<div class="space-y-2">
					<label for="new_password" class="text-sm font-medium">New Password</label>
					<Input id="new_password" type="password" placeholder="••••••••" disabled class="max-w-md" />
				</div>
				<div class="space-y-2">
					<label for="confirm_password" class="text-sm font-medium">Confirm Password</label>
					<Input id="confirm_password" type="password" placeholder="••••••••" disabled class="max-w-md" />
				</div>
				<Button disabled>Update Password</Button>
			</form>
		</section>
		
		<section class="rounded-md border border-destructive/20 bg-card p-6 text-card-foreground shadow-sm">
			<h2 class="mb-4 text-xl font-semibold text-destructive">Danger Zone</h2>
			<p class="mb-6 text-sm text-muted-foreground">Once you delete your account, there is no going back. Please be certain.</p>
			<Button variant="destructive" disabled>Delete Account</Button>
		</section>
	</div>
</div>
