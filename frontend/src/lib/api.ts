import type { CancelEvent, FillEvent, StatusSnapshot, TradeTapeEvent } from '@/types/status'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8010'
export const WS_STATUS_URL =
  import.meta.env.VITE_WS_STATUS_URL ?? API_BASE_URL.replace(/^http/, 'ws') + '/ws/status'

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`)
  if (!response.ok) throw new Error(`GET ${path} failed: ${response.status}`)
  return response.json()
}

export function fetchStatus(): Promise<StatusSnapshot | null> {
  return getJson('/api/status')
}

export function fetchFills(): Promise<FillEvent[]> {
  return getJson('/api/fills')
}

export function fetchTrades(): Promise<TradeTapeEvent[]> {
  return getJson('/api/trades')
}

export function fetchCancellations(): Promise<CancelEvent[]> {
  return getJson('/api/cancellations')
}
