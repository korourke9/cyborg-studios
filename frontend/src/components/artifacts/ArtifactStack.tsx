import type { ParsedArtifact } from "@/lib/artifacts/display";
import { ArtifactCard } from "@/components/artifacts/ArtifactCard";

type Props = {
  items: ParsedArtifact[];
  featured?: boolean;
  emptyLabel?: string;
};

export function ArtifactStack({
  items,
  featured = false,
  emptyLabel = "Nothing here yet.",
}: Props) {
  if (items.length === 0) {
    return <p className="text-sm text-muted">{emptyLabel}</p>;
  }

  return (
    <div className="grid gap-4">
      {items.map((item) => (
        <ArtifactCard key={item.artifact.id} item={item} featured={featured} />
      ))}
    </div>
  );
}
