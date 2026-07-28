import { Card } from '@/components/ui/card'
import { cn } from '@/lib/utils'

export function RiskGauge({
  label,
  value,
  max,
  format,
  sublabel,
}: {
  label: string
  value: number | null
  max: number
  format: (v: number) => string
  sublabel?: string
}) {
  const pct = value == null ? 0 : Math.min(100, (Math.abs(value) / max) * 100)
  const tone = pct >= 90 ? 'negative' : pct >= 70 ? 'warning' : 'positive'

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-none">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        <span
          className={cn(
            'font-mono text-xs font-medium',
            tone === 'positive' && 'text-positive',
            tone === 'warning' && 'text-warning',
            tone === 'negative' && 'text-negative',
          )}
        >
          {pct.toFixed(0)}%
        </span>
      </div>

      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500',
            tone === 'positive' && 'bg-positive',
            tone === 'warning' && 'bg-warning',
            tone === 'negative' && 'bg-negative',
          )}
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="flex items-center justify-between font-mono text-xs text-muted-foreground">
        <span>{value != null ? format(value) : '—'}</span>
        <span>limit {format(max)}</span>
      </div>
      {sublabel && <span className="text-[11px] text-muted-foreground">{sublabel}</span>}
    </Card>
  )
}
