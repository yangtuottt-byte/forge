import { type ButtonHTMLAttributes } from 'react'
import { cn } from '../lib/cn'

type Variant = 'primary' | 'secondary' | 'ghost'

const VARIANT_STYLES: Record<Variant, string> = {
  primary: 'bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800/70',
  secondary: 'bg-slate-800 hover:bg-slate-700 disabled:bg-slate-800/70',
  ghost: 'bg-transparent hover:bg-slate-800 disabled:opacity-50',
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  loading?: boolean
}

export function Button({
  className,
  variant = 'primary',
  loading,
  children,
  disabled,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-slate-100 transition disabled:cursor-not-allowed',
        VARIANT_STYLES[variant],
        className,
      )}
      disabled={disabled || loading}
      {...rest}
    >
      {loading ? (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-transparent" />
      ) : null}
      {children}
    </button>
  )
}
