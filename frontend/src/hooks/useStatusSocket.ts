import { useEffect } from 'react'
import { WS_STATUS_URL } from '@/lib/api'
import { useEngineStore } from '@/store/engine-store'
import type { StatusSnapshot } from '@/types/status'

const INITIAL_DELAY_MS = 1000
const MAX_DELAY_MS = 15000

/** Mirrors the Python client's reconnect policy: geometric backoff, capped,
 * reset once a connection is actually established. */
export function useStatusSocket() {
  const setStatus = useEngineStore((s) => s.setStatus)
  const setConnected = useEngineStore((s) => s.setConnected)

  useEffect(() => {
    let socket: WebSocket | null = null
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null
    let attempt = 0
    let stopped = false

    const connect = () => {
      socket = new WebSocket(WS_STATUS_URL)

      socket.onopen = () => {
        attempt = 0
        setConnected(true)
      }

      socket.onmessage = (event: MessageEvent<string>) => {
        const snapshot = JSON.parse(event.data) as StatusSnapshot
        setStatus(snapshot)
      }

      socket.onclose = () => {
        setConnected(false)
        if (stopped) return
        const delay = Math.min(INITIAL_DELAY_MS * 2 ** attempt, MAX_DELAY_MS)
        attempt += 1
        reconnectTimer = setTimeout(connect, delay)
      }

      socket.onerror = () => {
        socket?.close()
      }
    }

    connect()

    return () => {
      stopped = true
      if (reconnectTimer) clearTimeout(reconnectTimer)
      socket?.close()
    }
  }, [setStatus, setConnected])
}
