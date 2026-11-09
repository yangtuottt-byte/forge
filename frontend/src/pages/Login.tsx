import { useState, type FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { Button } from '../components/Button'
import { Input } from '../components/Input'

// 登录页:邮箱 + 密码 → auth.login → 跳目标(默认 /dashboard)
export function Login() {
  const { login, token } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from =
    (location.state as { from?: { pathname: string } } | null)?.from?.pathname ||
    '/dashboard'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // 已在登录态 → 直接跳走
  if (token) return <Navigate to={from} replace />

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setError('请填写邮箱和密码')
      return
    }
    setLoading(true)
    setError('')
    try {
      await login(email, password)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-full items-center justify-center px-6">
      <div className="w-full max-w-sm rounded-xl border border-slate-800 bg-slate-900/40 p-8">
        <h1 className="text-lg font-semibold">登录 Forge</h1>
        <p className="mt-1 text-sm text-slate-400">用你的邮箱登录平台</p>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <div>
            <label className="mb-1 block text-sm text-slate-300">邮箱</label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-slate-300">密码</label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </div>
          {error ? <p className="text-sm text-rose-400">{error}</p> : null}
          <Button type="submit" loading={loading} className="w-full">
            登录
          </Button>
        </form>

        <p className="mt-4 text-sm text-slate-400">
          没有账号?{' '}
          <Link to="/register" className="text-indigo-400 hover:underline">
            注册
          </Link>
        </p>
      </div>
    </div>
  )
}
