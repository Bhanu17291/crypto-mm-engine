import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { EmptyState } from '@/components/ui/empty-state'
import { Activity } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatPrice, formatQty, formatTime } from '@/lib/format'
import type { TradeTapeEvent } from '@/types/status'

export function TradeTape({ trades, loading }: { trades: TradeTapeEvent[]; loading?: boolean }) {
  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-lg shadow-black/20">
      <span className="text-xs font-medium text-muted-foreground">Trade Tape</span>

      {loading ? (
        <div className="space-y-1.5">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-5 w-full" />
          ))}
        </div>
      ) : trades.length === 0 ? (
        <EmptyState
          icon={Activity}
          title="No trades yet"
          description="The public tape fills in as the market trades — this isn't limited to our own orders."
        />
      ) : (
        <div className="max-h-80 space-y-0.5 overflow-y-auto font-mono text-xs">
          {trades.slice(0, 60).map((trade, i) => {
            // is_buyer_maker: true -> the resting order was a bid, so this
            // trade was sell-initiated (aggressor sold into the bid).
            const sellInitiated = trade.is_buyer_maker
            return (
              <div key={i} className="flex justify-between px-1 py-0.5">
                <span className={cn(sellInitiated ? 'text-negative' : 'text-positive')}>
                  {formatPrice(trade.price)}
                </span>
                <span className="text-foreground/70">{formatQty(trade.quantity)}</span>
                <span className="text-muted-foreground">{formatTime(trade.timestamp_ms)}</span>
              </div>
            )
          })}
        </div>
      )}
    </Card>
  )
}
