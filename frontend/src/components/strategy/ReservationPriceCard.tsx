import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { formatPrice, formatQty } from '@/lib/format'
import type { StatusSnapshot } from '@/types/status'

export function ReservationPriceCard({ status }: { status: StatusSnapshot | null }) {
  if (!status) {
    return (
      <Card className="gap-3 border-border/60 bg-card p-4 shadow-lg shadow-black/20">
        <span className="text-xs font-medium text-muted-foreground">Reservation Price</span>
        <Skeleton className="h-24 w-full" />
      </Card>
    )
  }

  const skew = status.reservation_price - status.mid_price
  const skewedByInventory = status.inventory !== 0

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-lg shadow-black/20">
      <span className="text-xs font-medium text-muted-foreground">Reservation Price</span>

      <div className="flex items-baseline gap-3">
        <span className="font-mono text-2xl font-medium tabular-nums">
          {formatPrice(status.reservation_price)}
        </span>
        <span
          className={`font-mono text-xs ${skew < 0 ? 'text-negative' : skew > 0 ? 'text-positive' : 'text-muted-foreground'}`}
        >
          {skew >= 0 ? '+' : ''}
          {formatPrice(skew)} vs mid
        </span>
      </div>

      <p className="text-xs leading-relaxed text-muted-foreground">
        {skewedByInventory ? (
          <>
            Inventory of <span className="font-mono text-foreground">{formatQty(status.inventory)}</span>{' '}
            pulls the reservation price {skew < 0 ? 'below' : 'above'} mid, skewing both quotes to{' '}
            {status.inventory > 0 ? 'encourage selling down the position' : 'encourage buying back the short'}.
          </>
        ) : (
          'Flat inventory - reservation price sits exactly at mid, quotes are symmetric.'
        )}
      </p>

      <div className="grid grid-cols-2 gap-3 border-t border-border/60 pt-3 text-xs">
        <div>
          <div className="text-muted-foreground">Optimal Spread</div>
          <div className="font-mono text-sm">{formatPrice(status.optimal_spread)}</div>
        </div>
        <div>
          <div className="text-muted-foreground">Time Remaining</div>
          <div className="font-mono text-sm">{Math.max(0, status.time_remaining_s).toFixed(0)}s</div>
        </div>
      </div>
    </Card>
  )
}
