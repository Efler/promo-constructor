import dayjs from 'dayjs'

export type MarketplacePromotionTone = 'brand' | 'teal' | 'orange' | 'blue' | 'grape'

export type MarketplacePromotion = {
  id: string
  title: string
  short_description: string
  starts_on: string
  ends_on: string
  join_deadline: string
  minimum_discount_percent: number
  minimum_stock_qty: number
  minimum_products: number
  eligible_parent_names: string[] | null
  benefits: [string, string?]
  tone: MarketplacePromotionTone
  featured: boolean
}

export type MarketplacePromotionStatus =
  | 'active'
  | 'ending_soon'
  | 'upcoming'
  | 'closed'

function relativeDate(days: number) {
  return dayjs().add(days, 'day').format('YYYY-MM-DD')
}

export const marketplacePromotions: MarketplacePromotion[] = [
  {
    id: 'summer-hit',
    title: 'Хиты лета',
    short_description:
      'Большая сезонная распродажа с дополнительным продвижением товаров в поиске и рекомендациях.',
    starts_on: relativeDate(-3),
    ends_on: relativeDate(11),
    join_deadline: relativeDate(5),
    minimum_discount_percent: 15,
    minimum_stock_qty: 5,
    minimum_products: 2,
    eligible_parent_names: null,
    benefits: [
      'Приоритетная витрина сезонных предложений',
      'Дополнительные показы в поиске',
    ],
    tone: 'brand',
    featured: true,
  },
  {
    id: 'fast-weekend',
    title: 'Быстрые выходные',
    short_description:
      'Короткая акция для товаров с хорошим остатком и быстрой конверсией в заказ.',
    starts_on: relativeDate(2),
    ends_on: relativeDate(5),
    join_deadline: relativeDate(1),
    minimum_discount_percent: 12,
    minimum_stock_qty: 3,
    minimum_products: 1,
    eligible_parent_names: null,
    benefits: [
      'Подборка выгодных предложений на главной',
      'Акционная плашка на весь период',
    ],
    tone: 'orange',
    featured: false,
  },
  {
    id: 'home-comfort',
    title: 'Неделя домашнего уюта',
    short_description:
      'Тематическая подборка товаров для дома, интерьера и освещения.',
    starts_on: relativeDate(9),
    ends_on: relativeDate(21),
    join_deadline: relativeDate(7),
    minimum_discount_percent: 20,
    minimum_stock_qty: 8,
    minimum_products: 2,
    eligible_parent_names: ['Товары для дома', 'Освещение'],
    benefits: [
      'Размещение в тематической подборке',
      'Повышенный приоритет в рекомендациях',
    ],
    tone: 'teal',
    featured: true,
  },
  {
    id: 'fashion-focus',
    title: 'Фокус на стиль',
    short_description:
      'Продвижение одежды и аксессуаров в специальной модной витрине маркетплейса.',
    starts_on: relativeDate(18),
    ends_on: relativeDate(31),
    join_deadline: relativeDate(15),
    minimum_discount_percent: 25,
    minimum_stock_qty: 5,
    minimum_products: 1,
    eligible_parent_names: ['Одежда', 'Аксессуары'],
    benefits: [
      'Попадание в модные подборки',
      'Больше показов в похожих товарах',
    ],
    tone: 'grape',
    featured: false,
  },
  {
    id: 'mega-price-drop',
    title: 'Мегаскидки месяца',
    short_description:
      'Главная распродажа месяца для товаров с глубокими скидками и достаточным запасом.',
    starts_on: relativeDate(38),
    ends_on: relativeDate(53),
    join_deadline: relativeDate(34),
    minimum_discount_percent: 30,
    minimum_stock_qty: 12,
    minimum_products: 3,
    eligible_parent_names: null,
    benefits: [
      'Максимальный охват акционной аудитории',
      'Отдельный лендинг распродажи',
    ],
    tone: 'blue',
    featured: true,
  },
]

export function getMarketplacePromotion(promotionId: string | undefined) {
  return marketplacePromotions.find((promotion) => promotion.id === promotionId) ?? null
}

export function getMarketplacePromotionStatus(
  promotion: MarketplacePromotion,
): MarketplacePromotionStatus {
  const today = dayjs().startOf('day')
  const startsOn = dayjs(promotion.starts_on)
  const endsOn = dayjs(promotion.ends_on)

  if (today.isAfter(endsOn)) {
    return 'closed'
  }

  if (today.isBefore(startsOn)) {
    return 'upcoming'
  }

  if (endsOn.diff(today, 'day') <= 3) {
    return 'ending_soon'
  }

  return 'active'
}

export function isPromotionJoinOpen(promotion: MarketplacePromotion) {
  return (
    getMarketplacePromotionStatus(promotion) !== 'closed' &&
    !dayjs().startOf('day').isAfter(dayjs(promotion.join_deadline))
  )
}

export function isDateInsidePromotion(date: string, promotion: MarketplacePromotion) {
  const calendarDate = dayjs(date)
  return (
    !calendarDate.isBefore(dayjs(promotion.starts_on), 'day') &&
    !calendarDate.isAfter(dayjs(promotion.ends_on), 'day')
  )
}
