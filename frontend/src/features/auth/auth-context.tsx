import type { PropsWithChildren } from 'react'
import { createContext, useContext } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ApiError, apiRequest } from '../../shared/api/client'

export type Seller = {
  username: string
  display_name: string
}

type LoginPayload = {
  username: string
  password: string
}

type AuthResponse = {
  message: string
  seller: Seller
}

type AuthContextValue = {
  seller: Seller | null
  isLoading: boolean
  login: (payload: LoginPayload) => Promise<Seller>
  logout: () => Promise<void>
  refreshSession: () => Promise<Seller | null>
}

const AuthContext = createContext<AuthContextValue | null>(null)

async function fetchCurrentSeller() {
  try {
    const response = await apiRequest<AuthResponse>('/auth/me')
    return response.seller
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null
    }

    throw error
  }
}

export function AuthProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient()

  const sessionQuery = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: fetchCurrentSeller,
  })

  const loginMutation = useMutation({
    mutationFn: async (payload: LoginPayload) => {
      const response = await apiRequest<AuthResponse>('/auth/login', {
        method: 'POST',
        body: payload,
      })

      return response.seller
    },
    onSuccess: (seller) => {
      queryClient.setQueryData(['auth', 'me'], seller)
    },
  })

  const logoutMutation = useMutation({
    mutationFn: async () => {
      await apiRequest('/auth/logout', {
        method: 'POST',
        parseAs: 'void',
      })
    },
    onSuccess: () => {
      queryClient.setQueryData(['auth', 'me'], null)
    },
  })

  const value: AuthContextValue = {
    seller: sessionQuery.data ?? null,
    isLoading: sessionQuery.isLoading,
    login: async (payload) => loginMutation.mutateAsync(payload),
    logout: async () => {
      await logoutMutation.mutateAsync()
    },
    refreshSession: async () => {
      const seller = await queryClient.fetchQuery({
        queryKey: ['auth', 'me'],
        queryFn: fetchCurrentSeller,
      })

      queryClient.setQueryData(['auth', 'me'], seller)
      return seller
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuthContext() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider.')
  }

  return context
}
