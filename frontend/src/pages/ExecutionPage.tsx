import { LiveOrdersCard } from '@/components/execution/LiveOrdersCard'
import { CancelledOrdersTable } from '@/components/execution/CancelledOrdersTable'
import { LatencyChart } from '@/components/execution/LatencyChart'
import { FillsTable } from '@/components/dashboard/FillsTable'
import { useEngineStore } from '@/store/engine-store'
import { useFills } from '@/hooks/useFills'
import { useCancellations } from '@/hooks/useCancellations'

export function ExecutionPage() {
  const status = useEngineStore((s) => s.status)
  const history = useEngineStore((s) => s.history)
  const { data: fills, isLoading: fillsLoading } = useFills()
  const { data: cancellations, isLoading: cancellationsLoading } = useCancellations()

  return (
    <div className="space-y-4 py-4">
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
        <LiveOrdersCard status={status} />
        <div className="lg:col-span-2">
          <LatencyChart history={history} />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        <FillsTable fills={fills ?? []} loading={fillsLoading} />
        <CancelledOrdersTable cancellations={cancellations ?? []} loading={cancellationsLoading} />
      </div>
    </div>
  )
}
