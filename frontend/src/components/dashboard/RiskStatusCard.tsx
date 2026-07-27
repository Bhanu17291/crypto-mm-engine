import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import type { StatusSnapshot } from '@/types/status'

export function RiskStatusCard({ status }: { status: StatusSnapshot | null }) {
  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-none">
      <span className="text-xs font-medium text-muted-foreground">Risk Status</span>

      {!status ? (
        <div className="space-y-2">
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-full" />
        </div>
      ) : (
        <div className="space-y-2.5">
          <RiskRow label="Kill Switch" tripped={status.risk.kill_switch_tripped} />
          <RiskRow label="Circuit Breaker" tripped={status.risk.circuit_breaker_tripped} />
          <RiskRow label="Quoting" tripped={status.risk.halted} invertLabel />
        </div>
      )}
    </Card>
  )
}

function RiskRow({
  label,
  tripped,
  invertLabel = false,
}: {
  label: string
  tripped: boolean
  invertLabel?: boolean
}) {
  const ok = !tripped

  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-muted-foreground">{label}</span>
      <div className="flex items-center gap-1.5">
        <span
          className={cn(
            'size-1.5 rounded-full',
            ok ? 'bg-positive' : 'bg-negative animate-pulse',
          )}
        />
        <span className={cn('text-xs font-medium', ok ? 'text-positive' : 'text-negative')}>
          {invertLabel ? (ok ? 'Active' : 'Halted') : ok ? 'Normal' : 'Tripped'}
        </span>
      </div>
    </div>
  )
}
