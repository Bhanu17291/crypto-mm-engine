import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { EmptyState } from '@/components/ui/empty-state'
import { ListOrdered } from 'lucide-react'
import { formatPrice, formatQty } from '@/lib/format'
import type { StatusSnapshot } from '@/types/status'

export function LiveOrdersCard({ status }: { status: StatusSnapshot | null }) {
  const orders = [
    status?.bid_order_id && status.quote.bid_price != null
      ? { id: status.bid_order_id, side: 'bid' as const, price: status.quote.bid_price, size: status.quote.bid_size }
      : null,
    status?.ask_order_id && status.quote.ask_price != null
      ? { id: status.ask_order_id, side: 'ask' as const, price: status.quote.ask_price, size: status.quote.ask_size }
      : null,
  ].filter((o): o is { id: string; side: 'bid' | 'ask'; price: number; size: number } => o != null)

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-lg shadow-black/20">
      <span className="text-xs font-medium text-muted-foreground">Live Orders</span>

      {!status ? (
        <div className="space-y-2">
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
        </div>
      ) : orders.length === 0 ? (
        <EmptyState
          icon={ListOrdered}
          title="No resting orders"
          description="Quotes are being withheld or between requotes — they'll appear here once placed."
        />
      ) : (
        <div className="space-y-2">
          {orders.map((order) => (
            <div
              key={order.id}
              className="flex items-center justify-between rounded-lg border border-border/60 bg-muted/30 p-3"
            >
              <div className="flex items-center gap-2">
                <Badge
                  className={
                    order.side === 'bid'
                      ? 'bg-positive-muted text-positive'
                      : 'bg-negative-muted text-negative'
                  }
                >
                  {order.side.toUpperCase()}
                </Badge>
                <span className="font-mono text-xs text-muted-foreground">#{order.id}</span>
              </div>
              <div className="text-right font-mono text-sm">
                <div>{formatPrice(order.price)}</div>
                <div className="text-[11px] text-muted-foreground">{formatQty(order.size)}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
