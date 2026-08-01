import Link from "next/link";
import { PhaserCabinet } from "@/components/play/PhaserCabinet";

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
      <PhaserCabinet projectId={id} />
    </main>
  );
}
