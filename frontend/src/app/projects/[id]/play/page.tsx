import Link from "next/link";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function PlayPage({ params }: Props) {
  const { id } = await params;

  return (
    <main className="flex min-h-screen flex-col bg-ink">
      <header className="flex items-center justify-between border-b-4 border-line px-4 py-3">
        <Link
          href={`/projects/${id}`}
          className="font-[family-name:var(--font-pixel)] text-[8px] text-cyan underline-offset-4 hover:underline"
        >
          ← BACK TO DESK
        </Link>
        <p className="font-[family-name:var(--font-pixel)] text-[8px] text-muted">
          PLAY CABINET
        </p>
      </header>
      <div className="flex flex-1 flex-col items-center justify-center gap-4 px-6 py-16 text-center">
        <p className="font-[family-name:var(--font-pixel)] text-[10px] leading-relaxed text-gold">
          Phaser runner coming soon
        </p>
        <p className="max-w-md text-sm text-muted">
          This route stays full-bleed for the game canvas. Engineering will drop
          a GameBundle here; until then the desk still shows Design artifacts.
        </p>
      </div>
    </main>
  );
}
