import { apiRequest } from '../../shared/api/client'

export type PromotionParticipationStatus = 'active' | 'scheduled' | 'completed'

export type PromotionParticipation = {
  id: number
  promotion_id: string
  promotion_title: string
  selected_product_ids: number[]
  discount_percent: number
  joined_at: string
  status: PromotionParticipationStatus
}

export type PromotionParticipationListResponse = {
  items: PromotionParticipation[]
  seller: string
  message: string
}

export async function listPromotionParticipations() {
  return apiRequest<PromotionParticipationListResponse>('/promotions')
}
