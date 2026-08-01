import type { ArtifactDetails } from "@/lib/api/client";

export type ArtifactTeam = "design" | "story" | "art" | "engineering" | "qa" | "producer" | "other";

const TYPE_META: Record<
  string,
  { label: string; team: ArtifactTeam; teamLabel: string }
> = {
  VISION_DOC: { label: "Vision", team: "design", teamLabel: "Design" },
  DESIGN_PILLARS: {
    label: "Design pillars",
    team: "design",
    teamLabel: "Design",
  },
  MECHANICS_SPEC: {
    label: "Mechanics",
    team: "design",
    teamLabel: "Design",
  },
  SYSTEMS_SPEC: { label: "Systems", team: "design", teamLabel: "Design" },
  NARRATIVE_SPEC: { label: "Narrative", team: "story", teamLabel: "Story" },
  EXPERIENCE_MILESTONES: {
    label: "Experience milestones",
    team: "story",
    teamLabel: "Story",
  },
  PRODUCER_NOTES: {
    label: "Producer notes",
    team: "producer",
    teamLabel: "Producer",
  },
  REFLECTION_NOTE: {
    label: "Reflection note",
    team: "other",
    teamLabel: "Process",
  },
};

export type ParsedArtifact = {
  artifact: ArtifactDetails;
  label: string;
  team: ArtifactTeam;
  teamLabel: string;
  data: unknown;
  parseError: string | null;
};

export type ArtifactField = {
  key: string;
  label: string;
  value: string | string[];
};

const TEAM_ORDER: ArtifactTeam[] = [
  "design",
  "story",
  "art",
  "engineering",
  "qa",
  "producer",
  "other",
];

export function parseArtifact(artifact: ArtifactDetails): ParsedArtifact {
  const meta = TYPE_META[artifact.type] ?? {
    label: artifact.type,
    team: "other" as const,
    teamLabel: "Other",
  };

  try {
    return {
      artifact,
      label: meta.label,
      team: meta.team,
      teamLabel: meta.teamLabel,
      data: JSON.parse(artifact.payload) as unknown,
      parseError: null,
    };
  } catch {
    return {
      artifact,
      label: meta.label,
      team: meta.team,
      teamLabel: meta.teamLabel,
      data: artifact.payload,
      parseError: "Payload is not valid JSON",
    };
  }
}

export function groupArtifactsByTeam(
  artifacts: ArtifactDetails[],
): { team: ArtifactTeam; teamLabel: string; items: ParsedArtifact[] }[] {
  const parsed = artifacts.map(parseArtifact);
  const buckets = new Map<
    ArtifactTeam,
    { teamLabel: string; items: ParsedArtifact[] }
  >();

  for (const item of parsed) {
    const existing = buckets.get(item.team);
    if (existing) {
      existing.items.push(item);
    } else {
      buckets.set(item.team, { teamLabel: item.teamLabel, items: [item] });
    }
  }

  return TEAM_ORDER.filter((team) => buckets.has(team)).map((team) => {
    const bucket = buckets.get(team)!;
    return { team, teamLabel: bucket.teamLabel, items: bucket.items };
  });
}

function humanizeKey(key: string): string {
  return key
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/_/g, " ")
    .replace(/^\w/, (c) => c.toUpperCase());
}

export function fieldsFromData(data: unknown): ArtifactField[] {
  if (data === null || typeof data !== "object" || Array.isArray(data)) {
    return [
      {
        key: "value",
        label: "Value",
        value: typeof data === "string" ? data : JSON.stringify(data, null, 2),
      },
    ];
  }

  return Object.entries(data as Record<string, unknown>).map(([key, raw]) => {
    let value: string | string[];
    if (Array.isArray(raw)) {
      value = raw.map((entry) => String(entry));
    } else if (raw !== null && typeof raw === "object") {
      value = JSON.stringify(raw, null, 2);
    } else {
      value = raw == null ? "" : String(raw);
    }
    return { key, label: humanizeKey(key), value };
  });
}
