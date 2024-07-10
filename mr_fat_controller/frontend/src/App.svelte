<script lang="ts">
  import { QueryClient, QueryClientProvider } from "@tanstack/svelte-query";
  import EntitiesList from "./lib/EntitiesList.svelte";

  const client = new QueryClient();
</script>

<QueryClientProvider {client}>
  <main class="max-w-xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Model Railway Fat Controller</h1>
    <EntitiesList />
  </main>
</QueryClientProvider>
