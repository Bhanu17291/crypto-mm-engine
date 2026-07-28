import { useMemo } from 'react'
import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Card } from '@/components/ui/card'
import { formatTime, formatUsd } from '@/lib/format'
import type { StatusSnapshot } from '@/types/status'

const AXIS_STYLE = { fontSize: 11, fill: 'var(--muted-foreground)' }

export function PnlBreakdownChart({ history }: { history: StatusSnapshot[] }) {
  const data = useMemo(
    () =>
      history.map((s) => ({
        t: s.timestamp_ms,
        realized: s.realized_pnl,
        unrealized: s.unrealized_pnl,
      })),
    [history],
  )
  const empty = data.length < 2

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-lg shadow-black/20">
      <span className="text-xs font-medium text-muted-foreground">
        Realized vs. Unrealized P&L (this session)
      </span>

      {empty ? (
        <div className="flex h-[260px] items-center justify-center text-xs text-muted-foreground">
          Collecting data…
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={data} margin={{ left: 0, right: 8, top: 8, bottom: 0 }}>
            <defs>
              <linearGradient id="realizedFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--positive)" stopOpacity={0.3} />
                <stop offset="100%" stopColor="var(--positive)" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="unrealizedFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--brand)" stopOpacity={0.3} />
                <stop offset="100%" stopColor="var(--brand)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="var(--border)" vertical={false} />
            <XAxis dataKey="t" tickFormatter={formatTime} tick={AXIS_STYLE} axisLine={false} tickLine={false} minTickGap={40} />
            <YAxis tick={AXIS_STYLE} axisLine={false} tickLine={false} width={64} tickFormatter={formatUsd} />
            <Tooltip
              labelFormatter={(v) => formatTime(v as number)}
              formatter={(value) => formatUsd(Number(value))}
              contentStyle={{
                background: 'var(--popover)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Area type="monotone" dataKey="realized" name="Realized" stroke="var(--positive)" strokeWidth={2} fill="url(#realizedFill)" isAnimationActive={false} />
            <Area type="monotone" dataKey="unrealized" name="Unrealized" stroke="var(--brand)" strokeWidth={2} fill="url(#unrealizedFill)" isAnimationActive={false} />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}
