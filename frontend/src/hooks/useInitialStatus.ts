import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchStatus } from '@/lib/api'
import { useEngineStore } from '@/store/engine-store'

/** REST fetch on mount so the dashboard isn't blank while waiting for the
 * next WS broadcast (the backend only pushes on change, at most every
 * 500ms) - the WS hook takes over from here. */
export function useInitialStatus() {
  const setStatus = useEngineStore((s) => s.setStatus)
  const query = useQuery({ queryKey: ['status'], queryFn: fetchStatus })

  useEffect(() => {
    if (query.data) setStatus(query.data)
  }, [query.data, setStatus])

  return query
}
