import axios from 'axios'

const authApi = axios.create({
  baseURL: '/api/auth',
  timeout: 10000,
})

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  access_token: string
  token_type: string
  expires_in: number
}

export interface UserData {
  username: string
  role: string
}

export async function login(params: LoginParams): Promise<LoginResult> {
  const res = await authApi.post('/login', params)
  return res.data
}

export async function getMe(): Promise<{ success: boolean; data: UserData }> {
  const res = await authApi.get('/me')
  return res.data
}

export async function verifyToken(): Promise<{ success: boolean; data: UserData }> {
  const res = await authApi.get('/verify')
  return res.data
}

const TOKEN_KEY = 'aigc_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export function isAuthenticated(): boolean {
  return !!getToken()
}
