import { Card } from '@/components/ui/card'
import type { PriceLevelStatus } from '@/types/status'

export function ImbalanceGauge({
  bids,
  asks,
}: {
  bids: PriceLevelStatus[]
  asks: PriceLevelStatus[]
}) {
  const bidVolume = bids.reduce((sum, l) => sum + l.quantity, 0)
  const askVolume = asks.reduce((sum, l) => sum + l.quantity, 0)
  const total = bidVolume + askVolume
  const bidPct = total > 0 ? (bidVolume / total) * 100 : 50

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-none">
      <span className="text-xs font-medium text-muted-foreground">Market Imbalance (top 20)</span>
      <div className="h-2.5 w-full overflow-hidden rounded-full bg-negative-muted">
        <div
          className="h-full rounded-full bg-positive transition-all duration-300"
          style={{ width: `${bidPct}%` }}
        />
      </div>
      <div className="flex justify-between font-mono text-xs">
        <span className="text-positive">{bidPct.toFixed(1)}% bid</span>
        <span className="text-negative">{(100 - bidPct).toFixed(1)}% ask</span>
      </div>
    </Card>
  )
}
