import { RiskGauge } from '@/components/risk/RiskGauge'
import { FillRateRangeGauge } from '@/components/risk/FillRateRangeGauge'
import { ControlsCard } from '@/components/risk/ControlsCard'
import { HistoryChartsCard } from '@/components/dashboard/HistoryChartsCard'
import { useEngineStore } from '@/store/engine-store'
import { formatQty, formatUsd } from '@/lib/format'

export function RiskPage() {
  const status = useEngineStore((s) => s.status)
  const history = useEngineStore((s) => s.history)

  const dailyLossUsed = status ? Math.max(0, -status.equity) : null

  return (
    <div className="space-y-4 py-4">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        <RiskGauge
          label="Position Exposure"
          value={status?.inventory ?? null}
          max={status?.max_position ?? 1}
          format={formatQty}
          sublabel="|inventory| against max_position"
        />
        <RiskGauge
          label="Daily Loss Usage"
          value={dailyLossUsed}
          max={status?.risk_limits?.max_daily_loss ?? 1}
          format={formatUsd}
          sublabel="Kill switch trips at 100%"
        />
        <FillRateRangeGauge risk={status?.risk ?? null} limits={status?.risk_limits ?? null} />
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <HistoryChartsCard history={history} />
        </div>
        <ControlsCard risk={status?.risk ?? null} />
      </div>
    </div>
  )
}
