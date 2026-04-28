import type { PropsWithChildren } from 'react'
import { Center, Loader } from '@mantine/core'
import { Navigate } from 'react-router-dom'
import { useAuth } from './use-auth'

export function GuestOnlyRoute({ children }: PropsWithChildren) {
  const { seller, isLoading } = useAuth()

  if (isLoading) {
    return (
      <Center mih="100vh">
        <Loader color="brand.7" />
      </Center>
    )
  }

  if (seller) {
    return <Navigate to="/app" replace />
  }

  return children
}
