import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { Button } from '../components/Button'
import { Input } from '../components/Input'

// 注册页:邮箱 + 密码 → auth.register(注册即返回 token,免二次登录)→ /dashboard
export function Register() {
  const { register, token } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (token) return <Navigate to="/dashboard" replace />

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setError('请填写邮箱和密码')
      return
    }
    if (password.length < 8) {
      setError('密码至少 8 位')
      return
    }
    setLoading(true)
    setError('')
    try {
      await register(email, password)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : '注册失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-full items-center justify-center px-6">
      <div className="w-full max-w-sm rounded-xl border border-slate-800 bg-slate-900/40 p-8">
        <h1 className="text-lg font-semibold">注册 Forge</h1>
        <p className="mt-1 text-sm text-slate-400">创建一个平台账号</p>

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
              placeholder="至少 8 位"
              autoComplete="new-password"
            />
          </div>
          {error ? <p className="text-sm text-rose-400">{error}</p> : null}
          <Button type="submit" loading={loading} className="w-full">
            注册
          </Button>
        </form>

        <p className="mt-4 text-sm text-slate-400">
          已有账号?{' '}
          <Link to="/login" className="text-indigo-400 hover:underline">
            登录
          </Link>
        </p>
      </div>
    </div>
  )
}
