import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import type { RiskStatus } from '@/types/status'

export function ControlsCard({ risk }: { risk: RiskStatus | null }) {
  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-lg shadow-black/20">
      <span className="text-xs font-medium text-muted-foreground">Trading Controls</span>

      {!risk ? (
        <div className="space-y-2">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      ) : (
        <div className="space-y-3">
          <ControlRow
            label="Kill Switch"
            description="Trips when daily P&L breaches the max loss limit."
            tripped={risk.kill_switch_tripped}
          />
          <ControlRow
            label="Circuit Breaker"
            description="Trips when the fill rate drifts outside its expected band."
            tripped={risk.circuit_breaker_tripped}
          />
        </div>
      )}
    </Card>
  )
}

function ControlRow({
  label,
  description,
  tripped,
}: {
  label: string
  description: string
  tripped: boolean
}) {
  return (
    <div
      className={cn(
        'rounded-lg border p-3',
        tripped ? 'border-negative/30 bg-negative-muted' : 'border-border/60 bg-muted/30',
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{label}</span>
        <span
          className={cn(
            'flex items-center gap-1.5 text-xs font-medium',
            tripped ? 'text-negative' : 'text-positive',
          )}
        >
          <span className={cn('size-1.5 rounded-full', tripped ? 'bg-negative animate-pulse' : 'bg-positive')} />
          {tripped ? 'Tripped — needs manual reset' : 'Normal'}
        </span>
      </div>
      <p className="mt-1 text-[11px] text-muted-foreground">{description}</p>
    </div>
  )
}
