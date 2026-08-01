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
  ART_DIRECTION: {
    label: "Concept brief",
    team: "art",
    teamLabel: "Art",
  },
  ASSET_LIST: { label: "Asset list", team: "art", teamLabel: "Art" },
  ASSET_PROMPTS: {
    label: "Asset prompts",
    team: "art",
    teamLabel: "Art",
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

export type PaletteSwatch = {
  role: string;
  hex: string;
};

export type ArtifactField = {
  key: string;
  label: string;
  value: string | string[] | PaletteSwatch[];
  kind?: "text" | "colors";
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
    if (key.toLowerCase() === "palette" && Array.isArray(raw)) {
      const swatches = parsePaletteSwatches(raw);
      if (swatches.length > 0) {
        return {
          key,
          label: humanizeKey(key),
          value: swatches,
          kind: "colors" as const,
        };
      }
    }

    let value: string | string[];
    if (Array.isArray(raw)) {
      value = raw.map((entry) => formatFieldEntry(entry));
    } else if (raw !== null && typeof raw === "object") {
      value = formatFieldEntry(raw);
    } else {
      value = raw == null ? "" : String(raw);
    }
    return { key, label: humanizeKey(key), value, kind: "text" as const };
  });
}

const DEFAULT_PALETTE_ROLES = [
  "primary",
  "secondary",
  "accent",
  "background",
  "ink",
] as const;

function parsePaletteSwatches(raw: unknown[]): PaletteSwatch[] {
  const swatches: PaletteSwatch[] = [];

  for (let index = 0; index < raw.length; index += 1) {
    const entry = raw[index];
    if (typeof entry === "string" && isHexColor(entry)) {
      swatches.push({
        role: DEFAULT_PALETTE_ROLES[index] ?? `color-${index + 1}`,
        hex: entry.trim(),
      });
      continue;
    }
    if (entry !== null && typeof entry === "object") {
      const record = entry as Record<string, unknown>;
      const hexValue = record.hex ?? record.color ?? record.value;
      if (typeof hexValue === "string" && isHexColor(hexValue)) {
        const role =
          typeof record.role === "string" && record.role.trim()
            ? record.role.trim()
            : (DEFAULT_PALETTE_ROLES[index] ?? `color-${index + 1}`);
        swatches.push({ role, hex: hexValue.trim() });
      }
    }
  }

  return swatches;
}

function isHexColor(value: string): boolean {
  return /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/.test(value.trim());
}

function formatFieldEntry(entry: unknown): string {
  if (entry === null || entry === undefined) return "";
  if (typeof entry !== "object") return String(entry);
  if (Array.isArray(entry)) {
    return entry.map((item) => formatFieldEntry(item)).join(", ");
  }
  const record = entry as Record<string, unknown>;
  if (typeof record.role === "string" && typeof record.prompt === "string") {
    return `${record.role}: ${record.prompt}`;
  }
  if (typeof record.role === "string" && typeof record.fileRef === "string") {
    return `${record.role} → ${record.fileRef}`;
  }
  if (typeof record.role === "string" && typeof record.file_ref === "string") {
    return `${record.role} → ${record.file_ref}`;
  }
  return Object.entries(record)
    .map(([key, value]) => `${humanizeKey(key)}: ${String(value)}`)
    .join(" · ");
}
