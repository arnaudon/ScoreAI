<script lang="ts">
	import AppSidebar from '$lib/components/Sidebar.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
</script>

<Sidebar.Provider>
	<!-- Sidebar -->
	<AppSidebar />

	<!-- Main Content -->
	<main class="flex-1 overflow-y-auto w-full p-8 bg-gray-50">
		<h1 class="text-2xl font-bold mb-4">ScoreAI</h1>

		<a href="/login" class="text-blue-500 hover:underline">Login</a>
	</main>
</Sidebar.Provider>
