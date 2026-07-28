import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { formatPrice, formatQty } from '@/lib/format'
import type { PriceLevelStatus } from '@/types/status'

export function DepthLadder({
  bids,
  asks,
  ourBidPrice,
  ourAskPrice,
}: {
  bids: PriceLevelStatus[]
  asks: PriceLevelStatus[]
  ourBidPrice: number | null
  ourAskPrice: number | null
}) {
  const maxQty = Math.max(
    1e-9,
    ...bids.map((l) => l.quantity),
    ...asks.map((l) => l.quantity),
  )
  const rows = Math.max(bids.length, asks.length, 1)

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-lg shadow-black/20">
      <span className="text-xs font-medium text-muted-foreground">Order Book</span>

      {bids.length === 0 && asks.length === 0 ? (
        <div className="space-y-1.5">
          {Array.from({ length: 10 }).map((_, i) => (
            <Skeleton key={i} className="h-6 w-full" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 font-mono text-xs">
          <div className="space-y-1">
            <Header label="Bids" />
            {Array.from({ length: rows }).map((_, i) => (
              <Row
                key={i}
                level={bids[i]}
                side="bid"
                maxQty={maxQty}
                highlighted={bids[i]?.price === ourBidPrice}
              />
            ))}
          </div>
          <div className="space-y-1">
            <Header label="Asks" />
            {Array.from({ length: rows }).map((_, i) => (
              <Row
                key={i}
                level={asks[i]}
                side="ask"
                maxQty={maxQty}
                highlighted={asks[i]?.price === ourAskPrice}
              />
            ))}
          </div>
        </div>
      )}
    </Card>
  )
}

function Header({ label }: { label: string }) {
  return (
    <div className="flex justify-between px-1 pb-1 text-[10px] font-sans font-medium uppercase tracking-wide text-muted-foreground">
      <span>{label}</span>
      <span>Qty</span>
    </div>
  )
}

function Row({
  level,
  side,
  maxQty,
  highlighted,
}: {
  level: PriceLevelStatus | undefined
  side: 'bid' | 'ask'
  maxQty: number
  highlighted: boolean
}) {
  if (!level) return <div className="h-6" />
  const width = Math.max(4, (level.quantity / maxQty) * 100)
  const isBid = side === 'bid'

  return (
    <div className="relative flex h-6 items-center justify-between overflow-hidden rounded px-1 tabular-nums">
      <div
        className={`absolute inset-y-0 ${isBid ? 'right-0 bg-positive-muted' : 'left-0 bg-negative-muted'}`}
        style={{ width: `${width}%` }}
      />
      <span className={`relative z-10 ${isBid ? 'text-positive' : 'text-negative'} ${highlighted ? 'font-bold' : ''}`}>
        {formatPrice(level.price)}
      </span>
      <span className="relative z-10 text-foreground/80">{formatQty(level.quantity)}</span>
    </div>
  )
}
