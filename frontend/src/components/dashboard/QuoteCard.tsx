import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { formatPrice } from '@/lib/format'
import type { StatusSnapshot } from '@/types/status'

export function QuoteCard({ status }: { status: StatusSnapshot | null }) {
  const spread =
    status?.quote.bid_price != null && status?.quote.ask_price != null
      ? status.quote.ask_price - status.quote.bid_price
      : null

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-lg shadow-black/20">
      <span className="text-xs font-medium text-muted-foreground">Current Quotes</span>

      {!status ? (
        <div className="space-y-2">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-3">
            <Side
              label="Bid"
              price={status.quote.bid_price}
              size={status.quote.bid_size}
              tone="positive"
            />
            <Side
              label="Ask"
              price={status.quote.ask_price}
              size={status.quote.ask_size}
              tone="negative"
            />
          </div>
          <div className="flex items-center justify-between border-t border-border/60 pt-3 text-xs text-muted-foreground">
            <span>
              Mid <span className="font-mono text-foreground">{formatPrice(status.mid_price)}</span>
            </span>
            <span>
              Spread{' '}
              <span className="font-mono text-foreground">
                {spread != null ? formatPrice(spread) : '—'}
              </span>
            </span>
          </div>
        </>
      )}
    </Card>
  )
}

function Side({
  label,
  price,
  size,
  tone,
}: {
  label: string
  price: number | null
  size: number
  tone: 'positive' | 'negative'
}) {
  return (
    <div className="rounded-lg bg-muted/50 p-3">
      <div className={`text-[11px] font-medium ${tone === 'positive' ? 'text-positive' : 'text-negative'}`}>
        {label}
      </div>
      <div className="mt-1 font-mono text-lg font-medium tabular-nums">
        {price != null ? formatPrice(price) : '—'}
      </div>
      <div className="font-mono text-[11px] text-muted-foreground">{size.toFixed(4)}</div>
    </div>
  )
}
