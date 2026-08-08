"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  getEngineeringLabOptions,
  updateEngineeringLabOptions,
  type EngineeringLabOptions,
  type PlayRuntime,
} from "@/lib/api/client";

const DEFAULT_OPTIONS: EngineeringLabOptions = {
  sdkEnabled: true,
  sdkLlmReview: true,
  sdkLlmAuthorship: true,
  allowUnreviewedSdkPlay: false,
  preferredPlayRuntime: "ir",
};

type Props = {
  /** Compact layout for Play header strip */
  compact?: boolean;
  onOptionsChange?: (options: EngineeringLabOptions) => void;
};

export function EngineeringLabPanel({ compact = false, onOptionsChange }: Props) {
  const [options, setOptions] = useState<EngineeringLabOptions>(DEFAULT_OPTIONS);
  const [synced, setSynced] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const onChangeRef = useRef(onOptionsChange);
  onChangeRef.current = onOptionsChange;

  const applyLocal = useCallback((next: EngineeringLabOptions, fromServer: boolean) => {
    setOptions(next);
    if (fromServer) {
      setSynced(true);
      setError(null);
    }
    onChangeRef.current?.(next);
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const next = await getEngineeringLabOptions();
        if (!cancelled) applyLocal(next, true);
      } catch (err) {
        if (!cancelled) {
          setSynced(false);
          setError(
            err instanceof Error
              ? `${err.message} — rebuild/restart the backend to enable live lab toggles.`
              : "Lab API unavailable — rebuild/restart the backend.",
          );
          onChangeRef.current?.(DEFAULT_OPTIONS);
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [applyLocal]);

  async function patch(partial: Partial<EngineeringLabOptions>) {
    const optimistic = { ...options, ...partial };
    setOptions(optimistic);
    onChangeRef.current?.(optimistic);
    setSaving(true);
    try {
      const next = await updateEngineeringLabOptions(partial);
      applyLocal(next, true);
    } catch (err) {
      setSynced(false);
      setError(
        err instanceof Error
          ? `${err.message} — changes are local-only until the lab API is up.`
          : "Failed to update lab options on the server.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <section
      className={`border-2 border-dashed border-[#c45c26]/60 bg-ink-raised/80 ${
        compact ? "p-3" : "p-4"
      }`}
    >
      <header className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="font-[family-name:var(--font-pixel)] text-[8px] text-[#c45c26]">
          LAB · DEV ONLY
        </h3>
        <p className="text-[11px] text-muted">
          {synced ? "Synced with backend" : "Remove before external release"}
        </p>
      </header>

      {error ? <p className="mb-2 text-xs text-[#c45c26]">{error}</p> : null}

      <div className={`flex flex-col ${compact ? "gap-2" : "gap-3"}`}>
        <label className="flex items-start gap-2 text-sm text-foam">
          <input
            type="checkbox"
            className="mt-1"
            checked={options.sdkEnabled}
            disabled={saving}
            onChange={(event) => patch({ sdkEnabled: event.target.checked })}
          />
          <span>
            <span className="font-medium">Emit SDK JS</span>
            <span className="block text-xs text-muted">
              Next Engineering run ships sdkSource (template or LLM-authored).
            </span>
          </span>
        </label>

        <label className="flex items-start gap-2 text-sm text-foam">
          <input
            type="checkbox"
            className="mt-1"
            checked={options.sdkLlmAuthorship}
            disabled={saving || !options.sdkEnabled}
            onChange={(event) =>
              patch({ sdkLlmAuthorship: event.target.checked })
            }
          />
          <span>
            <span className="font-medium">LLM SDK gameplay authorship</span>
            <span className="block text-xs text-muted">
              On = LLM writes Cyborg.boot JS with gameplay twists. Off = IR→SDK
              template only. Needs LLM configured.
            </span>
          </span>
        </label>

        <label className="flex items-start gap-2 text-sm text-foam">
          <input
            type="checkbox"
            className="mt-1"
            checked={options.sdkLlmReview}
            disabled={saving || !options.sdkEnabled}
            onChange={(event) => patch({ sdkLlmReview: event.target.checked })}
          />
          <span>
            <span className="font-medium">LLM security review</span>
            <span className="block text-xs text-muted">
              Off = static denylist only. Needs LLM configured on the backend.
            </span>
          </span>
        </label>

        <label className="flex items-start gap-2 text-sm text-foam">
          <input
            type="checkbox"
            className="mt-1"
            checked={options.allowUnreviewedSdkPlay}
            disabled={saving}
            onChange={(event) =>
              patch({ allowUnreviewedSdkPlay: event.target.checked })
            }
          />
          <span>
            <span className="font-medium">Allow unreviewed SDK in Play</span>
            <span className="block text-xs text-muted">
              Unsafe — lets Play load sdkSource even if review is deny/pending.
            </span>
          </span>
        </label>

        <div>
          <p className="mb-1 text-xs text-muted">Preferred Play runtime</p>
          <div className="flex flex-wrap gap-2">
            {(["ir", "sdk"] as PlayRuntime[]).map((runtime) => (
              <button
                key={runtime}
                type="button"
                disabled={saving}
                onClick={() => patch({ preferredPlayRuntime: runtime })}
                className={`border-2 px-2 py-1 font-[family-name:var(--font-pixel)] text-[8px] ${
                  options.preferredPlayRuntime === runtime
                    ? "border-cyan bg-ink text-cyan"
                    : "border-line text-muted"
                }`}
              >
                {runtime === "ir" ? "IR COMPILER" : "SDK JS"}
              </button>
            ))}
          </div>
        </div>

        <p className="text-[11px] leading-relaxed text-muted">
          Generation flags apply on the next Engineering step. Play preference
          applies immediately on the Play cabinet.
        </p>
      </div>
    </section>
  );
}
