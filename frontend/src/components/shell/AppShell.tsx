"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  gameLabel,
  listProjects,
  type ProjectSummary,
} from "@/lib/api/client";

type Props = {
  children: React.ReactNode;
};

export function AppShell({ children }: Props) {
  const pathname = usePathname();
  const [games, setGames] = useState<ProjectSummary[]>([]);

  const refresh = useCallback(async () => {
    try {
      setGames(await listProjects());
    } catch {
      setGames([]);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh, pathname]);

  const isNewGame = pathname === "/";

  return (
    <div className="flex min-h-screen">
      <aside className="flex w-60 shrink-0 flex-col border-r border-line bg-ink-panel/80 px-3 py-4">
        <Link
          href="/"
          className="mb-6 px-2 font-[family-name:var(--font-pixel)] text-[10px] leading-relaxed text-cyan"
        >
          Cyborg Studios
        </Link>

        <Link
          href="/"
          className={`mb-4 block border-2 px-3 py-2 font-[family-name:var(--font-pixel)] text-[8px] leading-relaxed ${
            isNewGame
              ? "border-lime bg-lime text-ink-panel"
              : "border-line bg-ink text-foam hover:border-cyan"
          }`}
        >
          + New game
        </Link>

        <p className="mb-2 px-2 font-[family-name:var(--font-pixel)] text-[8px] text-muted">
          Games
        </p>
        <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto">
          {games.length === 0 ? (
            <p className="px-2 text-xs text-muted">No games yet</p>
          ) : (
            games.map((game) => {
              const href = `/projects/${game.id}`;
              const active = pathname === href || pathname.startsWith(`${href}/`);
              return (
                <Link
                  key={game.id}
                  href={href}
                  className={`rounded-sm px-2 py-1.5 text-sm leading-snug ${
                    active
                      ? "bg-ink-raised text-foam"
                      : "text-muted hover:bg-ink hover:text-foam"
                  }`}
                  title={game.prompt}
                >
                  {gameLabel(game.prompt)}
                </Link>
              );
            })
          )}
        </nav>
      </aside>

      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}
