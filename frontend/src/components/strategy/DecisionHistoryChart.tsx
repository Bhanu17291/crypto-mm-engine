import { useMemo } from 'react'
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Card } from '@/components/ui/card'
import { formatPrice, formatTime } from '@/lib/format'
import type { StatusSnapshot } from '@/types/status'

const AXIS_STYLE = { fontSize: 11, fill: 'var(--muted-foreground)' }

export function DecisionHistoryChart({ history }: { history: StatusSnapshot[] }) {
  const data = useMemo(
    () =>
      history.map((s) => ({
        t: s.timestamp_ms,
        mid: s.mid_price,
        reservation: s.reservation_price,
        bid: s.quote.bid_price,
        ask: s.quote.ask_price,
      })),
    [history],
  )
  const empty = data.length < 2

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-none">
      <span className="text-xs font-medium text-muted-foreground">
        Mid vs. Reservation Price vs. Quotes
      </span>

      {empty ? (
        <div className="flex h-[260px] items-center justify-center text-xs text-muted-foreground">
          Collecting data…
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data} margin={{ left: 0, right: 8, top: 8, bottom: 0 }}>
            <CartesianGrid stroke="var(--border)" vertical={false} />
            <XAxis dataKey="t" tickFormatter={formatTime} tick={AXIS_STYLE} axisLine={false} tickLine={false} minTickGap={40} />
            <YAxis tick={AXIS_STYLE} axisLine={false} tickLine={false} width={64} tickFormatter={formatPrice} domain={['auto', 'auto']} />
            <Tooltip
              labelFormatter={(v) => formatTime(v as number)}
              formatter={(value) => formatPrice(Number(value))}
              contentStyle={{
                background: 'var(--popover)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line type="monotone" dataKey="mid" name="Mid" stroke="var(--muted-foreground)" strokeWidth={1.5} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="reservation" name="Reservation" stroke="var(--brand)" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="bid" name="Bid" stroke="var(--positive)" strokeWidth={1} dot={false} isAnimationActive={false} strokeDasharray="3 3" />
            <Line type="monotone" dataKey="ask" name="Ask" stroke="var(--negative)" strokeWidth={1} dot={false} isAnimationActive={false} strokeDasharray="3 3" />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}
