import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

// 合并 className:clsx 处理条件拼接,tailwind-merge 处理冲突类去重
// (如 cn('px-4', isBig && 'px-6') → 'px-6')
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
