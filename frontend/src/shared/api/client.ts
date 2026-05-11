const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/ui-api/v1'

type ParseMode = 'json' | 'text' | 'void'

type ApiRequestOptions = Omit<RequestInit, 'body'> & {
  body?: BodyInit | Record<string, unknown>
  parseAs?: ParseMode
}

export class ApiError extends Error {
  status: number
  data: unknown

  constructor(message: string, status: number, data: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

export async function apiRequest<T = void>(
  path: string,
  options: ApiRequestOptions = {},
) {
  const { body, headers, parseAs = 'json', ...init } = options
  const requestHeaders = new Headers(headers)

  let requestBody: BodyInit | undefined

  if (body instanceof FormData || typeof body === 'string' || body instanceof URLSearchParams) {
    requestBody = body
  } else if (body !== undefined) {
    requestHeaders.set('Content-Type', 'application/json')
    requestBody = JSON.stringify(body)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
    ...init,
    headers: requestHeaders,
    body: requestBody,
  })

  if (parseAs === 'void') {
    if (!response.ok) {
      throw new ApiError(response.statusText, response.status, null)
    }

    return undefined as T
  }

  const contentType = response.headers.get('content-type') ?? ''
  const payload =
    contentType.includes('application/json') ? await response.json() : await response.text()

  if (!response.ok) {
    throw new ApiError(response.statusText, response.status, payload)
  }

  if (parseAs === 'text') {
    return payload as T
  }

  return payload as T
}
