<script lang="ts">
	import type { PageProps } from './$types';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { enhance } from '$app/forms';

	let { form }: PageProps = $props();
	let isRegister = $state(false);
</script>

<div class="flex h-full items-center justify-center py-20">
	<div class="bg-card text-card-foreground w-full max-w-sm rounded-lg border p-8 shadow-card">
		<div class="mb-6 text-center">
			<h1 class="text-fancy-title text-3xl font-bold">ScoreAI</h1>
			<p class="mt-2 text-muted-foreground">
				Your intelligent music score library. Upload, manage, and discover scores with AI-powered
				assistance.
			</p>
		</div>

		<div class="separator-ornate"></div>
		<h2 class="text-fancy-title mb-6 text-center text-xl font-semibold">
			{isRegister ? 'Sign Up' : 'Login'}
		</h2>

		<form
			method="POST"
			action={isRegister ? '?/register' : '?/login'}
			class="space-y-4"
			use:enhance
		>
			<div class="space-y-2">
				<label for="username" class="text-sm leading-none font-medium">Username</label>
				<Input id="username" name="username" type="text" value={form?.username ?? ''} />
			</div>
			{#if isRegister}
				<div class="space-y-2">
					<label for="email" class="text-sm leading-none font-medium">Email</label>
					<Input id="email" name="email" type="email" value={form?.email ?? ''} required />
				</div>
			{/if}
			<div class="space-y-2">
				<label for="password" class="text-sm leading-none font-medium">Password</label>
				<Input id="password" name="password" type="password" />
			</div>

			{#if isRegister}
				<div class="space-y-2">
					<label for="instrument" class="text-sm leading-none font-medium"
						>Preferred Instrument</label
					>
					<select
						id="instrument"
						name="instrument"
						class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
					>
						<option value="" disabled selected={!form?.instrument}>Select an instrument...</option>
						<option value="piano" selected={form?.instrument === 'piano'}>Piano</option>
						<option value="violin" selected={form?.instrument === 'violin'}>Violin</option>
						<option value="viola" selected={form?.instrument === 'viola'}>Viola</option>
						<option value="cello" selected={form?.instrument === 'cello'}>Cello</option>
						<option value="guitar" selected={form?.instrument === 'guitar'}>Guitar</option>
						<option value="flute" selected={form?.instrument === 'flute'}>Flute</option>
						<option value="clarinet" selected={form?.instrument === 'clarinet'}>Clarinet</option>
						<option value="trumpet" selected={form?.instrument === 'trumpet'}>Trumpet</option>
						<option value="other" selected={form?.instrument === 'other'}>Other</option>
					</select>
				</div>
			{/if}

			{#if !isRegister}
				<div class="flex items-center space-x-2 pt-2">
					<Checkbox id="remember" name="remember" />
					<label
						for="remember"
						class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
					>
						Keep me logged in
					</label>
				</div>
			{/if}

			{#if form?.error}
				<p class="text-destructive text-sm font-medium">{form.error}</p>
			{/if}
			{#if form?.message}
				<p class="text-sm font-medium text-green-600 dark:text-green-400">{form.message}</p>
			{/if}

			<Button type="submit" class="w-full">{isRegister ? 'Sign Up' : 'Log in'}</Button>
		</form>

		<div class="mt-4 text-center text-sm">
			{#if isRegister}
				<p class="text-muted-foreground">
					Already have an account? <button
						type="button"
						class="text-primary hover:underline"
						onclick={() => (isRegister = false)}>Log in</button
					>
				</p>
			{:else}
				<p class="text-muted-foreground">
					Don't have an account? <button
						type="button"
						class="text-primary hover:underline"
						onclick={() => (isRegister = true)}>Sign up</button
					>
				</p>
			{/if}
		</div>
	</div>
</div>
