<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import * as m from '$lib/paraglide/messages.js';
</script>

<div class="flex h-full items-center justify-center p-8 text-center">
	<div class="max-w-md space-y-4">
		<h1 class="text-2xl font-bold text-foreground">{m.no_score_selected()}</h1>
		<p class="text-muted-foreground">{m.please_select_score()}</p>
		<Button href="/db-viewer">{m.go_to_db_viewer()}</Button>
	</div>
</div>
