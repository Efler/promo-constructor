import { useQuery } from '@tanstack/react-query'
import { listPromotionParticipations } from './api'

export function usePromotionParticipationsQuery() {
  return useQuery({
    queryKey: ['promotions', 'participations'],
    queryFn: listPromotionParticipations,
  })
}
