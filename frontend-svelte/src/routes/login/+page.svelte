<script lang="ts">
	import type { PageProps } from './$types';
	let { form }: PageProps = $props();
</script>

<h1>Login</h1>

<form method="POST">
	<div>
		<label for="email">Email</label>
		<input id="email" name="email" type="email" value={form?.email ?? ''} />
	</div>
	<div>
		<label for="password">Password</label>
		<input id="password" name="password" type="password" />
	</div>

	{#if form?.error}
		<p class="error">{form.error}</p>
	{/if}

	<button type="submit">Log in</button>
</form>

<style>
	.error {
		color: red;
	}
	div {
		margin-bottom: 1em;
	}
</style>
