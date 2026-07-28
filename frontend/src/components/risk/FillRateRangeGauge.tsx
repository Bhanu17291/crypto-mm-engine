import { Card } from '@/components/ui/card'
import type { RiskLimitsStatus, RiskStatus } from '@/types/status'

const pct = (v: number) => `${(v * 100).toFixed(1)}%`

export function FillRateRangeGauge({
  risk,
  limits,
}: {
  risk: RiskStatus | null
  limits: RiskLimitsStatus | null
}) {
  const fillRate = risk?.fill_rate ?? null
  const min = (limits?.min_fill_rate ?? 0) * 100
  const max = (limits?.max_fill_rate ?? 1) * 100
  const marker = fillRate != null ? fillRate * 100 : null

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-none">
      <span className="text-xs font-medium text-muted-foreground">
        Fill Rate ({limits?.fill_rate_window ?? '—'}-cycle window)
      </span>

      <div className="relative h-2 w-full overflow-hidden rounded-full bg-negative-muted">
        <div
          className="absolute inset-y-0 bg-positive-muted"
          style={{ left: `${min}%`, width: `${Math.max(0, max - min)}%` }}
        />
        {marker != null && (
          <div
            className="absolute top-1/2 size-2.5 -translate-y-1/2 -translate-x-1/2 rounded-full border-2 border-background bg-brand shadow"
            style={{ left: `${Math.min(100, Math.max(0, marker))}%` }}
          />
        )}
      </div>

      <div className="flex items-center justify-between font-mono text-xs text-muted-foreground">
        <span>{fillRate != null ? pct(fillRate) : 'collecting…'}</span>
        <span>
          band {pct(limits?.min_fill_rate ?? 0)} – {pct(limits?.max_fill_rate ?? 1)}
        </span>
      </div>
    </Card>
  )
}
