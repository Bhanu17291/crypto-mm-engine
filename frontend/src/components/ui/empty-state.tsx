import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

export function EmptyState({
  icon: Icon,
  title,
  description,
  className,
}: {
  icon: LucideIcon
  title: string
  description?: string
  className?: string
}) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-2 py-8 text-center', className)}>
      <div className="relative flex size-10 items-center justify-center rounded-full bg-brand/10">
        <span className="absolute inline-flex size-full animate-ping rounded-full bg-brand/20" />
        <Icon className="relative size-5 text-brand" strokeWidth={1.75} />
      </div>
      <div className="text-xs font-medium text-foreground/80">{title}</div>
      {description && (
        <div className="max-w-[240px] text-[11px] leading-relaxed text-muted-foreground">
          {description}
        </div>
      )}
    </div>
  )
}
