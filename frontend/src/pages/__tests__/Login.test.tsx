import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../../auth/AuthProvider'
import { Login } from '../Login'

// 注意:空提交校验路径不触发网络请求(!email || !password → 直接报错),适合单测
describe('Login', () => {
  it('空提交时显示校验错误', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </MemoryRouter>,
    )

    // 未输入邮箱/密码直接提交 → 显示校验提示
    const submit = screen.getByRole('button', { name: '登录' })
    await user.click(submit)

    expect(await screen.findByText('请填写邮箱和密码')).toBeInTheDocument()
  })
})
