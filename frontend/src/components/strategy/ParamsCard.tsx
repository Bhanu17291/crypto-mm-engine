import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { QuotingParamsStatus } from '@/types/status'

const ROWS: { key: keyof QuotingParamsStatus; label: string; symbol: string; format: (v: number) => string }[] = [
  { key: 'risk_aversion', label: 'Risk Aversion', symbol: 'γ', format: (v) => v.toFixed(4) },
  { key: 'order_arrival_intensity', label: 'Order Arrival Intensity', symbol: 'κ', format: (v) => v.toFixed(4) },
  { key: 'volatility', label: 'Volatility', symbol: 'σ', format: (v) => v.toFixed(6) },
  { key: 'time_horizon_s', label: 'Time Horizon', symbol: 'T', format: (v) => `${v.toFixed(0)}s` },
  { key: 'max_inventory', label: 'Max Inventory', symbol: 'q_max', format: (v) => v.toFixed(6) },
  { key: 'quote_size', label: 'Quote Size', symbol: 'δq', format: (v) => v.toFixed(6) },
]

export function ParamsCard({ params }: { params: QuotingParamsStatus | null }) {
  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-lg shadow-black/20">
      <span className="text-xs font-medium text-muted-foreground">
        Avellaneda-Stoikov Parameters
      </span>

      {!params ? (
        <div className="space-y-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </div>
      ) : (
        <div className="divide-y divide-border/60">
          {ROWS.map((row) => (
            <div key={row.key} className="flex items-center justify-between py-2 text-sm">
              <div className="flex items-baseline gap-2">
                <span className="font-mono text-xs text-brand">{row.symbol}</span>
                <span className="text-muted-foreground">{row.label}</span>
              </div>
              <span className="font-mono tabular-nums">{row.format(params[row.key])}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
