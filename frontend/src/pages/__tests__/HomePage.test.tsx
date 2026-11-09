import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { HomePage } from '../HomePage'

describe('HomePage', () => {
  it('渲染平台标题', () => {
    render(<HomePage />)
    expect(
      screen.getByText(/Forge · 多智能体协作研发平台/),
    ).toBeInTheDocument()
  })
})
