export const mechanics = [
  {
    key: 'overview',
    label: 'Обзор',
    to: '/app',
    isBeta: false,
    description: 'Главная страница с быстрым доступом к инструментам продавца.',
  },
  {
    key: 'promotions',
    label: 'Акции',
    to: '/app/promotions',
    isBeta: true,
    description: 'Запускайте акции для выбранных товаров и управляйте условиями показа.',
  },
  {
    key: 'promocodes',
    label: 'Промокоды',
    to: '/app/promocodes',
    isBeta: true,
    description: 'Создавайте промокоды, настраивайте скидку и условия применения.',
  },
  {
    key: 'bundles',
    label: 'Комплекты',
    to: '/app/bundles',
    isBeta: true,
    description: 'Объединяйте товары в комплекты и предлагайте готовые наборы по выгодной цене.',
  },
] as const
