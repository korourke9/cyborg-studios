"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ErrorBannerProvider, useErrorBanner } from "@/components/shell/ErrorBanner";
import { GameNavItem } from "@/components/shell/GameNavItem";
import { listProjects, type ProjectSummary } from "@/lib/api/client";

type Props = {
  children: React.ReactNode;
};

function AppShellInner({ children }: Props) {
  const pathname = usePathname();
  const { reportError } = useErrorBanner();
  const [games, setGames] = useState<ProjectSummary[]>([]);

  const refresh = useCallback(async () => {
    try {
      setGames(await listProjects());
    } catch (error) {
      setGames([]);
      reportError(
        error instanceof Error ? error.message : "Could not load games.",
      );
    }
  }, [reportError]);

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
              const active =
                pathname === href || pathname.startsWith(`${href}/`);
              return (
                <GameNavItem
                  key={game.id}
                  game={game}
                  active={active}
                  onDeleted={(id) => {
                    setGames((current) =>
                      current.filter((entry) => entry.id !== id),
                    );
                  }}
                />
              );
            })
          )}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">{children}</div>
    </div>
  );
}

export function AppShell({ children }: Props) {
  return (
    <ErrorBannerProvider>
      <AppShellInner>{children}</AppShellInner>
    </ErrorBannerProvider>
  );
}
