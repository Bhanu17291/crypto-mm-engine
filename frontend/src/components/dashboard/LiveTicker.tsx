import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Sparkline } from './Sparkline'
import { formatPrice } from '@/lib/format'
import type { StatusSnapshot } from '@/types/status'

export function LiveTicker({
  status,
  history,
}: {
  status: StatusSnapshot | null
  history: StatusSnapshot[]
}) {
  const prevPriceRef = useRef<number | null>(null)
  const [flash, setFlash] = useState<'up' | 'down' | null>(null)
  const [now, setNow] = useState(Date.now())

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [])

  const midPrice = status?.mid_price ?? null

  useEffect(() => {
    if (midPrice == null) return
    const prev = prevPriceRef.current
    if (prev != null && midPrice !== prev) {
      setFlash(midPrice > prev ? 'up' : 'down')
    }
    prevPriceRef.current = midPrice
  }, [midPrice])

  useEffect(() => {
    if (flash == null) return
    const timer = setTimeout(() => setFlash(null), 700)
    return () => clearTimeout(timer)
  }, [flash])

  const secondsAgo = status ? Math.max(0, Math.round((now - status.timestamp_ms) / 1000)) : null

  return (
    <Card className="flex-row items-center justify-between border-border/60 bg-card p-4 shadow-lg shadow-black/20">
      <div className="flex items-center gap-3">
        <span className="relative flex size-2.5">
          <span className="absolute inline-flex size-full animate-ping rounded-full bg-brand opacity-60" />
          <span className="relative inline-flex size-2.5 rounded-full bg-brand shadow-[0_0_8px_var(--brand)]" />
        </span>
        <div>
          <div className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
            {status?.symbol ? status.symbol.toUpperCase() : '—'} · Live Mid Price
          </div>
          <motion.div
            animate={{
              color:
                flash === 'up'
                  ? 'var(--positive)'
                  : flash === 'down'
                    ? 'var(--negative)'
                    : 'var(--foreground)',
            }}
            transition={{ duration: 0.4 }}
            className="font-mono text-2xl font-semibold tabular-nums"
          >
            {status ? formatPrice(status.mid_price) : 'waiting…'}
          </motion.div>
        </div>
      </div>

      <div className="hidden sm:block">
        <Sparkline values={history.slice(-40).map((h) => h.mid_price)} />
      </div>

      <div className="text-right font-mono text-xs text-muted-foreground">
        <div className="text-foreground/80">{history.length.toLocaleString()} updates</div>
        <div>{secondsAgo != null ? `${secondsAgo}s ago` : 'connecting…'}</div>
      </div>
    </Card>
  )
}
