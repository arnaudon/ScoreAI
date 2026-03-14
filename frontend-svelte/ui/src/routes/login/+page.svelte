<script lang="ts">
	import type { PageProps } from './$types';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { enhance } from '$app/forms';
	import * as m from '$lib/paraglide/messages.js';

	let { form }: PageProps = $props();
	let isRegister = $state(false);
</script>

<div class="flex h-full items-center justify-center py-20">
	<div class="bg-card text-card-foreground w-full max-w-sm rounded-lg border p-8 shadow-card">
		<div class="mb-6 text-center">
			<img src="/logo.png" alt="ScoreGuide Logo" class="mx-auto mb-4 h-16 w-auto" />
			<h1 class="text-fancy-title text-3xl font-bold">ScoreGuide</h1>
			<p class="mt-2 text-muted-foreground">
				{m.login_description()}
			</p>
		</div>

		<h2 class="text-fancy-title mb-6 text-center text-xl font-semibold">
			{isRegister ? m.sign_up() : m.login()}
		</h2>

		<form
			method="POST"
			action={isRegister ? '?/register' : '?/login'}
			class="space-y-4"
			use:enhance
		>
			<div class="space-y-2">
				<label for="username" class="text-sm leading-none font-medium">{m.username()}</label>
				<Input id="username" name="username" type="text" value={form?.username ?? ''} />
			</div>
			{#if isRegister}
				<div class="space-y-2">
					<label for="email" class="text-sm leading-none font-medium">{m.email()}</label>
					<Input id="email" name="email" type="email" value={form?.email ?? ''} required />
				</div>
			{/if}
			<div class="space-y-2">
				<label for="password" class="text-sm leading-none font-medium">{m.password()}</label>
				<Input id="password" name="password" type="password" />
			</div>

			{#if isRegister}
				<div class="space-y-2">
					<label for="instrument" class="text-sm leading-none font-medium"
						>{m.preferred_instrument()}</label
					>
					<select
						id="instrument"
						name="instrument"
						class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
					>
						<option value="" disabled selected={!form?.instrument}>{m.select_instrument()}</option>
						<option value="piano" selected={form?.instrument === 'piano'}>{m.inst_piano()}</option>
						<option value="violin" selected={form?.instrument === 'violin'}>{m.inst_violin()}</option>
						<option value="viola" selected={form?.instrument === 'viola'}>{m.inst_viola()}</option>
						<option value="cello" selected={form?.instrument === 'cello'}>{m.inst_cello()}</option>
						<option value="guitar" selected={form?.instrument === 'guitar'}>{m.inst_guitar()}</option>
						<option value="flute" selected={form?.instrument === 'flute'}>{m.inst_flute()}</option>
						<option value="clarinet" selected={form?.instrument === 'clarinet'}>{m.inst_clarinet()}</option>
						<option value="trumpet" selected={form?.instrument === 'trumpet'}>{m.inst_trumpet()}</option>
						<option value="other" selected={form?.instrument === 'other'}>{m.inst_other()}</option>
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
						{m.keep_logged_in()}
					</label>
				</div>
			{/if}

			{#if form?.error}
				<p class="text-destructive text-sm font-medium">{form.error}</p>
			{/if}
			{#if form?.message}
				<p class="text-sm font-medium text-green-600 dark:text-green-400">{form.message}</p>
			{/if}

			<Button type="submit" class="w-full">{isRegister ? m.sign_up() : m.login()}</Button>
		</form>

		<div class="mt-4 text-center text-sm">
			{#if isRegister}
				<p class="text-muted-foreground">
					{m.already_have_account()} <button
						type="button"
						class="text-primary hover:underline"
						onclick={() => (isRegister = false)}>{m.login()}</button
					>
				</p>
			{:else}
				<p class="text-muted-foreground">
					{m.dont_have_account()} <button
						type="button"
						class="text-primary hover:underline"
						onclick={() => (isRegister = true)}>{m.sign_up()}</button
					>
				</p>
			{/if}
		</div>
	</div>
</div>
