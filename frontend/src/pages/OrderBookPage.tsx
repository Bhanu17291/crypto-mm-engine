import { DepthLadder } from '@/components/orderbook/DepthLadder'
import { SpreadStats } from '@/components/orderbook/SpreadStats'
import { ImbalanceGauge } from '@/components/orderbook/ImbalanceGauge'
import { TradeTape } from '@/components/orderbook/TradeTape'
import { useEngineStore } from '@/store/engine-store'
import { useTrades } from '@/hooks/useTrades'

export function OrderBookPage() {
  const status = useEngineStore((s) => s.status)
  const { data: trades, isLoading: tradesLoading } = useTrades()

  return (
    <div className="space-y-4 py-4">
      <SpreadStats status={status} />

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <DepthLadder
            bids={status?.book?.bids ?? []}
            asks={status?.book?.asks ?? []}
            ourBidPrice={status?.quote?.bid_price ?? null}
            ourAskPrice={status?.quote?.ask_price ?? null}
          />
        </div>
        <div className="space-y-3">
          <ImbalanceGauge bids={status?.book?.bids ?? []} asks={status?.book?.asks ?? []} />
          <TradeTape trades={trades ?? []} loading={tradesLoading} />
        </div>
      </div>
    </div>
  )
}
