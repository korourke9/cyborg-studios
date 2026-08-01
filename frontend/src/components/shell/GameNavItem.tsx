"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import { deleteProject, gameLabel, type ProjectSummary } from "@/lib/api/client";
import { useErrorBanner } from "@/components/shell/ErrorBanner";

type Props = {
  game: ProjectSummary;
  active: boolean;
  onDeleted: (id: string) => void;
};

export function GameNavItem({ game, active, onDeleted }: Props) {
  const router = useRouter();
  const { reportError } = useErrorBanner();
  const menuId = useId();
  const [open, setOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const href = `/projects/${game.id}`;

  useEffect(() => {
    if (!open) return;

    function onPointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  async function handleDelete() {
    if (deleting) return;
    if (!window.confirm(`Delete “${gameLabel(game.prompt)}”?`)) {
      setOpen(false);
      return;
    }
    setDeleting(true);
    setOpen(false);
    try {
      await deleteProject(game.id);
      onDeleted(game.id);
      if (active) {
        router.push("/");
      }
    } catch (error) {
      setDeleting(false);
      reportError(
        error instanceof Error ? error.message : "Could not delete that game.",
      );
    }
  }

  return (
    <div
      ref={rootRef}
      className={`group relative flex items-center gap-0.5 rounded-sm ${
        active ? "bg-ink-raised" : "hover:bg-ink"
      }`}
    >
      <Link
        href={href}
        className={`min-w-0 flex-1 truncate px-2 py-1.5 text-sm leading-snug ${
          active ? "text-foam" : "text-muted group-hover:text-foam"
        }`}
        title={game.prompt}
      >
        {gameLabel(game.prompt)}
      </Link>

      <button
        type="button"
        aria-label={`Actions for ${gameLabel(game.prompt)}`}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={menuId}
        disabled={deleting}
        onClick={(event) => {
          event.preventDefault();
          event.stopPropagation();
          setOpen((value) => !value);
        }}
        className={`shrink-0 px-1.5 py-1 font-[family-name:var(--font-pixel)] text-[10px] leading-none text-muted opacity-0 transition group-hover:opacity-100 focus:opacity-100 ${
          open || active ? "opacity-100" : ""
        }`}
      >
        ⋮
      </button>

      {open ? (
        <div
          id={menuId}
          role="menu"
          className="absolute top-full right-0 z-20 mt-1 min-w-[7.5rem] border-2 border-line bg-ink-panel py-1 shadow-[3px_3px_0_0_#9b7ed9]"
        >
          <button
            type="button"
            role="menuitem"
            disabled={deleting}
            onClick={() => {
              void handleDelete();
            }}
            className="block w-full px-3 py-1.5 text-left text-sm text-coral hover:bg-ink-raised disabled:opacity-50"
          >
            Delete
          </button>
        </div>
      ) : null}
    </div>
  );
}
