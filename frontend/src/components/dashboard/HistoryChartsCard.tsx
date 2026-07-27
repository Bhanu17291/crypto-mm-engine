import { useMemo } from 'react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Card } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatPrice, formatQty, formatTime } from '@/lib/format'
import type { StatusSnapshot } from '@/types/status'

const AXIS_STYLE = { fontSize: 11, fill: 'var(--muted-foreground)' }

function ChartTooltip({
  active,
  payload,
  label,
  valueFormat,
}: {
  active?: boolean
  payload?: { value: number }[]
  label?: number
  valueFormat: (v: number) => string
}) {
  if (!active || !payload?.length || label == null) return null
  return (
    <div className="rounded-lg border border-border bg-popover px-3 py-2 text-xs shadow-md">
      <div className="text-muted-foreground">{formatTime(label)}</div>
      <div className="font-mono font-medium text-foreground">{valueFormat(payload[0].value)}</div>
    </div>
  )
}

export function HistoryChartsCard({ history }: { history: StatusSnapshot[] }) {
  const data = useMemo(
    () => history.map((s) => ({ t: s.timestamp_ms, equity: s.equity, inventory: s.inventory })),
    [history],
  )
  const empty = data.length < 2

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-none">
      <Tabs defaultValue="equity">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-muted-foreground">History</span>
          <TabsList className="h-7">
            <TabsTrigger value="equity" className="text-xs">
              Equity Curve
            </TabsTrigger>
            <TabsTrigger value="inventory" className="text-xs">
              Inventory
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="equity">
          {empty ? (
            <EmptyChart />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={data} margin={{ left: 0, right: 8, top: 8, bottom: 0 }}>
                <defs>
                  <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--brand)" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="var(--brand)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="var(--border)" vertical={false} />
                <XAxis dataKey="t" tickFormatter={formatTime} tick={AXIS_STYLE} axisLine={false} tickLine={false} minTickGap={40} />
                <YAxis tick={AXIS_STYLE} axisLine={false} tickLine={false} width={56} tickFormatter={formatPrice} domain={['auto', 'auto']} />
                <Tooltip content={<ChartTooltip valueFormat={formatPrice} />} />
                <Area
                  type="monotone"
                  dataKey="equity"
                  stroke="var(--brand)"
                  strokeWidth={2}
                  fill="url(#equityFill)"
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </TabsContent>

        <TabsContent value="inventory">
          {empty ? (
            <EmptyChart />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={data} margin={{ left: 0, right: 8, top: 8, bottom: 0 }}>
                <CartesianGrid stroke="var(--border)" vertical={false} />
                <XAxis dataKey="t" tickFormatter={formatTime} tick={AXIS_STYLE} axisLine={false} tickLine={false} minTickGap={40} />
                <YAxis tick={AXIS_STYLE} axisLine={false} tickLine={false} width={56} tickFormatter={formatQty} domain={['auto', 'auto']} />
                <Tooltip content={<ChartTooltip valueFormat={formatQty} />} />
                <Line
                  type="stepAfter"
                  dataKey="inventory"
                  stroke="var(--chart-3)"
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </TabsContent>
      </Tabs>
    </Card>
  )
}

function EmptyChart() {
  return (
    <div className="flex h-[220px] items-center justify-center text-xs text-muted-foreground">
      Collecting data…
    </div>
  )
}
