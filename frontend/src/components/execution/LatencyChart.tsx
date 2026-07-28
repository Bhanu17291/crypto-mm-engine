import { useMemo } from 'react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Card } from '@/components/ui/card'
import { formatTime } from '@/lib/format'
import type { StatusSnapshot } from '@/types/status'

const AXIS_STYLE = { fontSize: 11, fill: 'var(--muted-foreground)' }

export function LatencyChart({ history }: { history: StatusSnapshot[] }) {
  const data = useMemo(
    () => history.map((s) => ({ t: s.timestamp_ms, latency: s.requote_latency_ms })),
    [history],
  )
  const empty = data.length < 2
  const avg = data.length ? data.reduce((sum, d) => sum + d.latency, 0) / data.length : null

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-lg shadow-black/20">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground">Requote Latency</span>
        {avg != null && (
          <span className="font-mono text-xs text-muted-foreground">avg {avg.toFixed(1)}ms</span>
        )}
      </div>

      {empty ? (
        <div className="flex h-[180px] items-center justify-center text-xs text-muted-foreground">
          Collecting data…
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={data} margin={{ left: 0, right: 8, top: 8, bottom: 0 }}>
            <defs>
              <linearGradient id="latencyFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--chart-3)" stopOpacity={0.3} />
                <stop offset="100%" stopColor="var(--chart-3)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="var(--border)" vertical={false} />
            <XAxis dataKey="t" tickFormatter={formatTime} tick={AXIS_STYLE} axisLine={false} tickLine={false} minTickGap={40} />
            <YAxis tick={AXIS_STYLE} axisLine={false} tickLine={false} width={40} tickFormatter={(v) => `${v}ms`} />
            <Tooltip
              labelFormatter={(v) => formatTime(v as number)}
              formatter={(value) => `${Number(value).toFixed(1)}ms`}
              contentStyle={{
                background: 'var(--popover)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Area type="monotone" dataKey="latency" stroke="var(--chart-3)" strokeWidth={2} fill="url(#latencyFill)" isAnimationActive={false} />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}
