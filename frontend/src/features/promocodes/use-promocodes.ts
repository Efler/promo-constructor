import { useQuery } from '@tanstack/react-query'
import { listPromocodes } from './api'

export function usePromocodesQuery() {
  return useQuery({
    queryKey: ['promocodes'],
    queryFn: listPromocodes,
  })
}
