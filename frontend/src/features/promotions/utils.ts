import dayjs from 'dayjs'
import type { MarketplacePromotion } from './api'

export function isDateInsidePromotion(
  date: string,
  promotion: MarketplacePromotion,
) {
  const calendarDate = dayjs(date)
  return (
    !calendarDate.isBefore(dayjs(promotion.starts_on), 'day') &&
    !calendarDate.isAfter(dayjs(promotion.ends_on), 'day')
  )
}
