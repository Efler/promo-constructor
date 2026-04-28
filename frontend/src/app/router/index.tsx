import { Navigate, RouterProvider, createBrowserRouter } from 'react-router-dom'
import { GuestOnlyRoute } from '../../features/auth/GuestOnlyRoute'
import { RequireAuth } from '../../features/auth/RequireAuth'
import { MechanicsOverviewPage } from '../../pages/home/MechanicsOverviewPage'
import { MechanicWorkspacePage } from '../../pages/home/MechanicWorkspacePage'
import { PrivateLayout } from '../../pages/home/PrivateLayout'
import { LoginPage } from '../../pages/login/LoginPage'

const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/app" replace />,
  },
  {
    path: '/login',
    element: (
      <GuestOnlyRoute>
        <LoginPage />
      </GuestOnlyRoute>
    ),
  },
  {
    path: '/app',
    element: (
      <RequireAuth>
        <PrivateLayout />
      </RequireAuth>
    ),
    children: [
      {
        index: true,
        element: <MechanicsOverviewPage />,
      },
      {
        path: 'promotions',
        element: (
          <MechanicWorkspacePage
            badge="Beta"
            title="Акции"
            description="Здесь будет сценарий создания и настройки акций для продавца."
            highlights={[
              'Базовые параметры акции',
              'Товары и ограничения',
              'Подготовка логики расчета',
            ]}
          />
        ),
      },
      {
        path: 'promocodes',
        element: (
          <MechanicWorkspacePage
            badge="Beta"
            title="Промокоды"
            description="Этот экран зарезервирован под будущий конструктор промокодов."
            highlights={[
              'Правила применения',
              'Срок действия и лимиты',
              'Привязка к seller context',
            ]}
          />
        ),
      },
      {
        path: 'bundles',
        element: (
          <MechanicWorkspacePage
            badge="Beta"
            title="Комплекты"
            description="Здесь позже появится настройка механики товарных комплектов."
            highlights={[
              'Состав комплектов',
              'Бонусы и скидки',
              'Проверка совместимости товаров',
            ]}
          />
        ),
      },
      {
        path: '*',
        element: <Navigate to="/app" replace />,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
