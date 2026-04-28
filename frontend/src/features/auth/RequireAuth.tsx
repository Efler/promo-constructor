import type { PropsWithChildren } from 'react'
import { Center, Loader } from '@mantine/core'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './use-auth'

export function RequireAuth({ children }: PropsWithChildren) {
  const { seller, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <Center mih="100vh">
        <Loader color="brand.7" />
      </Center>
    )
  }

  if (!seller) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return children
}
