import { apiRequest } from '../../shared/api/client'

export type DiscountMode = 'percent' | 'amount'
export type PromoType =
  | 'single_buyer_single_order'
  | 'all_buyers_once'
  | 'all_buyers_limited'
export type AudienceType =
  | 'all'
  | 'bought_last_half_year'
  | 'not_bought_last_half_year'
export type ProductScope = 'all' | 'selected'
export type CodeMode = 'generate' | 'manual'

export type PromocodeCreatePayload = {
  title: string
  starts_on: string
  ends_on: string
  discount_mode: DiscountMode
  discount_value: number
  promo_type: PromoType
  audience_type: AudienceType
  product_scope: ProductScope
  selected_product_ids: number[]
  code_mode: CodeMode
  manual_code: string | null
}

export type PromocodeRead = {
  id: number
  seller_id: number
  title: string
  starts_on: string
  ends_on: string
  discount_mode: DiscountMode
  discount_value: number
  promo_type: PromoType
  audience_type: AudienceType
  product_scope: ProductScope
  code: string
  selected_product_ids: number[]
  created_at: string
  updated_at: string
}

export type PromocodeCreateResponse = {
  message: string
  promocode: PromocodeRead
}

export type PromocodeListItem = {
  id: number
  title: string
  code: string
  starts_on: string
  ends_on: string
  discount_mode: DiscountMode
  discount_value: number
  status: 'active' | 'expired'
  created_at: string
}

export type PromocodeCodeAvailability = {
  code: string
  normalized_code: string
  is_available: boolean
}

export async function createPromocode(payload: PromocodeCreatePayload) {
  return apiRequest<PromocodeCreateResponse>('/promocodes', {
    method: 'POST',
    body: payload,
  })
}

export async function listPromocodes() {
  return apiRequest<PromocodeListItem[]>('/promocodes')
}

export async function getPromocodeCodeAvailability(code: string) {
  const params = new URLSearchParams({ code })
  return apiRequest<PromocodeCodeAvailability>(`/promocodes/code-availability?${params.toString()}`)
}
