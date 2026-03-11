<script lang="ts">
	import type { PageProps } from './$types';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { enhance } from '$app/forms';

	let { form }: PageProps = $props();
	let isRegister = $state(false);
</script>

<div class="flex h-full items-center justify-center py-20">
	<div class="w-full max-w-sm rounded-lg border bg-card p-8 text-card-foreground shadow-sm">
		<h1 class="mb-6 text-center text-2xl font-bold">{isRegister ? 'Sign Up' : 'Login'}</h1>

		<form method="POST" action={isRegister ? '?/register' : '?/login'} class="space-y-4" use:enhance>
			<div class="space-y-2">
				<label for="username" class="text-sm font-medium leading-none">Username</label>
				<Input id="username" name="username" type="text" value={form?.username ?? ''} />
			</div>
			<div class="space-y-2">
				<label for="password" class="text-sm font-medium leading-none">Password</label>
				<Input id="password" name="password" type="password" />
			</div>

			{#if form?.error}
				<p class="text-sm font-medium text-destructive">{form.error}</p>
			{/if}
			{#if form?.message}
				<p class="text-sm font-medium text-green-600 dark:text-green-400">{form.message}</p>
			{/if}

			<Button type="submit" class="w-full">{isRegister ? 'Sign Up' : 'Log in'}</Button>
		</form>

		<div class="mt-4 text-center text-sm">
			{#if isRegister}
				<p class="text-muted-foreground">Already have an account? <button type="button" class="text-primary hover:underline" onclick={() => isRegister = false}>Log in</button></p>
			{:else}
				<p class="text-muted-foreground">Don't have an account? <button type="button" class="text-primary hover:underline" onclick={() => isRegister = true}>Sign up</button></p>
			{/if}
		</div>
	</div>
</div>
