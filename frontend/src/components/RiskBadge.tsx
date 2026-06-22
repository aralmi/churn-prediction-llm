import { formatRiskLevel } from "../utils";

interface RiskBadgeProps {
  level: string | null;
}

export function RiskBadge({ level }: RiskBadgeProps) {
  if (!level) {
    return <span className="risk-badge risk-badge-neutral">Неизвестно</span>;
  }

  const normalizedLevel = level.toLowerCase();
  const className = `risk-badge risk-badge-${normalizedLevel}`;

  return <span className={className}>{formatRiskLevel(normalizedLevel)}</span>;
}
