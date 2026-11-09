import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useTaskProgress } from '../useTaskProgress'

// 最小 WebSocket mock:捕获实例,允许手动触发 open/message/close
type Handlers = {
  open?: () => void
  message?: (ev: { data: string }) => void
  close?: () => void
}

class MockWS {
  static instances: MockWS[] = []
  url: string
  readyState = 0
  onopen: Handlers['open']
  onmessage: Handlers['message']
  onclose: Handlers['close']
  constructor(url: string) {
    this.url = url
    MockWS.instances.push(this)
  }
  close() {
    this.readyState = 3
    this.onclose?.()
  }
  // 测试辅助:手动触发
  triggerOpen() {
    this.readyState = 1
    this.onopen?.()
  }
  triggerMessage(data: string) {
    this.onmessage?.({ data })
  }
  triggerClose() {
    this.readyState = 3
    this.onclose?.()
  }
}

beforeEach(() => {
  MockWS.instances = []
  vi.stubGlobal('WebSocket', MockWS)
})

describe('useTaskProgress', () => {
  it('初始为 pending / 0,且建立了一条连接', () => {
    const { result } = renderHook(() => useTaskProgress(1))
    expect(result.current.status).toBe('pending')
    expect(result.current.progress).toBe(0)
    expect(MockWS.instances.length).toBe(1)
  })

  it('连接 URL 含任务 id 与 ws 路径', () => {
    renderHook(() => useTaskProgress(3))
    const ws = MockWS.instances[MockWS.instances.length - 1]
    expect(ws.url).toMatch(/\/tasks\/3\/ws/)
  })

  it('running → done 状态流转', () => {
    const { result } = renderHook(() => useTaskProgress(7))
    const ws = MockWS.instances[MockWS.instances.length - 1]

    act(() => ws.triggerMessage(JSON.stringify({ status: 'running', progress: 40 })))
    expect(result.current.status).toBe('running')
    expect(result.current.progress).toBe(40)

    act(() => ws.triggerMessage(JSON.stringify({ status: 'done', progress: 100 })))
    expect(result.current.status).toBe('done')
    expect(result.current.progress).toBe(100)
  })

  it('onFinished 在 done 时回调一次', () => {
    const onFinished = vi.fn()
    renderHook(() => useTaskProgress(7, { onFinished }))
    const ws = MockWS.instances[MockWS.instances.length - 1]

    act(() => ws.triggerMessage(JSON.stringify({ status: 'done', progress: 100 })))
    expect(onFinished).toHaveBeenCalledTimes(1)
  })

  it('完成后异常断线不再重连', () => {
    renderHook(() => useTaskProgress(7))
    const ws = MockWS.instances[MockWS.instances.length - 1]

    act(() => ws.triggerMessage(JSON.stringify({ status: 'done', progress: 100 })))
    act(() => ws.triggerClose())
    // 已完成 → 不应再新建连接
    expect(MockWS.instances.length).toBe(1)
  })
})
