"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  gameBundleEntryUrl,
  getPlayBundleInfo,
  type EngineeringLabOptions,
  type PlayBundleInfo,
  type PlayRuntime,
} from "@/lib/api/client";
import { EngineeringLabPanel } from "@/components/lab/EngineeringLabPanel";

type Props = {
  projectId: string;
  initialRuntime?: PlayRuntime;
};

export function PhaserCabinet({ projectId, initialRuntime = "ir" }: Props) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [info, setInfo] = useState<PlayBundleInfo | null>(null);
  const [lab, setLab] = useState<EngineeringLabOptions | null>(null);
  const [runtime, setRuntime] = useState<PlayRuntime>(initialRuntime);
  const [error, setError] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const [frameReady, setFrameReady] = useState(false);
  const [showLab, setShowLab] = useState(true);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const playInfo = await getPlayBundleInfo(projectId);
        if (cancelled) return;
        setInfo(playInfo);
        if (playInfo.runtimes.length === 0) {
          setError("No playable runtime is available yet.");
        } else {
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Could not load play info.",
          );
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [projectId, reloadKey]);

  useEffect(() => {
    if (!info) return;
    const preferred =
      lab?.preferredPlayRuntime ?? initialRuntime;
    const next = info.runtimes.includes(preferred)
      ? preferred
      : info.runtimes[0];
    if (next) setRuntime(next);
  }, [info, lab?.preferredPlayRuntime, initialRuntime]);

  useEffect(() => {
    if (lab === null) return;
    setReloadKey((key) => key + 1);
  }, [lab?.allowUnreviewedSdkPlay]);

  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const data = event.data || {};
      if (data.type === "cyborg-playframe-ready") {
        setFrameReady(true);
      }
      if (data.type === "cyborg-play-ready") {
        setReady(true);
        setError(null);
      }
      if (data.type === "cyborg-play-error") {
        setError(String(data.message || "Playframe error"));
        setReady(false);
      }
    }
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);

  const selectableRuntimes = useMemo(() => {
    const set = new Set<PlayRuntime>(info?.runtimes ?? []);
    // Lab: always offer both so testers can attempt SDK and see gate errors.
    set.add("ir");
    set.add("sdk");
    return Array.from(set);
  }, [info]);

  const scriptUrl = useMemo(() => {
    if (!info) return null;
    if (!info.runtimes.includes(runtime)) {
      // Still attempt boot URL so gate failures surface in the cabinet.
      return `${gameBundleEntryUrl(projectId, runtime)}&t=${Date.now()}`;
    }
    return `${gameBundleEntryUrl(projectId, runtime)}&t=${Date.now()}`;
  }, [info, projectId, runtime]);

  useEffect(() => {
    if (!frameReady || !scriptUrl || !iframeRef.current?.contentWindow) return;
    setReady(false);
    iframeRef.current.contentWindow.postMessage(
      { type: "cyborg-boot", scriptUrl, runtime },
      "*",
    );
  }, [frameReady, scriptUrl, runtime]);

  return (
    <div className="flex w-full flex-1 flex-col items-center justify-center gap-4 px-4 py-8">
      <div className="flex w-full max-w-4xl flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap gap-2">
            {selectableRuntimes.map((option) => {
              const available = info?.runtimes.includes(option) ?? false;
              return (
                <button
                  key={option}
                  type="button"
                  onClick={() => setRuntime(option)}
                  className={`border-2 px-2 py-1 font-[family-name:var(--font-pixel)] text-[8px] ${
                    runtime === option
                      ? "border-cyan bg-ink-raised text-cyan"
                      : available
                        ? "border-line text-muted"
                        : "border-line/50 text-muted/50"
                  }`}
                  title={
                    available
                      ? undefined
                      : "Not cleared for Play — boot may fail (lab probe)"
                  }
                >
                  {option === "ir" ? "IR COMPILER" : "SDK JS"}
                  {!available ? " ?" : ""}
                </button>
              );
            })}
          </div>
          <button
            type="button"
            onClick={() => setShowLab((value) => !value)}
            className="font-[family-name:var(--font-pixel)] text-[8px] text-[#c45c26] underline-offset-2 hover:underline"
          >
            {showLab ? "HIDE LAB" : "SHOW LAB"}
          </button>
        </div>

        {showLab ? (
          <EngineeringLabPanel compact onOptionsChange={setLab} />
        ) : null}
      </div>

      {info && !info.runtimes.includes("sdk") && info.sdkReviewVerdict !== "skipped" ? (
        <p className="max-w-xl text-center text-xs text-muted">
          SDK runtime pending/denied ({info.sdkReviewVerdict}
          {info.sdkReviewNotes[0] ? `: ${info.sdkReviewNotes[0]}` : ""}). Toggle
          “Allow unreviewed SDK” in Lab to force Play, or keep IR.
        </p>
      ) : null}

      <iframe
        ref={iframeRef}
        title="Cyborg playframe"
        src="/playframe.html"
        sandbox="allow-scripts"
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
          {runtime.toUpperCase()} · ARROWS / WASD · JUMP SPACE · AVOID HAZARDS
        </p>
      ) : null}
    </div>
  );
}
