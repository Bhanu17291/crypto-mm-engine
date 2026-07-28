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
  fill_rate: number | null
}

export interface PriceLevelStatus {
  price: number
  quantity: number
}

export interface OrderBookStatus {
  bids: PriceLevelStatus[]
  asks: PriceLevelStatus[]
}

export interface QuotingParamsStatus {
  risk_aversion: number
  order_arrival_intensity: number
  volatility: number
  time_horizon_s: number
  max_inventory: number
  quote_size: number
}

export interface RiskLimitsStatus {
  max_position: number
  max_daily_loss: number
  max_stale_data_ms: number
  min_fill_rate: number
  max_fill_rate: number
  fill_rate_window: number
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
  reservation_price: number
  optimal_spread: number
  time_remaining_s: number
  bid_order_id: string | null
  ask_order_id: string | null
  requote_latency_ms: number
  book: OrderBookStatus
  quoting_params: QuotingParamsStatus
  risk_limits: RiskLimitsStatus
}

export interface FillEvent {
  order_id: string
  side: 'bid' | 'ask'
  price: number
  quantity: number
  fee: number
  timestamp_ms: number
}

export interface TradeTapeEvent {
  price: number
  quantity: number
  is_buyer_maker: boolean
  timestamp_ms: number
}

export interface CancelEvent {
  order_id: string
  timestamp_ms: number
}
