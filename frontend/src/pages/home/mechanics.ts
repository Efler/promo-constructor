export const mechanics = [
  {
    key: 'overview',
    label: 'Обзор',
    to: '/app',
    isBeta: false,
    description: 'Входная точка и выбор доступной механики.',
  },
  {
    key: 'promotions',
    label: 'Акции',
    to: '/app/promotions',
    isBeta: true,
    description: 'Будущие настройки промо-акций и параметров кампаний.',
  },
  {
    key: 'promocodes',
    label: 'Промокоды',
    to: '/app/promocodes',
    isBeta: true,
    description: 'Конструктор правил для промокодов и ограничений применения.',
  },
  {
    key: 'bundles',
    label: 'Комплекты',
    to: '/app/bundles',
    isBeta: true,
    description: 'Подготовка механики комплектов и связей между товарами.',
  },
] as const
