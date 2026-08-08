import Link from "next/link";
import type { GameBundleSummary } from "@/lib/artifacts/desk";

type Props = {
  projectId: string;
  bundle: GameBundleSummary;
};

export function EngineeringBuildCard({ projectId, bundle }: Props) {
  const sdkCleared = bundle.sdkReviewVerdict === "allow";
  const sdkBlocked =
    Boolean(bundle.sdkReviewVerdict) &&
    bundle.sdkReviewVerdict !== "allow" &&
    bundle.sdkReviewVerdict !== "skipped" &&
    bundle.sdkReviewVerdict !== "pending";

  return (
    <article className="border-4 border-line bg-ink-panel shadow-[4px_4px_0_0_#d4c4f0]">
      <header className="flex flex-wrap items-baseline justify-between gap-2 border-b-4 border-line px-4 py-3">
        <div>
          <h4 className="font-[family-name:var(--font-pixel)] text-[10px] leading-relaxed text-lime">
            Playable build
          </h4>
          <p className="mt-1 font-[family-name:var(--font-pixel)] text-[8px] text-muted">
            GAME_BUNDLE · IR + SDK EXPERIMENT
          </p>
        </div>
      </header>

      <div className="space-y-3 px-4 py-3">
        <div>
          <p className="font-[family-name:var(--font-pixel)] text-[8px] tracking-wide text-cyan">
            Title
          </p>
          <p className="mt-1 text-sm text-foam">{bundle.title}</p>
        </div>
        <div>
          <p className="font-[family-name:var(--font-pixel)] text-[8px] tracking-wide text-cyan">
            Status
          </p>
          <p className="mt-1 text-sm text-foam">
            Engineering shipped an IR-compiled level
            {sdkCleared
              ? " and an SDK JS runtime cleared by security review."
              : ". SDK JS waits on security review before Play can load it."}
          </p>
        </div>
        <div>
          <p className="font-[family-name:var(--font-pixel)] text-[8px] tracking-wide text-cyan">
            Summary
          </p>
          <p className="mt-1 text-sm leading-relaxed text-foam">{bundle.summary}</p>
        </div>
        {bundle.controls ? (
          <div>
            <p className="font-[family-name:var(--font-pixel)] text-[8px] tracking-wide text-cyan">
              Controls
            </p>
            <p className="mt-1 text-sm text-foam">{bundle.controls}</p>
          </div>
        ) : null}
        {bundle.implemented.length > 0 ? (
          <div>
            <p className="font-[family-name:var(--font-pixel)] text-[8px] tracking-wide text-cyan">
              Implemented
            </p>
            <ul className="mt-1 list-inside list-disc text-sm text-foam">
              {bundle.implemented.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        ) : null}
        <div>
          <p className="font-[family-name:var(--font-pixel)] text-[8px] tracking-wide text-cyan">
            SDK authorship
          </p>
          <p className="mt-1 text-sm text-foam">
            {bundle.sdkAuthorship || "none"}
            {bundle.sdkGameplayNotes[0] ? ` — ${bundle.sdkGameplayNotes[0]}` : ""}
          </p>
        </div>
        <div>
          <p className="font-[family-name:var(--font-pixel)] text-[8px] tracking-wide text-cyan">
            SDK review
          </p>
          <p className="mt-1 text-sm text-foam">
            {bundle.sdkReviewVerdict || "pending"}
            {bundle.sdkReviewNotes[0] ? ` — ${bundle.sdkReviewNotes[0]}` : ""}
          </p>
          {sdkBlocked ? (
            <p className="mt-1 text-xs text-[#c45c26]">
              SDK Play is blocked until review allows it. IR compiler remains playable.
            </p>
          ) : null}
        </div>
        <div className="pt-1">
          <Link
            href={`/projects/${projectId}/play`}
            className="btn-arcade inline-block border-4 border-lime bg-lime px-3 py-2 font-[family-name:var(--font-pixel)] text-[8px] text-ink-panel shadow-[3px_3px_0_0_#9b7ed9]"
          >
            OPEN PLAY
          </Link>
        </div>
      </div>
    </article>
  );
}
