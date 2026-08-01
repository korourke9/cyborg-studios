"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { createProject } from "@/lib/api/client";
import { useErrorBanner } from "@/components/shell/ErrorBanner";

export default function HomePage() {
  const router = useRouter();
  const { reportError } = useErrorBanner();
  const [prompt, setPrompt] = useState(
    "A tiny robot adventure in a glowing cave",
  );
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  async function submitPrompt(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!prompt.trim()) return;

    setSubmitting(true);
    setSubmitError(null);

    try {
      const created = await createProject(prompt.trim());
      router.push(`/projects/${created.projectId}`);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to create project";
      setSubmitError(message);
      reportError(message);
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-col gap-8 px-8 py-16">
      <div className="space-y-3">
        <h1 className="font-[family-name:var(--font-pixel)] text-2xl leading-relaxed text-cyan sm:text-3xl">
          Cyborg Studios
        </h1>
        <p className="max-w-xl text-lg leading-relaxed text-foam">
          Bring your ideas to life — with the help of a full team
        </p>
      </div>

      <section className="border-4 border-line bg-ink-panel p-5 shadow-[6px_6px_0_0_#9b7ed9]">
        <h2 className="mb-4 font-[family-name:var(--font-pixel)] text-[10px] text-lime">
          Start building!
        </h2>
        <form className="flex flex-col gap-4" onSubmit={submitPrompt}>
          <label className="sr-only" htmlFor="game-prompt">
            Game prompt
          </label>
          <textarea
            id="game-prompt"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            rows={4}
            className="w-full border-2 border-line bg-ink px-3 py-3 text-base text-foam outline-none placeholder:text-muted/70 focus:border-cyan"
            placeholder="Describe the game concept"
          />
          <button
            type="submit"
            disabled={submitting}
            className="btn-arcade w-fit border-4 border-lime bg-lime px-5 py-3 font-[family-name:var(--font-pixel)] text-[10px] text-ink-panel shadow-[4px_4px_0_0_#9b7ed9] transition hover:translate-x-px hover:translate-y-px hover:shadow-[2px_2px_0_0_#9b7ed9] disabled:cursor-not-allowed disabled:border-line disabled:bg-ink-raised disabled:text-muted disabled:shadow-none"
          >
            {submitting ? "LOADING…" : "PRESS START"}
          </button>
        </form>
        {submitError ? (
          <p className="mt-3 text-sm text-coral">{submitError}</p>
        ) : null}
      </section>
    </main>
  );
}
