import { useMemo } from 'react'
import { StatCard } from '@/components/dashboard/StatCard'
import { ArrowLeftRight, Coins, Hash, Ruler } from 'lucide-react'
import { formatQty, formatUsd } from '@/lib/format'
import type { FillEvent, StatusSnapshot } from '@/types/status'

function nearestMidPrice(history: StatusSnapshot[], timestampMs: number): number | null {
  if (history.length === 0) return null
  let closest = history[0]
  let closestDiff = Math.abs(closest.timestamp_ms - timestampMs)
  for (const snapshot of history) {
    const diff = Math.abs(snapshot.timestamp_ms - timestampMs)
    if (diff < closestDiff) {
      closest = snapshot
      closestDiff = diff
    }
  }
  return closest.mid_price
}

export function TradeStatsCard({
  fills,
  history,
}: {
  fills: FillEvent[]
  history: StatusSnapshot[]
}) {
  const stats = useMemo(() => {
    if (fills.length === 0) return null

    const volume = fills.reduce((sum, f) => sum + f.quantity, 0)
    const fees = fills.reduce((sum, f) => sum + f.fee, 0)

    // Approximate: joins each fill against the closest snapshot we have in
    // this session's client-side history (live fills don't carry a
    // mid-price-at-fill field the way backtest fills do), so this is a
    // best-effort session estimate, not exact.
    const captures = fills
      .map((f) => {
        const mid = nearestMidPrice(history, f.timestamp_ms)
        if (mid == null) return null
        return f.side === 'bid' ? mid - f.price : f.price - mid
      })
      .filter((v): v is number => v != null)
    const avgCapture = captures.length ? captures.reduce((a, b) => a + b, 0) / captures.length : null

    return { volume, fees, avgCapture, count: fills.length }
  }, [fills, history])

  return (
    <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
      <StatCard label="Fill Count" value={stats?.count ?? null} format={(v) => v.toFixed(0)} icon={Hash} tone="neutral" />
      <StatCard label="Volume Traded" value={stats?.volume ?? null} format={formatQty} icon={ArrowLeftRight} tone="neutral" />
      <StatCard label="Fees Paid" value={stats?.fees ?? null} format={formatUsd} icon={Coins} tone="neutral" />
      <StatCard
        label="Avg Spread Capture"
        value={stats?.avgCapture ?? null}
        format={formatUsd}
        icon={Ruler}
        tone="auto"
        sublabel="approx, session-only"
      />
    </div>
  )
}
