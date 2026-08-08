"use client";

import type { ArtAssetPreview } from "@/lib/artifacts/desk";
import { API_BASE_URL } from "@/lib/api/client";

type Props = {
  assets: ArtAssetPreview[];
};

function resolveAssetSrc(fileRef: string): string {
  if (fileRef.startsWith("http://") || fileRef.startsWith("https://")) {
    return fileRef;
  }
  if (fileRef.startsWith("/")) {
    return `${API_BASE_URL}${fileRef}`;
  }
  return fileRef;
}

function roleLabel(role: string): string {
  return role
    .replace(/[_-]+/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/^\w/, (c) => c.toUpperCase());
}

export function ArtAssetsCard({ assets }: Props) {
  if (assets.length === 0) return null;

  return (
    <article className="border-4 border-line bg-ink-panel shadow-[4px_4px_0_0_#d4c4f0]">
      <header className="flex flex-wrap items-baseline justify-between gap-2 border-b-4 border-line px-4 py-3">
        <div>
          <h4 className="font-[family-name:var(--font-pixel)] text-[10px] leading-relaxed text-lime">
            Generated assets
          </h4>
          <p className="mt-1 font-[family-name:var(--font-pixel)] text-[8px] text-muted">
            Hero, backdrop, and hazard sprites for the playable build
          </p>
        </div>
      </header>

      <ul className="grid gap-3 px-4 py-3 sm:grid-cols-3">
        {assets.map((asset) => (
          <li
            key={asset.id}
            className="border border-line bg-ink px-2 py-2"
          >
            <p className="font-[family-name:var(--font-pixel)] text-[8px] text-cyan">
              {roleLabel(asset.role)}
            </p>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={resolveAssetSrc(asset.fileRef)}
              alt={roleLabel(asset.role)}
              className="mt-2 h-36 w-full bg-ink-raised object-contain"
            />
          </li>
        ))}
      </ul>
    </article>
  );
}
