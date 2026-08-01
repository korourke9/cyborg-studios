import type { ArtifactDetails } from "@/lib/api/client";
import type { ArtifactTeam, ParsedArtifact } from "@/lib/artifacts/display";
import { parseArtifact } from "@/lib/artifacts/display";

export type PipelineStage =
  | "Design"
  | "Story"
  | "Art"
  | "Engineering"
  | "QA"
  | "Producer";

export const PIPELINE_STAGES: PipelineStage[] = [
  "Design",
  "Story",
  "Art",
  "Engineering",
  "QA",
  "Producer",
];

const STAGE_TEAM: Record<PipelineStage, ArtifactTeam> = {
  Design: "design",
  Story: "story",
  Art: "art",
  Engineering: "engineering",
  QA: "qa",
  Producer: "producer",
};

export function stageForStatus(status: string): PipelineStage {
  if (status.includes("VISION") || status.includes("DESIGN")) return "Design";
  if (status.includes("STORY") || status.includes("NARRATIVE")) return "Story";
  if (status.includes("ART")) return "Art";
  if (status.includes("ENGINEER") || status.includes("CODE")) return "Engineering";
  if (status.includes("QA")) return "QA";
  if (status.includes("PRODUCER")) return "Producer";
  if (status === "DONE") return "Design";
  return "Design";
}

export function artifactsForStage(
  artifacts: ArtifactDetails[],
  stage: PipelineStage,
): ParsedArtifact[] {
  const team = STAGE_TEAM[stage];
  return artifacts
    .map(parseArtifact)
    .filter((item) => {
      if (item.team !== team) return false;
      if (item.artifact.type === "REFLECTION_NOTE") return false;
      if (item.artifact.type === "GAME_BUNDLE") return false;
      // Brief already shows these on the project card
      if (
        stage === "Design" &&
        (item.artifact.type === "VISION_DOC" ||
          item.artifact.type === "DESIGN_PILLARS")
      ) {
        return false;
      }
      return true;
    });
}

export function briefFromArtifacts(artifacts: ArtifactDetails[]): {
  summary: string | null;
  pillars: string[];
} {
  let summary: string | null = null;
  let pillars: string[] = [];

  for (const artifact of artifacts) {
    const parsed = parseArtifact(artifact);
    if (parsed.parseError || typeof parsed.data !== "object" || parsed.data === null) {
      continue;
    }
    const data = parsed.data as Record<string, unknown>;
    if (artifact.type === "VISION_DOC" && typeof data.summary === "string") {
      summary = data.summary;
    }
    if (artifact.type === "DESIGN_PILLARS" && Array.isArray(data.pillars)) {
      pillars = data.pillars.map((entry) => String(entry));
    }
  }

  return { summary, pillars };
}

export function hasGameBundle(artifacts: ArtifactDetails[]): boolean {
  return artifacts.some((artifact) => artifact.type === "GAME_BUNDLE");
}

export type GameBundleSummary = {
  title: string;
  summary: string;
  controls: string;
  implemented: string[];
};

export function gameBundleSummaryFromArtifacts(
  artifacts: ArtifactDetails[],
): GameBundleSummary | null {
  for (let i = artifacts.length - 1; i >= 0; i -= 1) {
    const artifact = artifacts[i];
    if (artifact.type !== "GAME_BUNDLE") continue;
    const parsed = parseArtifact(artifact);
    if (parsed.parseError || typeof parsed.data !== "object" || parsed.data === null) {
      return {
        title: "Playable build",
        summary: "Engineering shipped a GameBundle for this project.",
        controls: "",
        implemented: [],
      };
    }
    const data = parsed.data as Record<string, unknown>;
    const implemented = Array.isArray(data.implemented)
      ? data.implemented.map((entry) => String(entry))
      : [];
    return {
      title:
        typeof data.title === "string" && data.title.trim()
          ? data.title
          : "Playable build",
      summary:
        typeof data.summary === "string" && data.summary.trim()
          ? data.summary
          : "Engineering compiled a playable Phaser level for this project.",
      controls: typeof data.controls === "string" ? data.controls : "",
      implemented,
    };
  }
  return null;
}
