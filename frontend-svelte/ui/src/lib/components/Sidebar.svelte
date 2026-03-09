<script lang="ts">
	import { Button } from '$lib/components/ui/button';
</script>

<aside class="w-64 bg-white border-r shadow-sm flex flex-col">
	<div class="p-4 border-b">
		<h2 class="text-xl font-bold text-gray-800">App Menu</h2>
	</div>
	<nav class="p-4 flex flex-col gap-2 flex-1">
		<Button variant="ghost" class="justify-start" href="/">Home</Button>
		<Button variant="ghost" class="justify-start" href="/login">Login</Button>
		<Button variant="ghost" class="justify-start" href="/db-viewer">Database Viewer</Button>
	</nav>
</aside>
