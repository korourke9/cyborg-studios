"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import {
  createProject,
  fetchText,
  getProject,
  type ProjectDetails,
} from "@/lib/api/client";

const TERMINAL_STATUSES = new Set(["DONE", "FAILED"]);

export default function HomePage() {
  const [apiMessage, setApiMessage] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [prompt, setPrompt] = useState(
    "A tiny robot adventure in a glowing cave",
  );
  const [submitting, setSubmitting] = useState(false);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [project, setProject] = useState<ProjectDetails | null>(null);
  const [projectError, setProjectError] = useState<string | null>(null);
  const pollTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const message = await fetchText("/");
        if (!cancelled) {
          setApiMessage(message);
        }
      } catch (error) {
        if (!cancelled) {
          setApiError(error instanceof Error ? error.message : "Unknown error");
        }
      }
    })();
    return () => {
      cancelled = true;
      if (pollTimer.current) {
        clearTimeout(pollTimer.current);
      }
    };
  }, []);

  async function pollProject(id: string): Promise<void> {
    try {
      const next = await getProject(id);
      setProject(next);
      if (!TERMINAL_STATUSES.has(next.status)) {
        pollTimer.current = setTimeout(() => {
          void pollProject(id);
        }, 600);
      }
    } catch (error) {
      setProjectError(
        error instanceof Error ? error.message : "Failed to fetch project status",
      );
    }
  }

  async function submitPrompt(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!prompt.trim()) return;

    setSubmitting(true);
    setProjectError(null);
    setProject(null);
    setProjectId(null);
    if (pollTimer.current) {
      clearTimeout(pollTimer.current);
    }

    try {
      const created = await createProject(prompt.trim());
      setProjectId(created.projectId);
      await pollProject(created.projectId);
    } catch (error) {
      setProjectError(
        error instanceof Error ? error.message : "Failed to create project",
      );
    } finally {
      setSubmitting(false);
    }
  }

  function formatTime(epochMillis: number): string {
    return new Date(epochMillis).toLocaleTimeString();
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-6 px-6 py-12">
      <h1 className="text-3xl font-semibold tracking-tight text-slate-900">
        Cyborg Studios
      </h1>
      <p className="text-base text-slate-600">
        Create a project prompt and watch orchestration progress in real time.
      </p>

      <section className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-800">
        <h2 className="mb-2 font-medium text-slate-900">API check</h2>
        {apiError ? (
          <p className="text-red-700">Could not reach backend: {apiError}</p>
        ) : apiMessage ? (
          <p className="font-mono text-emerald-800">{apiMessage}</p>
        ) : (
          <p className="text-slate-500">Contacting backend…</p>
        )}
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="mb-3 text-lg font-medium text-slate-900">
          Generate project
        </h2>
        <form className="flex flex-col gap-3" onSubmit={submitPrompt}>
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            rows={3}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
            placeholder="Describe the game concept"
          />
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={submitting}
              className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {submitting ? "Starting…" : "Generate"}
            </button>
            {projectId ? (
              <p className="text-xs text-slate-500">
                Project ID: <span className="font-mono">{projectId}</span>
              </p>
            ) : null}
          </div>
        </form>
        {projectError ? (
          <p className="mt-3 text-sm text-red-700">{projectError}</p>
        ) : null}
      </section>

      {project ? (
        <section className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="mb-3 text-lg font-medium text-slate-900">
            Project status
          </h2>
          <div className="grid gap-1 text-sm text-slate-700">
            <p>
              <span className="font-medium">Status:</span>{" "}
              <span className="font-mono">{project.status}</span>
            </p>
            <p>
              <span className="font-medium">Prompt:</span> {project.prompt}
            </p>
            <p>
              <span className="font-medium">Updated:</span>{" "}
              {formatTime(project.updatedAt)}
            </p>
          </div>

          <h3 className="mt-4 mb-2 text-sm font-semibold text-slate-900">
            Artifacts
          </h3>
          {project.artifacts.length === 0 ? (
            <p className="text-sm text-slate-500">No artifacts yet.</p>
          ) : (
            <ul className="space-y-2">
              {project.artifacts.map((artifact) => (
                <li
                  key={artifact.id}
                  className="rounded border border-slate-200 bg-slate-50 p-3"
                >
                  <p className="text-xs font-semibold tracking-wide text-slate-600">
                    {artifact.type}
                  </p>
                  <p className="mt-1 text-sm text-slate-800">{artifact.payload}</p>
                </li>
              ))}
            </ul>
          )}
        </section>
      ) : null}
    </main>
  );
}
