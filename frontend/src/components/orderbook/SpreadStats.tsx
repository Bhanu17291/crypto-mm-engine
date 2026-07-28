import { StatCard } from '@/components/dashboard/StatCard'
import { Layers, Percent, Ruler, Target } from 'lucide-react'
import { formatPrice } from '@/lib/format'
import type { StatusSnapshot } from '@/types/status'

export function SpreadStats({ status }: { status: StatusSnapshot | null }) {
  const bestBid = status?.book?.bids?.[0] ?? null
  const bestAsk = status?.book?.asks?.[0] ?? null

  const spread = bestBid && bestAsk ? bestAsk.price - bestBid.price : null
  const spreadBps =
    spread != null && status ? (spread / status.mid_price) * 10_000 : null

  // Microprice: mid weighted toward whichever side has less resting size,
  // since that side is more likely to move next - a standard short-horizon
  // fair-value estimate, distinct from the plain arithmetic mid.
  const microprice =
    bestBid && bestAsk
      ? (bestBid.price * bestAsk.quantity + bestAsk.price * bestBid.quantity) /
        (bestBid.quantity + bestAsk.quantity)
      : null

  return (
    <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
      <StatCard label="Mid Price" value={status?.mid_price ?? null} format={formatPrice} icon={Target} tone="neutral" />
      <StatCard label="Microprice" value={microprice} format={formatPrice} icon={Layers} tone="neutral" />
      <StatCard label="Spread" value={spread} format={formatPrice} icon={Ruler} tone="neutral" />
      <StatCard
        label="Spread (bps)"
        value={spreadBps}
        format={(v) => v.toFixed(1)}
        icon={Percent}
        tone="neutral"
      />
    </div>
  )
}
