import { Slot, Slottable } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-[var(--radius-control)] border border-transparent text-sm font-medium tracking-[0.01em] transition-[color,background-color,border-color,box-shadow,transform] duration-200 ease-out disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow-[var(--shadow-elev-1)] hover:-translate-y-px hover:bg-primary/92 hover:shadow-[var(--shadow-elev-2)]",
        destructive:
          "bg-destructive text-white shadow-[var(--shadow-elev-1)] hover:-translate-y-px hover:bg-destructive/92 hover:shadow-[var(--shadow-elev-2)] focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
        outline:
          "border-border/80 bg-background/95 shadow-[var(--shadow-elev-1)] hover:-translate-y-px hover:bg-accent/80 hover:text-accent-foreground hover:shadow-[var(--shadow-elev-2)] dark:border-input dark:bg-[var(--surface-input)] dark:hover:bg-input/60",
        secondary:
          "bg-secondary text-secondary-foreground shadow-[var(--shadow-elev-1)] hover:-translate-y-px hover:bg-secondary/88 hover:shadow-[var(--shadow-elev-2)]",
        ghost:
          "shadow-none hover:bg-accent/70 hover:text-accent-foreground dark:hover:bg-accent/60",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-[var(--control-height)] px-4 py-2 has-[>svg]:px-3",
        sm: "h-[var(--control-height-sm)] gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-[var(--control-height-lg)] px-6 has-[>svg]:px-4",
        icon: "size-[var(--control-height)]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
  VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
}

function LoadingButton({
  className,
  loading = false,
  children,
  disabled,
  variant,
  size,
  asChild = false,
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : "button"
  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      disabled={loading || disabled}
      {...props}
    >
      {loading && <Loader2 className="mr-2 h-5 w-5 animate-spin" />}
      <Slottable>{children}</Slottable>
    </Comp>
  )
}

export { buttonVariants, LoadingButton }
