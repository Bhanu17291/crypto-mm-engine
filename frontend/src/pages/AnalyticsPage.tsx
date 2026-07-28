import { PnlBreakdownChart } from '@/components/analytics/PnlBreakdownChart'
import { TradeStatsCard } from '@/components/analytics/TradeStatsCard'
import { HistoryChartsCard } from '@/components/dashboard/HistoryChartsCard'
import { useEngineStore } from '@/store/engine-store'
import { useFills } from '@/hooks/useFills'

export function AnalyticsPage() {
  const history = useEngineStore((s) => s.history)
  const { data: fills } = useFills()

  return (
    <div className="space-y-4 py-4">
      <p className="text-xs text-muted-foreground">
        These stats cover this browser session only (since the dashboard connected) - the engine
        doesn't persist historical data yet, so there's no multi-day Sharpe/Sortino/drawdown here,
        just what's actually been observed live.
      </p>

      <TradeStatsCard fills={fills ?? []} history={history} />

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        <PnlBreakdownChart history={history} />
        <HistoryChartsCard history={history} />
      </div>
    </div>
  )
}
