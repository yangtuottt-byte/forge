import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TaskProgress } from '../TaskProgress'

describe('TaskProgress', () => {
  it('显示进度百分比', () => {
    render(<TaskProgress status="running" progress={40} />)
    expect(screen.getByText('40%')).toBeInTheDocument()
    expect(screen.getByText('执行中')).toBeInTheDocument()
  })

  it('done 状态显示已完成', () => {
    render(<TaskProgress status="done" progress={100} />)
    expect(screen.getByText('已完成')).toBeInTheDocument()
  })
})
