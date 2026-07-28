import { useQuery } from '@tanstack/react-query'
import { fetchCancellations } from '@/lib/api'

export function useCancellations() {
  return useQuery({
    queryKey: ['cancellations'],
    queryFn: fetchCancellations,
    refetchInterval: 2000,
  })
}
