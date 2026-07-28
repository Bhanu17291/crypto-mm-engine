import { Activity, Boxes, Coins, Gauge, TrendingUp, Wallet } from 'lucide-react'
import { StatCard } from '@/components/dashboard/StatCard'
import { QuoteCard } from '@/components/dashboard/QuoteCard'
import { RiskStatusCard } from '@/components/dashboard/RiskStatusCard'
import { FillsTable } from '@/components/dashboard/FillsTable'
import { HistoryChartsCard } from '@/components/dashboard/HistoryChartsCard'
import { useEngineStore } from '@/store/engine-store'
import { useFills } from '@/hooks/useFills'
import { formatPct, formatQty, formatUsd } from '@/lib/format'

export function DashboardPage() {
  const status = useEngineStore((s) => s.status)
  const history = useEngineStore((s) => s.history)
  const { data: fills, isLoading: fillsLoading } = useFills()

  const exposure = status ? Math.abs(status.inventory) / status.max_position : null

  return (
    <div className="space-y-4 py-4">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <StatCard label="Equity" value={status?.equity ?? null} format={formatUsd} icon={Wallet} tone="auto" />
        <StatCard
          label="Realized PnL"
          value={status?.realized_pnl ?? null}
          format={formatUsd}
          icon={TrendingUp}
          tone="auto"
        />
        <StatCard
          label="Unrealized PnL"
          value={status?.unrealized_pnl ?? null}
          format={formatUsd}
          icon={Activity}
          tone="auto"
        />
        <StatCard
          label="Inventory"
          value={status?.inventory ?? null}
          format={formatQty}
          icon={Boxes}
          tone="neutral"
        />
        <StatCard label="Exposure" value={exposure} format={formatPct} icon={Gauge} tone="neutral" />
        <StatCard
          label="Fees Paid"
          value={status?.fees_paid ?? null}
          format={formatUsd}
          icon={Coins}
          tone="neutral"
        />
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <HistoryChartsCard history={history} />
        </div>
        <div className="space-y-3">
          <QuoteCard status={status} />
          <RiskStatusCard status={status} />
        </div>
      </div>

      <FillsTable fills={fills ?? []} loading={fillsLoading} />
    </div>
  )
}
