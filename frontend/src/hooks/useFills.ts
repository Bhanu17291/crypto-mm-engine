import { useQuery } from '@tanstack/react-query'
import { fetchFills } from '@/lib/api'

export function useFills() {
  return useQuery({
    queryKey: ['fills'],
    queryFn: fetchFills,
    refetchInterval: 2000,
  })
}
