interface StatCardProps {
  label: string;
  value: string;
  tone?: "default" | "accent";
}

export function StatCard({ label, value, tone = "default" }: StatCardProps) {
  return (
    <article className={`stat-card stat-card-${tone}`}>
      <p>{label}</p>
      <strong>{value}</strong>
    </article>
  );
}

