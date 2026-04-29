<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { createProject, fetchText, getProject, type ProjectDetails } from '$lib/api/client';

	const TERMINAL_STATUSES = new Set(['DONE', 'FAILED']);

	let apiMessage = $state<string | null>(null);
	let apiError = $state<string | null>(null);

	let prompt = $state('A tiny robot adventure in a glowing cave');
	let submitting = $state(false);
	let projectId = $state<string | null>(null);
	let project = $state<ProjectDetails | null>(null);
	let projectError = $state<string | null>(null);

	let pollTimer: ReturnType<typeof setTimeout> | null = null;

	onMount(async () => {
		try {
			apiMessage = await fetchText('/');
		} catch (e) {
			apiError = e instanceof Error ? e.message : 'Unknown error';
		}
	});

	onDestroy(() => {
		if (pollTimer) {
			clearTimeout(pollTimer);
		}
	});

	async function submitPrompt(event: SubmitEvent): Promise<void> {
		event.preventDefault();
		if (!prompt.trim()) return;

		submitting = true;
		projectError = null;
		project = null;
		projectId = null;

		try {
			const created = await createProject(prompt.trim());
			projectId = created.projectId;
			await pollProject(created.projectId);
		} catch (e) {
			projectError = e instanceof Error ? e.message : 'Failed to create project';
		} finally {
			submitting = false;
		}
	}

	async function pollProject(id: string): Promise<void> {
		try {
			const next = await getProject(id);
			project = next;
			if (!TERMINAL_STATUSES.has(next.status)) {
				pollTimer = setTimeout(() => {
					void pollProject(id);
				}, 600);
			}
		} catch (e) {
			projectError = e instanceof Error ? e.message : 'Failed to fetch project status';
		}
	}

	function formatTime(epochMillis: number): string {
		return new Date(epochMillis).toLocaleTimeString();
	}
</script>

<svelte:head>
	<title>Cyborg Studios — Game Builder</title>
</svelte:head>

<main class="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-6 px-6 py-12">
	<h1 class="text-3xl font-semibold tracking-tight text-slate-900">Cyborg Studios</h1>
	<p class="text-base text-slate-600">Create a project prompt and watch orchestration progress in real time.</p>

	<section class="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-800">
		<h2 class="mb-2 font-medium text-slate-900">API check</h2>
		{#if apiError}
			<p class="text-red-700">Could not reach backend: {apiError}</p>
		{:else if apiMessage}
			<p class="font-mono text-emerald-800">{apiMessage}</p>
		{:else}
			<p class="text-slate-500">Contacting backend…</p>
		{/if}
	</section>

	<section class="rounded-lg border border-slate-200 bg-white p-4">
		<h2 class="mb-3 text-lg font-medium text-slate-900">Generate project</h2>
		<form class="flex flex-col gap-3" onsubmit={submitPrompt}>
			<textarea
				bind:value={prompt}
				rows="3"
				class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
				placeholder="Describe the game concept"
			></textarea>
			<div class="flex items-center gap-3">
				<button
					type="submit"
					disabled={submitting}
					class="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
				>
					{submitting ? 'Starting…' : 'Generate'}
				</button>
				{#if projectId}
					<p class="text-xs text-slate-500">Project ID: <span class="font-mono">{projectId}</span></p>
				{/if}
			</div>
		</form>
		{#if projectError}
			<p class="mt-3 text-sm text-red-700">{projectError}</p>
		{/if}
	</section>

	{#if project}
		<section class="rounded-lg border border-slate-200 bg-white p-4">
			<h2 class="mb-3 text-lg font-medium text-slate-900">Project status</h2>
			<div class="grid gap-1 text-sm text-slate-700">
				<p><span class="font-medium">Status:</span> <span class="font-mono">{project.status}</span></p>
				<p><span class="font-medium">Prompt:</span> {project.prompt}</p>
				<p><span class="font-medium">Updated:</span> {formatTime(project.updatedAt)}</p>
			</div>

			<h3 class="mt-4 mb-2 text-sm font-semibold text-slate-900">Artifacts</h3>
			{#if project.artifacts.length === 0}
				<p class="text-sm text-slate-500">No artifacts yet.</p>
			{:else}
				<ul class="space-y-2">
					{#each project.artifacts as artifact}
						<li class="rounded border border-slate-200 bg-slate-50 p-3">
							<p class="text-xs font-semibold tracking-wide text-slate-600">{artifact.type}</p>
							<p class="mt-1 text-sm text-slate-800">{artifact.payload}</p>
						</li>
					{/each}
				</ul>
			{/if}
		</section>
	{/if}
</main>
