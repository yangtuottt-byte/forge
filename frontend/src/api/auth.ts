import { request } from './client'
import type { Token, UserOut } from './types'

// 认证接口
export async function register(email: string, password: string): Promise<Token> {
  return request<Token>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export async function login(email: string, password: string): Promise<Token> {
  return request<Token>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export async function getMe(): Promise<UserOut> {
  return request<UserOut>('/users/me')
}
