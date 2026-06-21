import { useQuery } from '@tanstack/react-query'
import {
  getPromotion,
  listPromotionParticipations,
  listPromotions,
} from './api'

export function usePromotionsQuery() {
  return useQuery({
    queryKey: ['promotions', 'catalog'],
    queryFn: listPromotions,
  })
}

export function usePromotionParticipationsQuery() {
  return useQuery({
    queryKey: ['promotions', 'participations'],
    queryFn: listPromotionParticipations,
  })
}

export function usePromotionQuery(slug: string | undefined) {
  return useQuery({
    queryKey: ['promotions', 'detail', slug],
    queryFn: () => getPromotion(slug as string),
    enabled: Boolean(slug),
  })
}
