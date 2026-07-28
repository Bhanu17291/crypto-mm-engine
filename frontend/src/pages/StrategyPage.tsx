import { ParamsCard } from '@/components/strategy/ParamsCard'
import { ReservationPriceCard } from '@/components/strategy/ReservationPriceCard'
import { DecisionHistoryChart } from '@/components/strategy/DecisionHistoryChart'
import { useEngineStore } from '@/store/engine-store'

export function StrategyPage() {
  const status = useEngineStore((s) => s.status)
  const history = useEngineStore((s) => s.history)

  return (
    <div className="space-y-4 py-4">
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
        <ParamsCard params={status?.quoting_params ?? null} />
        <div className="lg:col-span-2">
          <ReservationPriceCard status={status} />
        </div>
      </div>

      <DecisionHistoryChart history={history} />
    </div>
  )
}
