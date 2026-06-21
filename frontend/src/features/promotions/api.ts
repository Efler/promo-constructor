import { apiRequest } from '../../shared/api/client'

export type MarketplacePromotionTone = 'brand' | 'teal' | 'orange' | 'blue' | 'grape'
export type MarketplacePromotionStatus =
  | 'active'
  | 'ending_soon'
  | 'upcoming'
  | 'closed'
export type PromotionParticipationStatus = 'active' | 'scheduled' | 'completed'

export type MarketplacePromotion = {
  id: number
  slug: string
  title: string
  short_description: string
  starts_on: string
  ends_on: string
  join_deadline: string
  minimum_discount_percent: number
  minimum_stock_qty: number
  minimum_products: number
  category_scope: 'all' | 'selected'
  eligible_parent_ids: number[]
  eligible_parent_names: string[] | null
  benefits: string[]
  card_tone: MarketplacePromotionTone
  is_featured: boolean
  status: MarketplacePromotionStatus
  join_open: boolean
}

export type PromotionParticipation = {
  id: number
  promotion_id: number
  promotion_slug: string
  promotion_title: string
  selected_product_ids: number[]
  additional_discount_percent: number
  joined_at: string
  status: PromotionParticipationStatus
}

export type PromotionParticipationCreatePayload = {
  additional_discount_percent: number
  selected_product_ids: number[]
  price_change_confirmed: boolean
}

export type PromotionParticipationCreateResponse = {
  message: string
  participation: PromotionParticipation
}

export async function listPromotions() {
  return apiRequest<MarketplacePromotion[]>('/promotions')
}

export async function getPromotion(slug: string) {
  return apiRequest<MarketplacePromotion>(`/promotions/${encodeURIComponent(slug)}`)
}

export async function listPromotionParticipations() {
  return apiRequest<PromotionParticipation[]>('/promotions/participations')
}

export async function createPromotionParticipation(
  slug: string,
  payload: PromotionParticipationCreatePayload,
) {
  return apiRequest<PromotionParticipationCreateResponse>(
    `/promotions/${encodeURIComponent(slug)}/participations`,
    {
      method: 'POST',
      body: payload,
    },
  )
}
