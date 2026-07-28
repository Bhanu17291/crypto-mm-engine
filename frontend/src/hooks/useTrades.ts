import { useQuery } from '@tanstack/react-query'
import { fetchTrades } from '@/lib/api'

export function useTrades() {
  return useQuery({
    queryKey: ['trades'],
    queryFn: fetchTrades,
    refetchInterval: 2000,
  })
}
