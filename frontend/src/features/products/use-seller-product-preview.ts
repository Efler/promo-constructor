import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '../../shared/api/client'

export type SellerProductPreviewItem = {
  id: number
  title: string
  brand: string | null
  description: string | null
  subject_name: string | null
  parent_name: string | null
  main_photo_url: string | null
  is_active: boolean
  item_count: number
  total_stock_qty: number
  min_price: string
  min_discounted_price: string | null
  max_discount_percent: number
  sizes: string[]
}

type UseSellerProductPreviewQueryOptions = {
  sellerId: number | null
  enabled?: boolean
}

export function useSellerProductPreviewQuery({
  sellerId,
  enabled = false,
}: UseSellerProductPreviewQueryOptions) {
  return useQuery({
    queryKey: ['seller-product-preview', sellerId],
    queryFn: () => apiRequest<SellerProductPreviewItem[]>('/products/bundle-cards'),
    enabled: enabled && sellerId !== null,
  })
}

export function formatProductMoney(value: string | null) {
  if (!value) {
    return null
  }

  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
  }).format(Number(value))
}
