"use client";

import { useParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { ProjectStatusPanel } from "@/components/projects/ProjectStatusPanel";
import { getProject, type ProjectDetails } from "@/lib/api/client";

const TERMINAL_STATUSES = new Set(["DONE", "FAILED"]);

export default function ProjectPage() {
  const params = useParams<{ id: string }>();
  const projectId = params.id;
  const [project, setProject] = useState<ProjectDetails | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll(id: string): Promise<void> {
      try {
        const next = await getProject(id);
        if (cancelled) return;
        setProject(next);
        setError(null);
        if (!TERMINAL_STATUSES.has(next.status)) {
          pollTimer.current = setTimeout(() => {
            void poll(id);
          }, 600);
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to load project");
      }
    }

    void poll(projectId);

    return () => {
      cancelled = true;
      if (pollTimer.current) {
        clearTimeout(pollTimer.current);
      }
    };
  }, [projectId]);

  return (
    <main className="mx-auto w-full max-w-3xl px-8 py-10">
      {error ? <p className="text-sm text-coral">{error}</p> : null}
      {!project && !error ? (
        <p className="animate-pulse-status font-[family-name:var(--font-pixel)] text-[10px] text-gold">
          Loading…
        </p>
      ) : null}
      {project ? <ProjectStatusPanel project={project} /> : null}
    </main>
  );
}
