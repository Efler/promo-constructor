import { Navigate, RouterProvider, createBrowserRouter } from 'react-router-dom'
import { GuestOnlyRoute } from '../../features/auth/GuestOnlyRoute'
import { RequireAuth } from '../../features/auth/RequireAuth'
import { BundleConstructorPage } from '../../pages/bundles/BundleConstructorPage'
import { BundleListPage } from '../../pages/bundles/BundleListPage'
import { MechanicsOverviewPage } from '../../pages/home/MechanicsOverviewPage'
import { PrivateLayout } from '../../pages/home/PrivateLayout'
import { LoginPage } from '../../pages/login/LoginPage'
import { PromocodeConstructorPage } from '../../pages/promocodes/PromocodeConstructorPage'
import { PromocodeListPage } from '../../pages/promocodes/PromocodeListPage'
import { SellerProfilePage } from '../../pages/profile/SellerProfilePage'
import { PromotionDashboardPage } from '../../pages/promotions/PromotionDashboardPage'
import { PromotionJoinPage } from '../../pages/promotions/PromotionJoinPage'

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
        path: 'profile',
        element: <SellerProfilePage />,
      },
      {
        path: 'promotions',
        element: <PromotionDashboardPage />,
      },
      {
        path: 'promotions/:promotionId/join',
        element: <PromotionJoinPage />,
      },
      {
        path: 'promocodes',
        element: <PromocodeListPage />,
      },
      {
        path: 'promocodes/new',
        element: <PromocodeConstructorPage />,
      },
      {
        path: 'bundles',
        element: <BundleListPage />,
      },
      {
        path: 'bundles/new',
        element: <BundleConstructorPage />,
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
