"use client"

import * as React from "react"
import { Check } from "lucide-react"

interface CheckboxProps {
  id?: string
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
  className?: string
  disabled?: boolean
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ id, checked = false, onCheckedChange, className = "", disabled = false }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onCheckedChange?.(e.target.checked)
    }

    return (
      <div className="relative">
        <input
          ref={ref}
          id={id}
          type="checkbox"
          checked={checked}
          onChange={handleChange}
          disabled={disabled}
          className="sr-only"
          aria-label="Checkbox"
        />
        <div
          className={`
            h-4 w-4 shrink-0 rounded-sm border border-gray-600 bg-transparent
            flex items-center justify-center cursor-pointer
            ${checked ? 'bg-blue-600 border-blue-600' : 'hover:border-gray-500'}
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            ${className}
          `}
          onClick={() => !disabled && onCheckedChange?.(!checked)}
        >
          {checked && <Check className="h-3 w-3 text-white" />}
        </div>
      </div>
    )
  }
)

Checkbox.displayName = "Checkbox"

export { Checkbox }
