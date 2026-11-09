import { describe, it, expect } from 'vitest'
import { API_BASE, toWsBase } from '../apiBase'

describe('apiBase', () => {
  it('默认 API 基础指向后端 /api/v1', () => {
    expect(API_BASE).toBe('http://localhost:8000/api/v1')
  })

  it('toWsBase:http→ws,https→wss', () => {
    expect(toWsBase('http://localhost:8000/api/v1')).toBe('ws://localhost:8000/api/v1')
    expect(toWsBase('https://forge.example/ws')).toBe('wss://forge.example/ws')
  })
})
