"use client";

import { useEffect, useState } from "react";
import { gameBundleEntryUrl } from "@/lib/api/client";

const PHASER_CDN =
  "https://cdn.jsdelivr.net/npm/phaser@3.87.0/dist/phaser.min.js";

type Props = {
  projectId: string;
};

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(
      `script[data-cyborg-src="${src}"]`,
    );
    if (existing) {
      if (existing.dataset.loaded === "true") {
        resolve();
        return;
      }
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener(
        "error",
        () => reject(new Error(`Failed to load ${src}`)),
        { once: true },
      );
      return;
    }
    const script = document.createElement("script");
    script.src = src;
    script.async = true;
    script.dataset.cyborgSrc = src;
    script.onload = () => {
      script.dataset.loaded = "true";
      resolve();
    };
    script.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.body.appendChild(script);
  });
}

export function PhaserCabinet({ projectId }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function boot() {
      setError(null);
      setReady(false);
      try {
        await loadScript(PHASER_CDN);
        if (cancelled) return;
        // Bust cache so regenerations pick up a new entrySource.
        await loadScript(
          `${gameBundleEntryUrl(projectId)}?t=${Date.now()}`,
        );
        if (!cancelled) setReady(true);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Could not start the game.",
          );
        }
      }
    }

    void boot();

    return () => {
      cancelled = true;
      const game = (
        window as Window & { __cyborgGame?: { destroy: (remove: boolean) => void } }
      ).__cyborgGame;
      if (game) {
        game.destroy(true);
        (
          window as Window & { __cyborgGame?: unknown }
        ).__cyborgGame = undefined;
      }
    };
  }, [projectId]);

  return (
    <div className="flex w-full flex-1 flex-col items-center justify-center gap-4 px-4 py-8">
      <div
        id="game-root"
        className="aspect-[16/9] w-full max-w-4xl border-4 border-line bg-ink"
      />
      {!ready && !error ? (
        <p className="font-[family-name:var(--font-pixel)] text-[8px] text-muted">
          LOADING CABINET…
        </p>
      ) : null}
      {error ? (
        <p className="max-w-md text-center text-sm text-[#c45c26]">{error}</p>
      ) : null}
      {ready ? (
        <p className="font-[family-name:var(--font-pixel)] text-[8px] text-muted">
          ARROWS / WASD · JUMP SPACE
        </p>
      ) : null}
    </div>
  );
}
