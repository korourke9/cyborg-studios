"use client";

import type {
  AssetRef,
  PaletteSwatch,
  ParsedArtifact,
} from "@/lib/artifacts/display";
import { fieldsFromData } from "@/lib/artifacts/display";
import { PaletteSwatchList } from "@/components/artifacts/PaletteSwatchList";
import { API_BASE_URL } from "@/lib/api/client";

type Props = {
  item: ParsedArtifact;
  featured?: boolean;
};

function isPaletteSwatches(
  value: string | string[] | PaletteSwatch[] | AssetRef[],
): value is PaletteSwatch[] {
  return (
    Array.isArray(value) &&
    value.length > 0 &&
    typeof value[0] === "object" &&
    value[0] !== null &&
    "hex" in value[0]
  );
}

function isAssetRefs(
  value: string | string[] | PaletteSwatch[] | AssetRef[],
): value is AssetRef[] {
  return (
    Array.isArray(value) &&
    value.length > 0 &&
    typeof value[0] === "object" &&
    value[0] !== null &&
    "fileRef" in value[0]
  );
}

function resolveAssetSrc(fileRef: string): string | null {
  if (fileRef.startsWith("placeholder")) return null;
  if (fileRef.startsWith("http://") || fileRef.startsWith("https://")) {
    return fileRef;
  }
  if (fileRef.startsWith("/")) {
    return `${API_BASE_URL}${fileRef}`;
  }
  return null;
}

export function ArtifactCard({ item, featured = false }: Props) {
  const fields = item.parseError ? [] : fieldsFromData(item.data);

  return (
    <article
      className={`border-4 bg-ink-panel ${
        featured
          ? "border-cyan shadow-[5px_5px_0_0_#ff8c42]"
          : "border-line shadow-[4px_4px_0_0_#d4c4f0]"
      }`}
    >
      <header className="flex flex-wrap items-baseline justify-between gap-2 border-b-4 border-line px-4 py-3">
        <div>
          <h4 className="font-[family-name:var(--font-pixel)] text-[10px] leading-relaxed text-lime">
            {item.label}
          </h4>
          <p className="mt-1 font-[family-name:var(--font-pixel)] text-[8px] text-muted">
            {item.artifact.type}
          </p>
        </div>
        <p className="font-[family-name:var(--font-pixel)] text-[8px] text-muted">
          #{item.artifact.id.slice(0, 8)}
        </p>
      </header>

      <div className="space-y-3 px-4 py-3">
        {item.parseError ? (
          <p className="text-sm text-coral">{item.parseError}</p>
        ) : (
          fields.map((field) => (
            <div key={field.key}>
              <p className="font-[family-name:var(--font-pixel)] text-[8px] tracking-wide text-cyan">
                {field.label}
              </p>
              {field.kind === "colors" && isPaletteSwatches(field.value) ? (
                <PaletteSwatchList swatches={field.value} />
              ) : field.kind === "assets" && isAssetRefs(field.value) ? (
                <ul className="mt-2 grid gap-3 sm:grid-cols-2">
                  {field.value.map((asset) => {
                    const src = resolveAssetSrc(asset.fileRef);
                    return (
                      <li
                        key={`${asset.id}-${asset.role}`}
                        className="border border-line bg-ink px-2 py-2"
                      >
                        <p className="font-[family-name:var(--font-pixel)] text-[8px] text-muted">
                          {asset.role}
                        </p>
                        {src ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={src}
                            alt={asset.role}
                            className="mt-2 h-28 w-full object-contain"
                          />
                        ) : (
                          <p className="mt-2 text-xs text-muted">
                            {asset.fileRef || "placeholder"}
                          </p>
                        )}
                      </li>
                    );
                  })}
                </ul>
              ) : Array.isArray(field.value) ? (
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-foam">
                  {field.value.map((entry) => (
                    <li key={String(entry)}>{String(entry)}</li>
                  ))}
                </ul>
              ) : (
                <p className="mt-1 whitespace-pre-wrap text-sm leading-relaxed text-foam">
                  {field.value}
                </p>
              )}
            </div>
          ))
        )}
      </div>

      <details className="border-t-4 border-line px-4 py-2">
        <summary className="cursor-pointer font-[family-name:var(--font-pixel)] text-[8px] text-muted hover:text-gold">
          Raw JSON
        </summary>
        <pre className="mt-2 overflow-x-auto pb-2 font-mono text-[11px] leading-relaxed text-muted">
          {item.parseError
            ? item.artifact.payload
            : JSON.stringify(item.data, null, 2)}
        </pre>
      </details>
    </article>
  );
}
