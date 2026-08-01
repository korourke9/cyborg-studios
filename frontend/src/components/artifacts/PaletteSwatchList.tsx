"use client";

import { useState } from "react";
import type { PaletteSwatch } from "@/lib/artifacts/display";

type Props = {
  swatches: PaletteSwatch[];
};

function hexToRgb(hex: string): string | null {
  const cleaned = hex.trim().replace(/^#/, "");
  let full = cleaned;
  if (cleaned.length === 3) {
    full = cleaned
      .split("")
      .map((char) => `${char}${char}`)
      .join("");
  }
  if (!/^[0-9a-fA-F]{6}$/.test(full)) {
    return null;
  }
  const value = Number.parseInt(full, 16);
  const r = (value >> 16) & 255;
  const g = (value >> 8) & 255;
  const b = value & 255;
  return `rgb(${r}, ${g}, ${b})`;
}

function humanizeRole(role: string): string {
  return role
    .replace(/[_-]+/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/^\w/, (char) => char.toUpperCase());
}

function CopyIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 16 16"
      fill="none"
      aria-hidden
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect
        x="5.5"
        y="5.5"
        width="8"
        height="8"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <path
        d="M10.5 5.5V4a1 1 0 0 0-1-1h-6a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h1.5"
        stroke="currentColor"
        strokeWidth="1.5"
      />
    </svg>
  );
}

export function PaletteSwatchList({ swatches }: Props) {
  const [copiedHex, setCopiedHex] = useState<string | null>(null);

  async function copyHex(hex: string): Promise<void> {
    try {
      await navigator.clipboard.writeText(hex);
      setCopiedHex(hex);
      window.setTimeout(() => {
        setCopiedHex((current) => (current === hex ? null : current));
      }, 1200);
    } catch {
      // Clipboard can fail without permission; keep UI quiet.
    }
  }

  return (
    <ul className="mt-2 flex w-full flex-col gap-2">
      {swatches.map((swatch) => {
        const rgb = hexToRgb(swatch.hex) ?? swatch.hex;
        const copied = copiedHex === swatch.hex;
        return (
          <li
            key={`${swatch.role}-${swatch.hex}`}
            className="flex w-full items-center gap-3 border border-line bg-ink px-3 py-2"
          >
            <span
              aria-hidden
              className="h-8 w-8 shrink-0 border border-line"
              style={{ backgroundColor: swatch.hex }}
            />
            <div className="min-w-0 flex-1">
              <p className="font-[family-name:var(--font-pixel)] text-[8px] text-cyan">
                {humanizeRole(swatch.role)}
              </p>
              <p className="mt-1 truncate font-mono text-xs text-foam">
                <span className="uppercase tracking-wide">{swatch.hex}</span>
                <span className="text-muted"> · {rgb}</span>
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                void copyHex(swatch.hex);
              }}
              className="inline-flex h-8 w-8 shrink-0 items-center justify-center border border-line text-muted hover:border-cyan hover:text-cyan"
              title={copied ? "Copied hex" : `Copy ${swatch.hex}`}
              aria-label={
                copied
                  ? `Copied hex for ${humanizeRole(swatch.role)}`
                  : `Copy hex for ${humanizeRole(swatch.role)}`
              }
            >
              {copied ? (
                <span className="font-[family-name:var(--font-pixel)] text-[8px] text-lime">
                  ✓
                </span>
              ) : (
                <CopyIcon className="h-4 w-4" />
              )}
            </button>
          </li>
        );
      })}
    </ul>
  );
}
