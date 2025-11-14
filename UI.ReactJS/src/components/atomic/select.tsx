import * as React from "react"
import { ChevronDown } from "lucide-react"
import { cn } from "@/components/lib/utils"

export interface SelectProps {
  value?: string
  onValueChange?: (value: string) => void
  placeholder?: string
  children: React.ReactNode
  disabled?: boolean
  className?: string
}

export interface SelectItemProps {
  value: string
  children: React.ReactNode
  onSelect?: () => void
}

const Select = React.forwardRef<HTMLDivElement, SelectProps>(
  ({ value, onValueChange, placeholder, children, disabled, className, ...props }, ref) => {
    const [isOpen, setIsOpen] = React.useState(false)
    const [selectedValue, setSelectedValue] = React.useState(value || "")

    const handleValueChange = (newValue: string) => {
      setSelectedValue(newValue)
      onValueChange?.(newValue)
      setIsOpen(false)
    }

    // Extract items from children
    const items = React.Children.toArray(children).filter(
      (child): child is React.ReactElement<SelectItemProps> =>
        React.isValidElement(child) && child.type === SelectItem
    )

    const selectedItem = items.find(item => item.props.value === selectedValue)
    const displayText = selectedItem ? selectedItem.props.children : placeholder

    React.useEffect(() => {
      if (value !== undefined) {
        setSelectedValue(value)
      }
    }, [value])

    return (
      <div className="relative" ref={ref} {...props}>
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className={cn(
            "flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            className
          )}
        >
          <span className={selectedValue ? "text-gray-900" : "text-gray-500"}>
            {displayText}
          </span>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </button>

        {isOpen && (
          <div className="absolute top-full left-0 right-0 z-50 mt-1 max-h-60 overflow-auto rounded-md border bg-white shadow-lg">
            {items.map((item) => (
              <button
                key={item.props.value}
                type="button"
                onClick={() => handleValueChange(item.props.value)}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
              >
                {item.props.children}
              </button>
            ))}
          </div>
        )}

        {/* Overlay to close dropdown when clicking outside */}
        {isOpen && (
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
        )}
      </div>
    )
  }
)
Select.displayName = "Select"

const SelectItem: React.FC<SelectItemProps> = ({ children }) => {
  return <>{children}</>
}

export { Select, SelectItem }
