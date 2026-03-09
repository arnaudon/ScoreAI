<script lang="ts">
	import AppSidebar from '$lib/components/Sidebar.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
</script>

<Sidebar.Provider>
	<!-- Sidebar -->
	<AppSidebar />

	<!-- Main Content -->
	<main class="w-full flex-1 overflow-y-auto bg-gray-50 p-8">
		<h1 class="mb-4 text-2xl font-bold">ScoreAI</h1>

		<a href="/login" class="text-blue-500 hover:underline">Login</a>
	</main>
</Sidebar.Provider>
