import type { FillEvent, StatusSnapshot } from '@/types/status'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8010'
export const WS_STATUS_URL =
  import.meta.env.VITE_WS_STATUS_URL ?? API_BASE_URL.replace(/^http/, 'ws') + '/ws/status'

export async function fetchStatus(): Promise<StatusSnapshot | null> {
  const response = await fetch(`${API_BASE_URL}/api/status`)
  if (!response.ok) throw new Error(`GET /api/status failed: ${response.status}`)
  return response.json()
}

export async function fetchFills(): Promise<FillEvent[]> {
  const response = await fetch(`${API_BASE_URL}/api/fills`)
  if (!response.ok) throw new Error(`GET /api/fills failed: ${response.status}`)
  return response.json()
}
