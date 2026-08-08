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
      // Asset list already shows generated thumbs; skip raw BINARY_ASSET cards
      if (item.artifact.type === "BINARY_ASSET") return false;
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

export type ArtAssetPreview = {
  id: string;
  role: string;
  fileRef: string;
};

export function artAssetPreviewsFromArtifacts(
  artifacts: ArtifactDetails[],
): ArtAssetPreview[] {
  const byId = new Map<string, ArtAssetPreview>();

  for (const artifact of artifacts) {
    const parsed = parseArtifact(artifact);
    if (parsed.parseError || typeof parsed.data !== "object" || parsed.data === null) {
      continue;
    }
    const data = parsed.data as Record<string, unknown>;

    if (artifact.type === "ASSET_LIST" && Array.isArray(data.assets)) {
      for (const entry of data.assets) {
        if (entry === null || typeof entry !== "object") continue;
        const record = entry as Record<string, unknown>;
        const fileRef = String(record.fileRef ?? record.file_ref ?? "");
        if (!fileRef || fileRef.startsWith("placeholder")) continue;
        const id = String(record.id ?? record.assetId ?? "asset");
        const role = String(record.role ?? "asset");
        byId.set(id, { id, role, fileRef });
      }
    }

    if (artifact.type === "BINARY_ASSET") {
      const fileRef = String(data.fileRef ?? data.file_ref ?? "");
      if (!fileRef || fileRef.startsWith("placeholder")) continue;
      const id = String(data.assetId ?? data.asset_id ?? data.id ?? "asset");
      const role = String(data.role ?? "asset");
      byId.set(id, { id, role, fileRef });
    }
  }

  const roleOrder = [
    "hero",
    "key-level-backdrop",
    "signature-hazard",
    "key-level-tiles",
    "collectible",
  ];
  return [...byId.values()].sort((a, b) => {
    const ai = roleOrder.indexOf(a.role);
    const bi = roleOrder.indexOf(b.role);
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
  });
}

export type GameBundleSummary = {
  title: string;
  summary: string;
  controls: string;
  implemented: string[];
  sdkReviewVerdict: string;
  sdkReviewNotes: string[];
  sdkAuthorship: string;
  sdkGameplayNotes: string[];
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
        sdkReviewVerdict: "pending",
        sdkReviewNotes: [],
        sdkAuthorship: "none",
        sdkGameplayNotes: [],
      };
    }
    const data = parsed.data as Record<string, unknown>;
    const implemented = Array.isArray(data.implemented)
      ? data.implemented.map((entry) => String(entry))
      : [];
    const notesRaw = data.sdkReviewNotes ?? data.sdk_review_notes;
    const sdkReviewNotes = Array.isArray(notesRaw)
      ? notesRaw.map((entry) => String(entry))
      : [];
    const gameplayRaw = data.sdkGameplayNotes ?? data.sdk_gameplay_notes;
    const sdkGameplayNotes = Array.isArray(gameplayRaw)
      ? gameplayRaw.map((entry) => String(entry))
      : [];
    const verdictRaw = data.sdkReviewVerdict ?? data.sdk_review_verdict;
    const authorshipRaw = data.sdkAuthorship ?? data.sdk_authorship;
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
      sdkReviewVerdict:
        typeof verdictRaw === "string" && verdictRaw.trim()
          ? verdictRaw
          : "pending",
      sdkReviewNotes,
      sdkAuthorship:
        typeof authorshipRaw === "string" && authorshipRaw.trim()
          ? authorshipRaw
          : "none",
      sdkGameplayNotes,
    };
  }
  return null;
}
