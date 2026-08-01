"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArtifactStack } from "@/components/artifacts/ArtifactStack";
import { EngineeringBuildCard } from "@/components/projects/EngineeringBuildCard";
import { gameLabel, type ProjectDetails } from "@/lib/api/client";
import {
  PIPELINE_STAGES,
  artifactsForStage,
  briefFromArtifacts,
  gameBundleSummaryFromArtifacts,
  hasGameBundle,
  stageForStatus,
  type PipelineStage,
} from "@/lib/artifacts/desk";

const TERMINAL_STATUSES = new Set(["DONE", "FAILED"]);

type Props = {
  project: ProjectDetails;
};

export function ProjectStatusPanel({ project }: Props) {
  const running = !TERMINAL_STATUSES.has(project.status);
  const playReady = hasGameBundle(project.artifacts);
  const { summary, pillars } = briefFromArtifacts(project.artifacts);
  const [selectedStage, setSelectedStage] = useState<PipelineStage>(() =>
    stageForStatus(project.status),
  );

  useEffect(() => {
    setSelectedStage(stageForStatus(project.status));
  }, [project.id, project.status]);

  const activeStage = stageForStatus(project.status);
  const stageArtifacts = artifactsForStage(project.artifacts, selectedStage);
  const engineeringBundle =
    selectedStage === "Engineering"
      ? gameBundleSummaryFromArtifacts(project.artifacts)
      : null;

  return (
    <section className="border-4 border-line bg-ink-panel p-5 shadow-[6px_6px_0_0_#9b7ed9]">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h1 className="font-[family-name:var(--font-pixel)] text-[12px] leading-relaxed text-cyan sm:text-sm">
            {gameLabel(project.prompt, 48)}
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-foam">{project.prompt}</p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`font-[family-name:var(--font-pixel)] text-[8px] ${
              project.status === "FAILED"
                ? "text-coral"
                : project.status === "DONE"
                  ? "text-lime"
                  : "animate-pulse-status text-gold"
            }`}
          >
            {project.status}
          </span>
          {playReady ? (
            <Link
              href={`/projects/${project.id}/play`}
              className="btn-arcade border-4 border-lime bg-lime px-3 py-2 font-[family-name:var(--font-pixel)] text-[8px] text-ink-panel shadow-[3px_3px_0_0_#9b7ed9]"
            >
              PLAY
            </Link>
          ) : (
            <button
              type="button"
              disabled
              className="border-4 border-line bg-ink-raised px-3 py-2 font-[family-name:var(--font-pixel)] text-[8px] text-muted"
            >
              PLAY
            </button>
          )}
        </div>
      </div>

      {(summary || pillars.length > 0) && (
        <div className="mt-4 border-t-2 border-line pt-4">
          {summary ? (
            <p className="text-sm leading-relaxed text-foam">{summary}</p>
          ) : null}
          {pillars.length > 0 ? (
            <ul className="mt-3 flex flex-wrap gap-2">
              {pillars.map((pillar) => (
                <li
                  key={pillar}
                  className="border border-line bg-ink-raised px-2 py-1 text-xs text-foam"
                >
                  {pillar}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      )}

      <div className="mt-5 flex flex-wrap gap-2">
        {PIPELINE_STAGES.map((stage, index) => {
          const activeIndex = PIPELINE_STAGES.indexOf(activeStage);
          const allDone = project.status === "DONE";
          const inProgress = running && index === activeIndex;
          const done = allDone || index < activeIndex;
          const selected = selectedStage === stage;
          return (
            <button
              key={stage}
              type="button"
              onClick={() => setSelectedStage(stage)}
              className={`border-2 px-2 py-1 font-[family-name:var(--font-pixel)] text-[8px] ${
                selected
                  ? "border-cyan bg-ink-raised text-cyan"
                  : inProgress
                    ? "border-gold text-gold"
                    : done
                      ? "border-lime/40 text-lime"
                      : "border-line text-muted"
              }`}
            >
              {stage}
            </button>
          );
        })}
      </div>

      <div className="mt-5 border-t-2 border-line pt-4">
        <h2 className="mb-3 font-[family-name:var(--font-pixel)] text-[8px] text-muted">
          {selectedStage}
        </h2>
        {engineeringBundle ? (
          <EngineeringBuildCard
            projectId={project.id}
            bundle={engineeringBundle}
          />
        ) : (
          <ArtifactStack
            items={stageArtifacts}
            emptyLabel={
              selectedStage === "Engineering"
                ? "No playable build yet."
                : "No deliverables yet."
            }
          />
        )}
      </div>
    </section>
  );
}
