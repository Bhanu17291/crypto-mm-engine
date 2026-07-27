// Mirrors crypto_mm_engine.live.status (Pydantic models served by the API).

export interface QuoteStatus {
  bid_price: number | null
  bid_size: number
  ask_price: number | null
  ask_size: number
}

export interface RiskStatus {
  halted: boolean
  kill_switch_tripped: boolean
  circuit_breaker_tripped: boolean
}

export interface StatusSnapshot {
  timestamp_ms: number
  symbol: string
  mid_price: number
  inventory: number
  max_position: number
  realized_pnl: number
  unrealized_pnl: number
  equity: number
  fees_paid: number
  quote: QuoteStatus
  risk: RiskStatus
}

export interface FillEvent {
  order_id: string
  side: 'bid' | 'ask'
  price: number
  quantity: number
  fee: number
  timestamp_ms: number
}
