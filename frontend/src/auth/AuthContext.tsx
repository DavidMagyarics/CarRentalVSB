import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import type { User } from '../api'
import {
  clearStoredToken,
  fetchMe,
  getStoredToken,
  loginUser,
  registerUser,
  storeToken,
} from '../api'

interface AuthContextValue {
  user: User | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = getStoredToken()
    if (!stored) {
      setLoading(false)
      return
    }
    fetchMe(stored)
      .then((current) => {
        setToken(stored)
        setUser(current)
      })
      .catch(() => clearStoredToken())
      .finally(() => setLoading(false))
  }, [])

  async function login(email: string, password: string) {
    const result = await loginUser(email, password)
    storeToken(result.access_token)
    setToken(result.access_token)
    setUser(result.user)
  }

  async function register(name: string, email: string, password: string) {
    const result = await registerUser(name, email, password)
    storeToken(result.access_token)
    setToken(result.access_token)
    setUser(result.user)
  }

  function logout() {
    clearStoredToken()
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
